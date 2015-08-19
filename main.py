import os, sys

execFolder = sys.argv[0]            # check whether path is given as an argument
if 'biographer' not in execFolder:
    execFolder = [path for path in sys.path if 'biographer' in path][0]
listPath = execFolder.split(os.sep)         # else, search for the path in the list of paths
i = listPath.index('biographer') + 1
path = str(os.sep).join(listPath[:i]) + os.sep      # all these stunts are for making this to work in QPython (Android)

ploc = os.path.expanduser('~') + os.sep + '.diary'      # config location (absolute)

try:
    execfile(path + "src/core.py")
    execfile(path + "src/cipher.py")
    execfile(path + "src/options.py")
    execfile(path + "src/search.py")
except IOError:
    print "\n[ERROR] Hmm, looks like you've executed the diary in some bad way!"
    print '\nEither `cd` into the folder and execute it, or call it using `python /path/to/Diary.py`\n'
    sys.exit(0)

# [Conventions used here]
# fileTuple = (file_path, formatted_datetime) returned by hashDate()
# dataTuple = (file_contents, key) returned by protect()
# fileData = list(word_counts) for each file sorted by date, returned by the searching functions

wait = (0.1 if sys.platform == 'win32' else 0)
# these 100ms sleep times at every KeyboardInterrupt is the workaround for catching EOFError properly in Windows

if __name__ == '__main__':
    loc, key, birthday, choice = configure()
    # 'birthday' of the diary is important because random stories and searching is based on that
    while choice == 'y':
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
            if 'linux' not in sys.platform:
                print '\n### This program runs best on Linux terminal ###'
            choices = ("\n\tWhat do you wanna do?\n",
                        " 1: Write today's story",
                        " 2: Random story",
                        " 3: View the story of someday",
                        " 4. Write the story for someday you've missed",
                        " 5. Search your stories",
                        " 6. Backup your stories",
                        " 7. Change your password",
                        " 8. Reconfigure your diary",
                        " 9. Exit the biographer",)
            print '\n\t\t'.join(choices)
            options =   ("key = write(key)",     # just to remember the password throughout the session
                        "key = random(key, birthday)",
                        "key = temp(hashDate(), key)",
                        "key = write(key, hashDate())",
                        "key = search(key, birthday)",
                        "backupStories(loc)",
                        "loc, key = changePass(key)",
                        "loc, key, birthday, choice = configure(True)",
                        "print; sys.exit('Goodbye...')",)
            try:
                ch = int(raw_input('\nChoice: '))
                if ch in range(1, len(choices)):
                    exec(options[int(ch)-1])
                else:
                    print error, 'Please enter a value between 1 and %d!' % (len(choices) - 1)
                    sleep(2)
                    continue
            except (KeyboardInterrupt, EOFError, ValueError):
                sleep(wait)
                print error, "C'mon, quit playing around!"
                sleep(2)
                continue
            choice = raw_input('\nDo something again (y/n)? ')
        except Exception as err:
            print error, 'Ah, something bad has happened! Maybe reconfigure your diary?'
            sleep(2)
            continue
        except (KeyboardInterrupt, EOFError):
            # EOFError was added just to make this script work on Windows (honestly, Windows sucks!)
            choice = raw_input('\n' + warning + ' Interrupted! Do something again (y/n)? ')
    if choice is not 'y':
        print '\nGoodbye...'