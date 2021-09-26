import sys
import os
import tempfile
import shutil
import getopt
import re
import datetime
import json
from dateutil import tz
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from definitions import STATUS_FILE, MOST_RECENT_FILE, MAIN_URL, CountryData, MailData

PROGRAM_NAME = 'reporter.py'
MAIL_SETTINGS_FILE = 'mail-settings.json'
MAIL_LIST_FILE = 'mail_list.csv'

def readCountryData(filePath):
    countryData = []
    with open(filePath, 'r') as f:
        firstLine = True
        while 1:
            line = f.readline()
            if line == '':
                break
            if not firstLine:
                country, updateTime, updateTimestamp, link = line.rstrip().split(',')
                countryData.append(CountryData(country, updateTime, int(updateTimestamp), link))
            firstLine = False
    return countryData

def readMailListData(filePath):
    mailListData = []
    with open(filePath, 'r') as f:
        firstLine = True
        while 1:
            line = f.readline()
            if line == '':
                break
            if not firstLine:
                name, nameInHelloForm, email = line.rstrip().split(',')
                mailListData.append(MailData(name, nameInHelloForm, email))
            firstLine = False
    return mailListData

def usage():
    print('usage: python3 ' + PROGRAM_NAME + ' [--help] -d|-w')

def filterUpdates(countryData, duractionInSeconds):
    nowTimestamp = datetime.datetime.now().timestamp()
    return list(filter(lambda x: nowTimestamp - x.updateTimestamp < duractionInSeconds, countryData))

def main(argv):
    opts, args = getopt.getopt(argv, 'dw', ['help'])
    daily = False
    weekly = False
    for opt, arg in opts:
        if opt == '--help':
            usage()
            exit(0)
        elif opt == '-d':
            daily = True
        elif opt == '-w':
            weekly = True
        else:
            usage()
            exit(1)

    if (not daily and not weekly) or (daily and weekly):
        usage()
        exit(1)

    countryData = readCountryData(STATUS_FILE)

    oneDayInSeconds = 60 * 60 * 24
    oneWeekInSeconds = oneDayInSeconds * 7
    updates = []
    if daily:
        updates = filterUpdates(countryData, oneDayInSeconds)
    if weekly:
        updates = filterUpdates(countryData, oneWeekInSeconds)

    if len(updates) == 0:
        return

    mailListData = readMailListData(MAIL_LIST_FILE)
    for mailData in mailListData:
        sendReport(mailData, updates, daily)

def sendMail(receiver, message):
    with open(MAIL_SETTINGS_FILE, 'r') as f:
        mailSettings = json.load(f)
        mailSettings['receiver'] = receiver
        mailSettings['message'] = message
    with open(MAIL_SETTINGS_FILE, 'w') as f:
        f.write(json.dumps(mailSettings, indent=4))
    result = os.system('python3 ../mail-sender/send_mail.py ' + MAIL_SETTINGS_FILE)
    if result != 0:
        print('Failed to send email to ' + receiver)

def getBody(mailData, updates, daily, plain):
    weekly = not daily
    html = not plain
    body = ''

    if html:
        body += '<html><head></head><body><p>'

    body += 'Ahoj ' + mailData.nameInHelloForm + ','

    body += newLine(plain, html)
    body += newLine(plain, html)

    body += 'zde je seznam zemí, u kterých za poslední'
    if daily:
        body += ' den'
    elif weekly:
        body += ' týden'

    body += ' proběhla aktualizace cestovních omezení:'

    body += newLine(plain, html)
    if plain:
        body += newLine(plain, html)

    if html:
        body += '<ul>'

    for update in updates:
        if plain:
            body += '  - ' + update.country + '\n'
        elif html:
            body += '<li><a href="' + update.link + '">' + update.country + '</a></li>'

    if html:
        body += '</ul>'

    if plain:
        body += newLine(plain, html)

    if html:
        body += 'Pro více informací klikni na odkaz s danou zemí.'
        body += newLine(plain, html)
        body += newLine(plain, html)

    body += 'S pozdravem,'
    body += newLine(plain, html)
    body += 'robot CovidTravelNewsCZ'

    if html:
        body += '</p></body></html>'

    return body

def newLine(plain, html):
    if plain:
        return '\n'
    elif html:
        return '<br>'

def sendReport(mailData, updates, daily):
    weekly = not daily

    subject = ''
    if daily:
        subject += 'Denní'
    elif weekly:
        subject += 'Týdenní'
    subject += ' aktualizace cestovních omezení'

    bodyPlain = getBody(mailData, updates, daily, True)
    bodyHtml = getBody(mailData, updates, daily, False)

    part1 = MIMEText(bodyPlain, 'plain')
    part2 = MIMEText(bodyHtml, 'html')

    mimeMessage = MIMEMultipart('alternative')
    mimeMessage['Subject'] = subject
    mimeMessage['From'] = getSender()
    mimeMessage['To'] = mailData.email
    mimeMessage.attach(part1)
    mimeMessage.attach(part2)
    mimeMessageStr = mimeMessage.as_string()

    # TODO: attach the .csv files for reference

    sendMail(mailData.email, mimeMessageStr)

def getSender():
    with open(MAIL_SETTINGS_FILE, 'r') as f:
        mailSettings = json.load(f)
        return mailSettings['sender']

if __name__ == '__main__':
    main(sys.argv[1:])