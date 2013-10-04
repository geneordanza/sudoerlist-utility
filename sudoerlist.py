#!/usr/bin/python
"""
NAME: sudoerlist.py
DESC: This programs display a list of users who have sudo access
LAST REV: 25th Jan 2013
AUTHOR: Gene Ordanza <geronimo.ordanza@fisglobal.com>
NOTE: Need to re-write this in shell (preferrably in ksh) and port to Solaris
      and AIX. (20131004)
"""

import socket
from datetime import datetime

#HOME, PASSWD, SUDOER, GROUP = ('home', 'passwd', 'sudoers', 'group')
HOME, PASSWD, SUDOER, GROUP = ('home', '/etc/passwd', '/etc/sudoers', '/etc/group')

USERALIAS = 'User_Alias'

def sudoindiv():
    fs = open(SUDOER)

    sudolist = []

    try:
        for x in fs:
            if x[0] == 'U' and x.split()[0] == USERALIAS:
                temp = x.split('=')[1].split(',')
                sudolist.extend(temp)
                temp = []

    finally:
        fs.close()

    return sudolist


def sudogroup():
    fs = open(SUDOER)
    fg = open(GROUP)
    templist, sudolist = ([], [])

    try:
        # Extract sudoer group from /etc/sudoers.
        sudogroup = [ x.split()[0].split('%')[1] for x in fs if x[0] == '%' ]

        # Extract users from sudogroup in /etc/group.
        for group in sudogroup:
            for line in fg:
                if line.find(group) >= 0:
                    templist.append(line.split(':')[-1].strip())
            fg.seek(0)

    finally:
        fs.close()
        fg.close()

    # Collect all sudo users into a single list.
    for x in templist:
        sudolist.extend(x.split(','))

    return sudolist

def userlisting():
    fp = open(PASSWD)
    fs = open(SUDOER)

    isUserAlias, finalist = False, []

    # Check if User_Alias is set on /etc/sudoers
    isUserAlias = [ True for x in fs if x[0] == 'U' and x.split()[0] == USERALIAS ]

    if isUserAlias:
        sudolist = sudoindiv()
    else:
        sudolist = sudogroup()

    try:
        # Extract all valid user from localhost.
        userlist = [ line.strip() for line in fp if line.find(HOME) >= 0 ]

        # Extract the login and real name from the userlist.
        # NOTE: This line is a hack. Need to write it properly.
        enumlist = [ (x.split(':')[0], ' '.join(x.split(':')[4].split()[0:2])) \
                     for x in userlist ]

        # Convert content of enumlist from tuple into list so we can append
        # other info to the variable.
        userlist = [ list(x) for x in enumlist ]

    finally:
        fp.close()


    # Old-school and unPythonic, there should be a more elegant way to do this.
    for (login, name) in userlist:
        value = False
        for sudoer in sudolist:
            if sudoer.find(login) >= 0:
                value = True
                break
        if value:
            finalist.append([login, name, 'YES'])
        else:
            finalist.append([login, name, 'FALSE'])

    return finalist


def report(listings):
    format = '%-9s %-20s %-6s'
    header = ('Login', 'Real Name', 'SUDO')

    print 'Hostname: %s' % socket.gethostname().upper()
    print 'Date: %s\n' % str(datetime.now()).split()[0]

    print format % header

    for user in listings:
        print format % tuple(user)

def main():
    report(userlisting())

if  __name__ == '__main__':
    main()

