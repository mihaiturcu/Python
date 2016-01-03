import mailbox
import os
import sys

import pwd
import grp

mailsDeleted = 0
skipped = 0


def usage():
    print "Usage:"
    print "python ", sys.argv[0], " pathToDirWithMboxFiles TYPESEARCH \"ThingToSearch\""
    print "or"
    print "python ", sys.argv[0], " pathToDirWithMboxFiles "
    print "TYPESEARCH = {\n" \
          "              subject -- will search by email subject\n" \
          "              from -- will search headers by email sender\n" \
          "              to -- will search headers by email recepients\n" \
          "              return -- will search headers by return-path address\n" \
          "              regex -- will search by email content matching given regex\n" \
          "             }\n"
    sys.exit(1)


def getbodyfromemail(message):
    """
    Ciordit de pe stack, lene mare
    http://stackoverflow.com/questions/26567843/reading-the-mail-content-of-an-mbox-file-using-python-mailbox
    """
    body = None
    if message.is_multipart():
        for part in message.walk():
            if part.is_multipart():
                for subpart in part.walk():
                    if subpart.get_content_type() == 'text/plain':
                        body = subpart.get_payload(decode=True)
            elif part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True)
    elif message.get_content_type() == 'text/plain':
        body = message.get_payload(decode=True)
    return body


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


def deleteStuff(mboxlist, searchkey, deletebywhat):
    validOptions = ['subject', 'from', 'to', 'return', 'regex']
    if deletebywhat not in validOptions:
        print "Wrong TYPESEARCH option :)"
        usage()
    global mailsDeleted, skipped
    for mboxitem in mboxlist:
        mbox = mailbox.mbox(mboxitem)
        deleteList = []
        for key, msg in mbox.iteritems():
            try:
                if "regex" == deletebywhat:
                    if str(getbodyfromemail(msg)).find(searchkey) != -1:
                        print "Sterg mesajul (dupa regex match) cu cheia %s din inbox-ul userului %s" % (key, msg['to'])
                        deleteList.append(key)
                else:
                    if searchkey in msg[deletebywhat]:
                        print "Sterg mesajul (dupa %s) cu cheia %s din inbox-ul userului %s" % (
                        deletebywhat, key, msg['to'])
                        deleteList.append(key)
            except:
                skipped += 1
                print "Trecut peste %d mailuri cu subiect gol" % skipped
        mbox.lock()
        try:
            for key in deleteList:
                mbox.remove(key)
                mailsDeleted += 1

        finally:
            mbox.flush()
            mbox.close()
            os.chmod(mboxitem, 0600)
            numeuser = mboxitem.split("/")[-1]
            uid = pwd.getpwnam(numeuser).pw_uid
            gid = grp.getgrnam("mail").gr_gid
            os.chown(mboxitem, uid, gid)


try:
    dirlist = listdir_fullpath(sys.argv[1])
except:
    usage()

if len(sys.argv) == 4:
    typesearch = sys.argv[2]
    if "subject" in sys.argv[2]:
        print "Sterg mesajele dupa subject = \'%s\'" % sys.argv[3]
        searchkey = sys.argv[3]
        deleteStuff(dirlist, searchkey, "subject")
    elif "from" in sys.argv[2]:
        print "Sterg mesajele dupa campul from = \'%s\'" % sys.argv[3]
        searchkey = sys.argv[3]
        deleteStuff(dirlist, searchkey, "from")
    elif "to" in sys.argv[2]:
        print "Sterg mesajele dupa campul TO = \'%s\'" % sys.argv[3]
        searchkey = sys.argv[3]
        deleteStuff(dirlist, searchkey, "to")
    elif "return" in sys.argv[2]:
        print "Sterg mesajele dupa campul return-path = \'%s\'" % sys.argv[3]
        searchkey = sys.argv[3]
        deleteStuff(dirlist, searchkey, "Return-Path")
    elif "regex" in sys.argv[2]:
        print "Sterg mesajele dupa regex-ul = \'%s\' " % sys.argv[3]
        searchkey = sys.argv[3]
        deleteStuff(dirlist, searchkey, "regex")
else:
    typesearch = raw_input("Dupa ce sa sterg mailuri? subject/from/to/return/regex (TYPESEARCH):\n")
    searchkey = raw_input("Input-ul dupa care se sterg mailurile:\n")
    print "searchKey = ", searchkey
    recheck = raw_input("Continui? y/n ").lower()
    if recheck == "y":
        deleteStuff(dirlist, searchkey, typesearch)
    else:
        print "N-am primit \"y\", nu fac nimic"

if mailsDeleted == 0:
    print "N-am sters nimic, n-am gasit mailuri dupa %s-ul dat" % typesearch
else:
    print "Am sters %d mailuri" % mailsDeleted
    print "Am ignorat %d mailuri ce aveau subiect gol" % skipped
