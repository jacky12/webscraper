from urllib.request import Request, urlopen #Modules used to access websites with their URLs
from urllib.error import URLError, HTTPError #Modules used to deal with errors with accessing websites
from http.client import IncompleteRead #Strange error catch
from ssl import CertificateError #Strange error catch and bypass
import ssl
import sys
from bs4 import BeautifulSoup
# import textract
from .utils import getDomain, omitSpaces
import re
import regex

# returns the HTML of a url
def loadURL(url):
    if url[0:4] != 'http':
        url = 'http://' + url
    context = ssl._create_unverified_context()  # bypasses SSL Certificate Verfication (proabably not a good idea, but it got more sites to work)
    req = Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'})  # changing the header prevents some webscraper blocking techniques
    try:

        response = urlopen(req, context=context).read()  # opens the URL and returns data (in bytes)
    except ConnectionResetError:
        print('Server didn\'t send data' + ' ' + url)
        return
    except HTTPError as e:
        print('HTTPError: ' + str(e.code) + ' ' + url)
        return
    except URLError as e:
        print('We failed to reach a server. ' + url)
        return
    except CertificateError:
        print("SSL Certificate Error with ", url)
        return
    except IncompleteRead as e:
        print("IncompleteRead Error with ", url)
        return
    except:
        e = sys.exc_info()[0]
        print(e)
        return
    else:
        return response


# Arguments:
#   -html: the html of a site
# Returns:
#   -text: a string containing the text
# Effect: Extracts text from html
def textExtracter(html):
    soup = BeautifulSoup(html,"html.parser") # get html from site

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = text.split('\n')
    lines = [line for line in lines if line != '']
    return lines # returns a String with all text


# Arguments:
#   -pathToFile: path to the directory containing the PDFs
#   -searchList: a list of the search objects
#   -extension: the extension of the file (in this case, it will be .pdf almost all the time)
# Returns: a list of search objects
# Effect: takes in a list of search objects (with html attribute appended)
#           and performs text extraction for each search object
def readFiles(pathToFile, searchList, extension): # files is a list of strings containing the file names and their extensions
    print("\nGathering text from websites...")
    for search in searchList:
        if search.downloaded == True and search.text is None:
            try:
                filename = getDomain(search.url)
                # print("This is " + file + "\'s text.")
                text = textract.process(pathToFile + filename + extension).decode("utf-8") # textract not working
                lines = text.split('\n')
                lines = [line for line in lines if line != '']
                search.text = lines
            except:
                print("Failed to analyze " + filename + "\'s text.")
                search.errored = True
                continue
        elif search.is_pdf == False and search.response is not None and search.text is None:
            response = search.response
            text = textExtracter(response)
            search.text = text
    return searchList


# Arguments:
#   -searchList: a list of search objects
#   -key_phrases: a list of phrases to search sentences
# Return: a list of search objects
# Effect: goes through the text of each search object to find sentences containing keywords
#       and append them to their corresponding search object
def findKeySentences(searchList, key_phrases):
    print("\nFinding sentences with key phrases...")

    #returns True if at least one element of key_phrases is contained in sentence (a string)
    def containsPhrase(sentence, key_phrases):
        for phrase in key_phrases:
            if sentence.find(phrase) != -1:
                return True
            else:
                return False

    def findNumbers(line):
        line = line.replace(',', '')
        numbers = regex.findall(r'\p{Sc}', line)
        return numbers
    found = False
    for search in searchList:
        lineerror = 1
        if search.key_sentences is None and search.text is not None:
            lines = search.text

            collect_lines = [] # collect all lines containing keyword of a search object
            for i, v in enumerate(lines):
                # new_line = []
                if containsPhrase(v.lower(), key_phrases):
                    collect_lines.append(lines[i])
                #     if len(v) < 15:
                #         lineerror = 3
                #     elif len(v) < 30:
                #         lineerror = 2
                #     else:
                #         lineerror = 1
                #     for line in lines[i - lineerror: i + lineerror]:
                #         line = omitSpaces(line)
                #         new_line.append(line)
                # if new_line != []:
                #
                #     collect_lines.append(" ".join(new_line))

            # collect_lines = []
            # for i, v in enumerate(lines):
            #     new_line = []
            #     if findNumbers(v.lower()) != []:
            #         for line in lines[i - 3: i + 3]:
            #             line = omitSpaces(line)
            #             new_line.append(line)
            #     if new_line != []:
            #         collect_lines.append(" ".join(new_line))

            search.key_sentences = collect_lines
            capitalized_sentences = [] # capitalize keywords
            if search.key_sentences != []:
                found = True
            for sentence in search.key_sentences:
                for phrase in key_phrases:
                    sentence = sentence.replace(phrase, phrase.upper())
                    sentence = sentence.replace(phrase.title(), phrase.upper())
                capitalized_sentences.append(sentence)
            search.key_sentences = capitalized_sentences

    if (found == False):
        print("\nNo sentences with key phrases found.")
    return searchList