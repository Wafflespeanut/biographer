import os, sys
from datetime import datetime, timedelta
from time import sleep
from timeit import default_timer as timer

from story import Story
from utils import ERROR, SUCCESS, WARNING, CAPTURE_WAIT
from utils import DateIterator, clear_screen, ffi_channel, fmt, fmt_text, force_input, get_lang


def build_paths(session, date_start, date_end):
    path_list = []

    for _i, day in DateIterator(date_start, date_end, 'Building the path list... %s'):
        file_path = Story(session, day).get_path()
        if file_path:
            path_list.append(file_path)

    assert path_list
    path_list.append(session.key)
    return path_list


def rusty_search(session, date_start, date_end, word):      # FFI for giving the searching job to Rust
    occurrences = []
    list_to_send = build_paths(session, date_start, date_end)
    list_to_send.append(word)
    count_string, timing = ffi_channel(list_to_send, mode = 1)
    print 'Parsing the data stream from Rust...'

    for i, string in enumerate(count_string.split(' ')):    # spaces in the data stream represent individual files
        idx = map(int, string.split(':'))       # ... and colons represent the indices where the word has occurred
        # Rust fills the indices of the file paths with the number of occurrences
        # So, "i" indicates the Nth day from the birthday
        if idx[0] > 0:
            occurrences.append((i, len(idx), idx))
    return occurrences, timing


# NOTE: Exhaustive process (that's why I've written a Rust library for this!)
# The library accelerates the searching time by ~100 times!
def py_search(session, date_start, date_end, word):
    occurrences, errors, no_stories, = [], 0, 0
    start = timer()
    date_iter = DateIterator(date_start, date_end)

    for i, day in date_iter:
        occurred, story = [], Story(session, day)

        try:
            if not story.get_path():
                no_stories += 1
                continue
            data = story.decrypt()      # AssertionError (if any) is caught here
            idx, jump, data_len = 0, len(word), len(data)

            # probably an inefficient way to find the word indices
            while idx < data_len:
                idx = data.find(word, idx)
                if idx == -1: break
                occurred.append(idx)
                idx += jump
        except AssertionError:
            errors += 1
            if errors > 10:
                print ERROR, "More than 10 files couldn't be decrypted! Terminating the search..."
                return [], (timer() - start)

        if occurred and occurred[0] > 0:    # "i" indicates the Nth day from the birthday
            occurrences.append((i, len(occurred), occurred))
        sum_value = sum(map(lambda stuff: stuff[1], occurrences))
        date_iter.send_msg('[Found: %d]' % sum_value)

    assert no_stories < (i + 1)
    return occurrences, (timer() - start)


def find_line_boundary(text, idx, limit, direction_value):  # find the closest boundary of text for a given limit
    i, num = idx, 0

    while text[i + direction_value] not in ('\n', '\t'):
        if text[i] == ' ': num += 1
        if num == limit: return i
        i += direction_value
    return i


def mark_text(text, indices, length, color = 'red'):    # Mark text and return corrected indices
    if sys.platform == 'win32':         # damn OS doesn't even support coloring
        return text, indices

    text = list(text)
    formatter = fmt(color), fmt()
    lengths = map(len, formatter)       # we gotta update the indices when we introduce colored text
    i, limit = 0, len(indices)
    new_indices = indices[:]

    while i < limit:
        idx = indices[i]
        text[idx] = formatter[0] + text[idx]
        text[idx + length - 1] += formatter[1]
        new_indices[i] -= lengths[0]
        j = i

        while j < limit:
            new_indices[j] += sum(lengths)
            j += 1
        i += 1

    return ''.join(text), new_indices


