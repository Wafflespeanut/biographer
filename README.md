## Anecdote (v0.4.1)

This is a little project of mine - an utility to remember everyday memories. For now, it puts your stories (with a MD5-hashed filename) into a directory for later viewing. It supports some basic encryption. I've used a simple algorithm to hex and shift the ASCII values in the files, which is similar to a *hexed* 256-char Caesar cipher with a byte-wise XOR<sup>[1]</sup>. It can also detect incorrect passwords.

Once stored, it doesn't disturb the original story (unless you play around). It decrypts to a temporary file for viewing, which also gets deleted almost immediately. While updating stories, it just appends your story to the previous story.

There's a SHA-256 hashing function which hashes the password into a local file, so that instead of typing the password each time you write/view some story, you can save it by signing in, but it requires at least one sign-in per session. And, the cool part - you can search through your stories for specific words (between a range of dates).

<sup>[1]: **It's not at all secure!**. And, that's not my goal either (at least, not for now). This is just to prevent people from peeking into the stories using text editors. But, if someone's really involved, then he'll be able to crack it in a few days.</sup>

### Checklist

- fix the memory leak occurring while transferring the string pointer from Rust to Python
- switch from a shift cipher to a stream cipher. That's because we don't need integrity in this case, we just need confidentiality (in which stream cipher rocks!). *Of course, protecting the files is always on your side.*
- add option for changing the password
- spawn multiple threads while searching with Rust

### Changelog

<sup>The commits (before 0.4.0: Memento) are in the [`scripts`](https://github.com/Wafflespeanut/scripts) repository. I moved it here once the diary became somewhat appealing. In case you wanna check those out, I've provided the links for each version below.</sup>

v0.4.2: Biographer *(still checking out)*
- Added errors, warnings & success messages
- Rust library can now be used for searching. It's damn fast! **But, it leaks memory!** (for now)

v0.4.1: [Anecdote](https://github.com/Wafflespeanut/anecdote/tree/6f7a80aa0ad24c299550e84e8d3ec0cf08bcbbc9)
- Improved search to suit the methods written for both Python & Rust
- Replaced the exhaustive date & time with builtin datetime objects
- Hashed password & diary location is stored in a configuration file
- Functions: `search(), pySearch(), findStory(), grabStories(), random(), temp()`

v0.4.0: [Memoir](https://github.com/Wafflespeanut/Memoir/tree/efc7cd4b15b1840c6b8d0a7c494690834e987cbe)
- Fixed a major flaw in the cipher. All these days, this has been consuming more time & memory. It's now been updated to a mixup of 256-char Caesar cipher and byte-wise XOR.
- No longer depends on text editors. It just prints the stories on the screen.
- No longer stores passwords, but hashes them (with SHA-256) to allow authentication for a particular session (which means you have to sign-in at the start of every session). While local password storage appeals our minds, it was a *really* bad move!
- Functions: `hashed(), shift(), CXOR(), temp(), protect(), write(), random(), search()`

v0.3.0: [Remembrancer](https://github.com/Wafflespeanut/scripts/tree/be3b51c14c5e708baa4003adf3346f51f5720529/Remembrancer)
- Smart search for specific words in stories
- Old tree-node method is now deprecated. All stories are now present in the specified directory
- Story names are hashed with MD5 (to obscure the file names)
- Functions: `hashed(), hashDate(), write(), diary(), search()`

v0.2.2: [Memorandum](https://github.com/Wafflespeanut/scripts/tree/8850c831c10955b5c32d2710abfbfef916031792/Memorandum)
- Passwords can be stored locally (after 10-layer hexing)
- Write stories for someday you've missed
- Sign-in / Sign-out options for easier use
- Functions: `check(), diary(), day()`

v0.2.1: [Souvenir](https://github.com/Wafflespeanut/scripts/tree/937d48dc3bc8608530253fc392594a90a4d59078/Memento)
- View random stories
- TEMP is deleted after a timeout (to keep things safe)
- One-time password for updating stories
- Fixed a faulty code in encryption
- Can detect incorrect passwords
- Functions: `random(), temp(), protect()`

v0.2.0: [Memento](https://github.com/Wafflespeanut/scripts/tree/7f2572857bbe86b2598d27ab7872017a580351ff/Memento) *(has some bugs)*
- Added a simple encryption method which hexes and shifts the ASCII values (to make it really "private" - further protection is of your own)
- Added a function for viewing stories on a given day
- A TEMP file is created for viewing/updating any story, leaving the original files undisturbed
- Functions: `hexed(), char(), zombify(), shift(), protect(), write()`

v0.1.0: [Private Diary](https://github.com/Wafflespeanut/scripts/tree/64a9c8dd2470ec309a439a41568778187bbe8bb7/Private%20Diary)
- Creates timestamped folders and text files for stories
- Writes the stories for every [RETURN] stroke, which indicates a paragraph
- Functions: `new(), diary()`
