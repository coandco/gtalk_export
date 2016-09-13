import os
import mailbox
import re
import time
import sys
import xml.dom.minidom
import HTMLParser
import argparse
import hangouts
from email.utils import parsedate

def extract_date_mbox(email):
    date = email.get('Date')
    return parsedate(date)

def filename_sanitize(input):
    return re.sub("([^a-zA-Z0-9._-])", "_", input)

def make_filename_json(member_array, name, email):
    outstr = ''
    for i in member_array:
        if member_array[i] not in (name, email):
            if outstr != '':
                outstr += "_"
            outstr += member_array[i];
    #Need to limit total filename size to 255
    return outstr[:250] + ".txt"

def msg_to_logline_json(message):
    return "%s <%s> %s\n" % (message['datetime'],  message['sender'], message['message'])

def write_to_file(filename, lines):
    '''Write a set of lines to a specified file.

    @param filename: path to file
    @type filename: string
    @param lines: array of log lines (strings) to write
    @type lines: [string, string, ...]
    
    '''
    with open(filename, "a") as myfile:
            myfile.write("".join(lines))

def parse_mailbox(mailbox_path, my_name, my_email, timestamp_format, use_mbox):
    mailbox_path = os.path.join(mailbox_path,"")
    if not os.path.isdir(mailbox_path + 'new'):
        os.mkdir(mailbox_path + 'new')
    if not os.path.isdir(mailbox_path + 'tmp'):
        os.mkdir(mailbox_path + 'tmp')

    if use_mbox:
        mbox = mailbox.mbox(mailbox_path)        
    else:
        mbox = mailbox.Maildir(mailbox_path, None)
    sorted_mails = sorted(mbox, key=extract_date_mbox)

    for message in sorted_mails:
        messageobj = []
        name = re.sub("Chat with ", "", message['subject'])

        payload = message.get_payload()
        if type(payload) is str:
            # We're in one of the new hybrid-style single-use messages
            to_name = re.sub(" <[^>]*>", "", message.get('To'))
            from_name = re.sub(" <[^>]*>", "", message.get('From'))
            if not name:
                name = to_name if to_name != my_name else from_name
            rawtimestr = message.get('Date')
            timestamp = time.strftime(timestamp_format, parsedate(rawtimestr))
            
            pars = HTMLParser.HTMLParser()
            outline = "%s <%s> %s\n" % (timestamp, from_name, pars.unescape(payload))
            messageobj.append(outline)
        else:
            #We're in an old Google Talk Jabber conversation message
            payload = payload[0].as_string()
            # The emails have forced line breaks that end in an equals sign
            payload = re.sub("=\r?\n", "", payload)
            # The emails replace all regular equals signs with =3D
            payload = re.sub("=3D", "=", payload)
            # The emails have a couple of chaff lines before the XML starts
            payload = re.sub(r'^[^<]*<', "<", payload)

            chatxml = xml.dom.minidom.parseString(payload)
            
            for messagexml in chatxml.getElementsByTagName("cli:message"):
                speaker = messagexml.getAttribute("from")
                rawtimestr = messagexml.getElementsByTagName("time")[0].getAttribute("ms")
                timefloat = float(rawtimestr[:-3] + "." + rawtimestr[-3:])
                timestamp = time.strftime(timestamp_format,time.localtime(timefloat))
                try:
                    content = messagexml.getElementsByTagName("cli:body")[0].firstChild.data
                except AttributeError:
                    # No 'data' element means that it's an empty message
                    content = ""
                except IndexError:
                    # No "cli:body" elements means that it's a non-message event,
                    # like a time-gap or user-unavailable message
                    continue
                outline = "%s <%s> %s\n" % (timestamp, speaker, content)
                messageobj.append(outline)

        write_to_file("%s.txt" % filename_sanitize(name)[:250], messageobj)

def parse_json(json_path, name, email, timestamp_format):
    with open(json_path, "r") as myfile:
        mydata=myfile.read()

    conversations = hangouts.hangoutsToArray(mydata, timestamp_format)

    print("JSON file first pass completed.  Writing to logfiles...")

    for conversation in conversations:
        filename = filename_sanitize(make_filename_json(conversation['members'],
                                                        name, email))
        messageobj = []
        for message in conversation['messages']:
            messageobj.append(msg_to_logline_json(message).encode("ascii", 
                                                                  "replace"))
        write_to_file(filename, messageobj)

parser = argparse.ArgumentParser(prog="gtalk_export")
parser.add_argument("-p", "--mailbox-path",
                    required=False,
                    default=None,
                    help="The location of the IMAP Maildir or mbox to parse")
parser.add_argument("-j", "--json-path",
                    required=False,
                    default=None,
                    help="The location of the Takeouts JSON to parse")
parser.add_argument("-n", "--name",
                    required=True,
                    help="The chat participant name whose files are being parsed")
parser.add_argument("-e", "--email",
                    required=True,
                    help="The chat participant email whose files are being parsed")
parser.add_argument("-t", "--timestamp-format",
                    required=False,
                    default='%Y-%m-%d %H:%M:%S',
                    help="The location of the IMAP mbox to parse")
parser.add_argument("-m", "--mbox",
                    required=False,
                    default=False,
                    help="Use mbox instead of Maildir")                    
                    

args = parser.parse_args()

if args.mailbox_path is None and args.json_path is None:
    sys.exit("No mbox or JSON provided -- nothing to do!")

if args.mailbox_path:
    print("Processing mailbox at %s" % args.mailbox_path)
    parse_mailbox(args.mailbox_path, args.name, args.email, args.timestamp_format, args.mbox)
    print("Finished processing mailbox")

if args.json_path:
    print("Processing json file at %s" % args.json_path)
    parse_json(args.json_path, args.name, args.email, args.timestamp_format)
    print("Finished processing json file")

print("GTalk/Hangouts export completed!")




