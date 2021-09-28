from bs4 import BeautifulSoup
import requests
import sys
import getopt
import re
import datetime
from dateutil import tz
from definitions import STATUS_FILE, MOST_RECENT_FILE, MAIN_URL, CountryData

PROGRAM_NAME = 'scraper.py'

def usage():
    print('usage: python3 ' + PROGRAM_NAME + ' [--help|--production]')

def writeCountryData(filePath, countryData):
    with open(filePath, 'w') as statusFile:
        statusFile.write('country,updateTime,updateTimestamp,link\n')
        for oneCountryData in countryData:
            statusFile.write(oneCountryData.country + ',' + \
                                oneCountryData.updateTime + ',' + \
                                str(oneCountryData.updateTimestamp) + ',' + \
                                oneCountryData.link + '\n')

def parseCountryNameFromAnchor(countryAnchor):
    strong = countryAnchor.find('strong')
    if strong != None:
        return strong.string
    return countryAnchor.string

def parseRawUpdateTime(articleDateElement):
    updatedElement = articleDateElement.find('span', {'class': 'updated'})
    if updatedElement == None:
        return articleDateElement.string
    return updatedElement.find('span', {'class': 'time'}).string

def main(argv):
    opts, args = getopt.getopt(argv, '', ['help', 'production'])
    production = False
    for opt, arg in opts:
        if opt == '--help':
            usage()
            exit(0)
        elif opt == '--production':
            production = True
        else:
            usage()
            exit(1)

    response = requests.get(MAIN_URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    countryAnchors = soup.find('div', {'class': 'article_content'}) \
                            .div.find_all('a', href=re.compile('https://www.mzv.cz/'))

    if not production:
        countryAnchors = countryAnchors[0:3] # artificially limit the list for dev purposes

    countryLinks = list(map(lambda a: a.attrs['href'], countryAnchors))
    countryNames = list(map(parseCountryNameFromAnchor, countryAnchors))
    countryData = []
    for i, countryLink in enumerate(countryLinks):
        response = requests.get(countryLink)
        soup = BeautifulSoup(response.content, 'html.parser')
        articleDateElement = soup.find('p', {'class': 'articleDate'})
        if articleDateElement == None:
            print('Warning: skipping unparsable country: ' + countryNames[i])
            # TODO: the list of unparsable countries should be part of an email, for reference
            continue
        rawUpdateTime = parseRawUpdateTime(articleDateElement)
        dateMatch = re.search('\s?(.+)\s/', rawUpdateTime)
        if dateMatch != None:
            date = dateMatch.group(1)
            time = re.search('/\s(.+)', rawUpdateTime).group(1)
        else:
            date = re.search('\s?(.+)$', rawUpdateTime).group(1)
            time = '00:00'
        updateTime = date + ' ' + time
        updateTimestamp = datetime.datetime.strptime(updateTime, "%d.%m.%Y %H:%M") \
                            .replace(tzinfo=tz.gettz('Europe/Prague')).timestamp()
        updateTimestamp = int(updateTimestamp)
        countryData.append(CountryData(countryNames[i], updateTime, updateTimestamp, countryLink))
    writeCountryData(STATUS_FILE, countryData)

    mostRecent = sorted(countryData, key=lambda d: d.updateTimestamp, reverse=True)
    writeCountryData(MOST_RECENT_FILE, mostRecent)

if __name__ == '__main__':
    main(sys.argv[1:])
