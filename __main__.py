import inspect, os, sys
from src import session as sess
from src import options
from src.story import Story

filename = inspect.getframeinfo(inspect.currentframe()).filename    # this sweetsauce should work for all cases
path = os.path.dirname(os.path.abspath(filename))

load_list = ["core.py", "cipher.py", "search.py"]
map(execfile, map(lambda string: os.path.join(path, "src", string), load_list))
_name, args = sys.argv[0], map(lambda string: string.strip('-'), sys.argv[1:])

# data_tuple = (file_contents, key) returned by protect()
# file_data = list(word_counts) for each file sorted by date, returned by the searching functions

def chain_args(args):
    try:
        option, value = args[0].split('=')
    except ValueError:
        option = args[0]
    # CHECKLIST
    return None

if __name__ == '__main__':  # there are a hell lot of `try...except`s for smoother experience
    session = sess.Session()
    if session.loop:
        sess.clear_screen()

    try:
        if args and session.loop:
            option = chain_args(args)
            if option:
                exec(option)        # `exec` is a nice hack to achieve wonderful things in Python
                exit('\n')
            print sess.error, 'Invalid arguments! Continuing with default...'
    except (KeyboardInterrupt, EOFError):
        sleep(sess.capture_wait)
        exit('\n')

    while session.loop:     # Main loop
        try:
            print '\n\t(Press Ctrl-C to get back to the main menu any time!)'
            if 'linux' not in sys.platform:
                print '\n\t### This program runs best on Linux terminal ###'
            print '\n\tWhat do you wanna do?\n'
            choices = {     # how the option will be displayed, and its corresponding executable line
                1: ("Write today's story", 'Story(session, "today").write()'),
                2: ("Random story", 'options.random(session)'),
                3: ("View the story of someday", 'Story(session).view()'),
                4: ("Write (or append to) the story of someday", 'Story(session, is_write = True).write()'),
                5: ("Search your stories", 'search(session)'),
                6: ("Backup your stories", 'options.backup(session)'),
                7: ("Change your password", 'options.change_pass(session)'),
                8: ("Reconfigure your diary", 'session.reconfigure()'),
                # hidden choice (in case the script somehow quits before encrypting a story)
                9: ("Encrypt a story", 'Story(session).encrypt()'),
                0: ("Exit the biographer", ''),
            }

            for i in range(1, len(choices) - 1) + [0]:
                print '\t\t%d. %s' % (i, choices[i][0])

            try:
                ch = int(raw_input('\nChoice: '))
                if ch == 0:
                    session.loop = False
                    break
                exec(choices[ch][1])
                assert session.loop
                session.loop = True if raw_input('\nDo something again (y/n)? ') == 'y' else False
            # This only checks whether the `loop` value is modified - all other AssertionErrors are handled elsewhere
            except AssertionError:
                break
            except (ValueError, KeyError):      # invalid input
                print sess.error, "Please enter a valid input! (between 0 and %s)" % (len(choices) - 1)
                sleep(2)
            except (KeyboardInterrupt, EOFError):   # interrupted input
                sleep(sess.capture_wait)
        except Exception as err:       # An uncaught exception (which has probably creeped all the way up here)
            try:
                print sess.error, err, '\nAh, something bad has happened! Maybe try reconfiguring your diary?'
                sleep(2)
            except (KeyboardInterrupt, EOFError):   # just to not quit while displaying
                sleep(sess.capture_wait)
        except (KeyboardInterrupt, EOFError):
            # EOFError was added just to make this script work on Windows (honestly, Windows sucks!)
            sleep(sess.capture_wait)
        if session.loop:
            sess.clear_screen()
    if not session.loop:
        print '\nGoodbye...\n'
