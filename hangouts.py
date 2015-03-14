import re
import json
import time

# This code was inspired by Jay2K1's Hangouts parser.  You can see the 
# blogpost for the original at:
# http://blog.jay2k1.com/2014/11/10/how-to-export-and-backup-your-google-hangouts-chat-history/
# He also runs a webservice for parsing Google Hangouts JSON files at:
# http://hangoutparser.jay2k1.com/

def replaceSmileys(string):
    # replaces UTF-8 graphical emoticons by their ASCII equivalents
    # list of emoji codes taken from https://aprescott.com/posts/hangouts-emoji
    patterns = [
        u'\U0001F41D',         # -<@% ?       honeybee
        u'\U0001F435',         # :(|) ?       monkey face
        u'\U0001F437',         # :(:) ?       pig face
        u'\U0001F473',         # (]:{ ?       man with turban
        u'\U0001F494',         # <\3 </3      ?       broken heart
        u'\U0001F49C',         # <3   ?       purple heart
        u'\U0001F4A9',         # ~@~  ?       pile of poo
        u'\U0001F600',         # :D :-D       ?       grinning face
        u'\U0001F601',         # ^_^  ?       grinning face with smiling eyes
        u'\U0001F602',         # XD
        u'\U0001F603',         # :) :-) =)    ?       smiling face with open mouth
        u'\U0001F604',         # =D   ?       smiling face with open mouth and smiling eyes
        u'\U0001F605',         # ^_^;;        ?       smiling face with open mouth and cold sweat
        u'\U0001F607',         # O:) O:-) O=) ?       smiling face with halo
        u'\U0001F608',         # }:) }:-) }=) ?       smiling face with horns
        u'\U0001F609',         # ;) ;-)       ?       winking face
        u'\U0001F60E',         # B) B-)       ?       smiling face with sunglasses
        u'\U0001F610',         # :-| :| =|    ?       neutral face
        u'\U0001F611',         # -_-  ?       expressionless face
        u'\U0001F613',         # o_o; ?       face with cold sweat
        u'\U0001F614',         # u_u  ?       pensive face
        u'\U0001F615',         # :\ :/ :-\ :-/ =\ =/  ?       confused face
        u'\U0001F616',         # :S :-S :s :-s        ?       confounded face
        u'\U0001F617',         # :* :-*       ?       kissing face
        u'\U0001F618',         # ;* ;-*       ?       face throwing a kiss
        u'\U0001F61B',         # :P :-P =P :p :-p =p  ?       face with stuck-out tongue
        u'\U0001F61C',         # ;P ;-P ;p ;-p        ?       face with stuck-out tongue and winking eye
        u'\U0001F61E',         # :( :-( =(    ?       disappointed face
        u'\U0001F621',         # >.< >:( >:-( >=(     ?       pouting face
        u'\U0001F622',         # T_T :'( ;_; ='(      ?       crying face
        u'\U0001F623',         # >_<  ?       persevering face
        u'\U0001F626',         # D:   ?       frowning face with open mouth
        u'\U0001F62E',         # o.o :o :-o =o        ?       face with open mouth
        u'\U0001F632',         # O.O :O :-O =O        ?       astonished face
        u'\U0001F634',         # O.O :O :-O =O        ?       astonished face
        u'\U0001F635',         # x_x X-O X-o X( X-(   ?       dizzy face
        u'\U0001F638',         # :X) :3 (=^..^=) (=^.^=) =^_^=        ?       grinning cat face with smiling eyes
        u'\U0001F64C'          # Dunno, but it needs to be replaced for ASCII
    ]
    replacements = [
        '-<@%',
        ':(|)',
        ':(:)',
        '(]:{',
        '</3',
        '<3',
        '~@~',
        ':D',
        '^_^',
        'XD',
        ':)',
        '=D',
        '^_^;;',
        'O:)',
        '}:)',
        ';)',
        'B-)',
        ':|',
        '-_-',
        'o_o;',
        'u_u',
        ':/',
        ':S',
        ':*',
        ';*',
        ':P',
        ';P',
        ':(',
        '>.<',
        ":'(",
        '>_<',
        'D:',
        ':o',
        ':O',
        '-_-Zzz',
        'x_x',
        ':3',
        '_'
    ]

    for index in range(len(patterns)):
        string = re.sub(patterns[index], replacements[index], string)
    return string

