gtalk_export
============

* Author: Clint Olson (with JSON-parsing code from [Jay2K1](http://blog.jay2k1.com/))
* License: MIT
* Meaning: Use everywhere, keep copyright, it'd be swell if you'd link back here.
 
## Usage
_Export Google Talk/Hangouts chats to logfiles_

Uses a modified version of [Jay2K1's Takeouts parser](http://hangoutparser.jay2k1.com/) (for Hangouts chats) alongside a custom mbox parser (for older Google Talk chats made before mid-2013) to produce a single set of unified logfiles.

To use it, follow these steps:

1. Export your Google Hangouts data using [Google Takeout](https://www.google.com/settings/takeout).  You'll be using the "Hangouts.json" file from the archive this gives you.
2. [Enable IMAP](https://support.google.com/mail/troubleshooter/1668960?hl=en#ts=1665018) on your GMail account.
3. Check the box to make Chats show up in IMAP, as detailed [here](http://readwrite.com/2011/09/16/google_liberates_gmail_chat_logs_via_imap)
4. Download your GMail IMAP chats folder ([Gmail]/Chats) using a desktop email client.  I used Thunderbird.  You'll be using the mbox-format mail-folder file (I recommend Thunderbird's [ImportExportTools](https://addons.mozilla.org/en-us/thunderbird/addon/importexporttools/) addon to assist in obtaining the file required).
5. Check out this repository to a directory.
6. Run this command: `python gtalk_export.py -m <path_to_mbox_file> -j <path_to_json_file> -n <your name> -e <your email>`
 
The program needs your name and email so that it knows who "you" are, and by extension who the other party is -- some of the mbox-format chats just list participants with no indication of which one is the account being parsed.  Running the command will generate a large number of .txt files in the current working directory (one for each contact you conversed with).