def search(session, word = None, lang = None, start = None, end = None, grep = 7):
    '''Invokes one of the searching functions and does some useful stuff'''
    clear_screen()
    now = datetime.now()

    def check_date(date):
        if date in ['today', 'now', 'end']:
            return now
        elif date in ['start', 'birthday']:
            return session.birthday
        try:
            return datetime.strptime(date, '%Y-%m-%d')
        except (TypeError, ValueError):
            return None

    sys.stdout.set_mode(1, 0.01)
    # Phase 1: Get the user input required for searching through the stories
    word = force_input(word, "\nEnter a word: ", ERROR + ' You must enter a word to continue!')
    lang = get_lang(lang)
    start, end = map(check_date, [start, end])

    while not all([start, end]):
        try:
            print WARNING, 'Enter dates in the form YYYY-MM-DD (Mind you, with hyphen!)\n'
            if not start:
                lower_bound = session.birthday
                start_date = raw_input('Start date (Press [Enter] to begin from the start of your diary): ')
                start = datetime.strptime(start_date, '%Y-%m-%d') if start_date else session.birthday
                assert (start >= lower_bound and start <= now), 'S'
            if not end:
                lower_bound = start
                end_date = raw_input("End date (Press [Enter] for today's date): ")
                end = datetime.strptime(end_date, '%Y-%m-%d') if end_date else now
                assert (end > lower_bound and end <= now), 'E'

        except AssertionError as msg:
            print ERROR, '%s date should be after %s and before %s' % \
                         (msg, lower_bound.strftime('%b. %d, %Y'), now.strftime('%b. %d, %Y'))
            if str(msg) == 'S':
                start = None
            else:
                end = None
        except ValueError:
            print ERROR, 'Oops! Error in input. Try again...'

    # Phase 2: Send the datetimes to the respective searching functions
    print "\nSearching your stories for the word '%s'..." % word
    search_function = rusty_search if lang == 'r' else py_search

    try:
        occurrences, timing = search_function(session, start, end, word)
    except AssertionError:
        print ERROR, 'There are no stories in the given location!'
        return

    def print_stuff(grep):      # function to choose between pretty and ugly printing
        sys.stdout.set_mode(0)
        results_begin = '\nSearch results from %s to %s:' % (start.strftime('%B %d, %Y'), end.strftime('%B %d, %Y')) + \
                        "\n\nStories on these days have the word '%s' in them...\n" % word

        if grep:    # pretty printing the output (at the cost of decrypting time)
            try:
                timer_start = timer()
                print results_begin

                for i, (n, word_count, indices) in enumerate(occurrences):
                    colored = []
                    date = start + timedelta(n)
                    content = Story(session, date).decrypt()
                    numbers = str(i + 1) + '. ' + date.strftime('%B %d, %Y (%A)')
                    text, indices = mark_text(content, indices, jump)   # precisely indicate the word in text

                    for idx in indices:     # find the word occurrences
                        left_bound = find_line_boundary(text, idx, grep, -1)
                        right_bound = find_line_boundary(text, idx, grep, 1)
                        sliced = '\t' + '... ' + text[left_bound:right_bound].strip() + ' ...'
                        colored.append(sliced)

                    print numbers, '\n%s' % '\n'.join(colored)  # print the numbers along with the word occurrences

                timer_stop = timer()

            except (KeyboardInterrupt, EOFError):
                sleep(CAPTURE_WAIT)
                grep = 0    # default back to ugly printing
                clear_screen()
                print "Yep, it takes time! Let's go back to the good ol' days..."

        if not grep:    # Yuck, but cleaner way to print the results
            sys.stdout.set_mode(0)
            print results_begin

            for i, (n, word_count, _indices) in enumerate(occurrences):
                date = session.birthday + timedelta(n)
                numbers = ' ' + str(i + 1) + '. ' + date.strftime('%B %d, %Y (%A)')
                spaces = 40 - len(numbers)
                print numbers, ' ' * spaces, '[ %s ]' % word_count  # print only the datetime and counts in each file

        sys.stdout.set_mode(1, 0.015)
        msg = fmt_text('Found a total of %d occurrences in %d stories!' % (total_count, num_stories), 'yellow')
        print '\n%s %s\n' % (SUCCESS, msg)
        print fmt_text('  Time taken for searching: ', 'blue') + \
              fmt_text('%s seconds!' % timing, 'green')

        if grep:
            print fmt_text('  Time taken for pretty printing: ', 'blue') + \
                  fmt_text('%s seconds!' % (timer_stop - timer_start), 'green')

    # Phase 3: Print the results (in a pretty or ugly way) using the giant function below
    jump, num_stories = len(word), len(occurrences)
    total_count = sum(map(lambda stuff: stuff[1], occurrences))
    print SUCCESS, 'Done! Time taken: %s seconds! (%d occurrences in %d stories!)' \
                   % (timing, total_count, num_stories)

    if not total_count:
        print ERROR, "Bummer! There are no stories containing '%s'..." % word
        return

    print_stuff(grep)

    # Phase 4: Get the user input and display the stories
    while occurrences:
        try:
            sys.stdout.set_mode(2)
            print '\nEnter a number to see the corresponding story...'
            print "\r(Enter 'pretty' or 'ugly' to print those search results again, or press [Enter] to exit)"
            ch = raw_input('\nInput: ')

            if ch == 'pretty':
                clear_screen()
                print_stuff(grep = 7)       # '7' is default, because it looks kinda nice
            elif ch == 'ugly':
                clear_screen()
                print_stuff(grep = 0)
            elif not ch:
                return
            elif int(ch) <= 0:
                raise ValueError
            else:
                n_day, word_count, indices = occurrences[int(ch) - 1]
                date = start + timedelta(n_day)
                (data, top, bottom) = Story(session, date).view(return_text = True)
                sys.stdout.set_mode(3)
                print top, mark_text(data, indices, jump, 'skyblue')[0], bottom
        except (ValueError, IndexError):
            print ERROR, 'Oops! Bad input! Try again...'