def hangoutsToArray(json_input, timestamp_format):
    # set the desired timestamp format here
    # the default is '%Y-%m-%d %H:%M:%S' which is YYYY-MM-DD HH:mm:ss.
    #timestamp_format = '%Y-%m-%d %H:%M:%S'

    # decode JSON
    decoded = json.loads(json_input)
    # extract useful part
    rawconvos = decoded['conversation_state']
    #print "%r" % rawconvos
    retval = []
    # loop through conversations
    for i in range(len(rawconvos)):
        #print "i is %d" % i
        #print "attempting in_conv: %s" % rawconvos[i]['conversation_state']['conversation']
        # first, get metadata
        retval.append({})
        convo = rawconvos[i]
        #print "%r" % convo
        in_conv = rawconvos[i]['conversation_state']['conversation']
        in_event = rawconvos[i]['conversation_state']['event']
        pdata = in_conv['participant_data']
        retval[i]['type'] = in_conv['type']
        retval[i]['msgcount'] = len(in_event)
        retval[i]['name'] = in_conv['name'] if 'name' in in_conv.keys() else ""
        # conversation participants
        for j in range(len(pdata)):
            id = pdata[j]['id']['chat_id']
            # use "unknown_<chat_id>" as name if they don't have a fallback_name
            name = pdata[j]['fallback_name'] if 'fallback_name' in pdata[j].keys() else "unknown_%s" % id
            if not 'members' in retval[i].keys():
                retval[i]['members'] = {}
            retval[i]['members'][id] = name

        # loop through messages/events
        messages = []
        for k in range(len(in_event)):
            messages.append({})
            messages[k]['timestamp'] = in_event[k]['timestamp']
            messages[k]['datetime'] = time.strftime(timestamp_format,time.localtime(int(messages[k]['timestamp'][0:10])))
            messages[k]['sender_id'] = in_event[k]['sender_id']['chat_id']
            messages[k]['sender'] = retval[i]['members'][messages[k]['sender_id']] if messages[k]['sender_id'] in retval[i]['members'].keys() else "unknown_%s" % id
            messages[k]['event_type'] = in_event[k]['event_type']

            if messages[k]['event_type'] == 'RENAME_CONVERSATION':
                newname = in_event[k]['conversation_rename']['new_name']
                oldname = in_event[k]['conversation_rename']['old_name']
                messages[k]['message'] = "changed conversation name %s%s" % \
                                         (("from '%s'" % oldname) if oldname else "", 
                                          ("to '%s'" % newname) if newname else "")
            elif messages[k]['event_type'] == 'HANGOUT_EVENT':
                if in_event[k]['hangout_event']['event_type'] == 'START_HANGOUT':
                    messages[k]['message'] = 'started a video chat'
                elif in_event[k]['hangout_event']['event_type'] == 'END_HANGOUT':
                    messages[k]['message'] = 'ended a video chat'
                else:
                    messages[k]['message'] = in_event[k]['hangout_event']['event_type']
            elif messages[k]['event_type'] == 'REGULAR_CHAT_MESSAGE':
                messages[k]['message'] = ""
                msg = ""
                msghtml = ""
                # join message segments together
                if 'segment' in in_event[k]['chat_message']['message_content'].keys():
                    for event in in_event[k]['chat_message']['message_content']['segment']:
                        if not 'text' in event.keys():
                            continue
                        if event['type'] == 'TEXT':
                            msg += event['text']
                            msghtml += re.sub("\n", "<br>", event['text'])
                        elif event['type'] == 'LINK':
                            msg += event['text']
                            msghtml += '<a href="%s" target="_blank">%s</a>' % (event['link_data']['link_target'], event['text'])
                        elif event['type'] == 'LINE_BREAK':
                            msg += event['text']
                            msghtml += re.sub("\n", "<br>", event['text'])
                # handle attachments
                elif 'attachment' in in_event[k]['chat_message']['message_content'].keys():
                    # loop through attachments
                    for att in in_event[k]['chat_message']['message_content']['attachment']:
                        # echo "<pre>";print_r($att);echo "</pre>";
                        if att['embed_item']['type'][0] == 'PLUS_PHOTO':
                            imgurl = att['embed_item']['embeds.PlusPhoto.plus_photo']['url']
                            msg += imgurl
                            msghtml += '<a href="%s" target="_blank"><img src="%s" alt="attached image" style="max-width:%s"></a>' % (imgurl, imgurl, "100%")
                # replace unicode emoticon characters by smileys
                messages[k]['message'] = replaceSmileys(msg)
                if msg != msghtml:
                    messages[k]['message_html'] = replaceSmileys(msghtml)
            elif messages[k]['event_type'] == 'ADD_USER':
                newuserid = in_event[k]['membership_change']['participant_id'][0]['chat_id']
                newusername = retval[i]['members'][newuserid] or 'unknown_%s' % newuserid
                messages[k]['message'] = "added user '%s' to conversation" % newusername
            elif messages[k]['event_type'] == 'REMOVE_USER':
                newuserid = in_event[k]['membership_change']['participant_id'][0]['chat_id']
                newusername = retval[i]['members'][newuserid] or 'unknown_%s' % newuserid
                messages[k]['message'] = "removed user '%s' from conversation" % newusername
            elif messages[k]['event_type'] == 'SMS':
                messages[k]['message'] = ""
                # join message segments together
                if 'segment' in in_event[k]['chat_message']['message_content'].keys():
                    for l in range(len(in_event[k]['chat_message']['message_content']['segment'])):
                        if not 'text' in in_event[k]['chat_message']['message_content']['segment'][l].keys():
                            continue
                        messages[k]['message'] += in_event[k]['chat_message']['message_content']['segment'][l]['text']
                # replace unicode emoticon characters by smileys
                messages[k]['message'] = replaceSmileys(messages[k]['message'])
            elif messages[k]['event_type'] == 'OTR_MODIFICATION':
                messages[k]['message'] = 'unknown OTR_MODIFICATION'
            elif messages[k]['event_type'] == 'VOICEMAIL':
                messages[k]['message'] = "new voicemail:\n"
                # join message segments together
                if 'segment' in in_event[k]['chat_message']['message_content'].keys():
                    for l in range(len(in_event[k]['chat_message']['message_content']['segment'])):
                        if not 'text' in in_event[k]['chat_message']['message_content']['segment'][l].keys():
                            continue
                        messages[k]['message'] += in_event[k]['chat_message']['message_content']['segment'][l]['text']
                # replace unicode emoticon characters by smileys
                messages[k]['message'] = replaceSmileys(messages[k]['message'])
        # sort messages by timestamp because for some reason they're cluttered
        messages.sort(cmp=lambda a,b: int(a['timestamp']) - int(b['timestamp']))
        # add the messages array to the conversation array
        retval[i]['messages'] = messages
    return retval
