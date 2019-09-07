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
4. Download your GMail IMAP chats folder ([Gmail]/Chats) using a desktop email client (script tested with Thunderbird).
5. Get the files that contain your chats. This script supports both the mbox format (one file, many "emails") and the Maildir format (one file per "email"):
  - If using mbox, you can simply copy the mbox file directly from your profile directory (it may be located at `[thunderbird_profile]/ImapMail/imap.gmail.com/[Gmail].sbd/Chats`). Or you can use Thunderbird's [ImportExportTools](https://addons.mozilla.org/en-us/thunderbird/addon/importexporttools/) addon to assist in obtaining the file required.
  - To use Maildir, you must enable the Maildir backend for Thunderbird. It's suggested to backup your emails first & enable maildir at the local level if you regularly use Thunderbird. Maildir can be enabled in the settings 3 different ways:
    - Options - Advanced - Advanced Configuration - Message Store Type for new accounts
    - Account Settings - Server Settings - Message Storage - Message Store Type
    - Account Settings - Local Folders - Message Storage - Message Store Type
6. Check out this repository to a directory.
7. Run this command: `python gtalk_export.py -p <path/to/mbox_file_or_maildir_directory> -j <path/to/json_file> -n <your name> -e <your email> ` **If using mbox, add `-m` to the end of the command**
 
The program needs your name and email so that it knows who "you" are, and by extension who the other party is -- some of the mbox-format chats just list participants with no indication of which one is the account being parsed.  Running the command will generate a large number of .txt files in the current working directory (one for each contact you conversed with).
