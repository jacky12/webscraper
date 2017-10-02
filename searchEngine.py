#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

from tkinter import *
from tkinter import ttk

from src import analyzeResults, search, utils
import os

api_key = None
cse_id = None
num_results = None
start_index = None
overwritesentences = None
search_term = None
exact_terms = None
excluded_terms = None
key_phrases = None

# uncomment when creating executable files
# savepathtomain = "Documents" + os.sep + "EasySearch" + os.sep
# savepathtodata = savepathtomain + "data" + os.sep
# savepathtopdf = savepathtomain + "pdf" + os.sep

savepathtomain = os.getcwd() + os.sep
savepathtodata = savepathtomain + "data" + os.sep
savepathtopdf = savepathtomain + "pdf" + os.sep


# Reads input file for info
inputfile = open(savepathtomain + "input.txt", "r")
lines = inputfile.readlines()


for line in lines:
    if len(line) > 0 and line[0] != "#" and line[0] != '\n':
        if line[:3] == "API":
            api_key = line[(line.find(":") + 1):]
            api_key = utils.omitSpaces(api_key)
        if line[:3] == "CSE":
            cse_id = line[(line.find(":") + 1):]
            cse_id = utils.omitSpaces(cse_id)



# Arguments:
#   -search_term (string): search phrase for Google search to use (only used if "city" is False)
#   -before (string): string to append to before a city on a city search (only used if "city" is True)
#   -after (string): string to append to after a city on a city search (only used if "city" is True)
#   -num_results (int): the number of results for google search to return (range: 1 - 99)
#   -start_index (int): at what should google search start looking at
#   -exact_terms (string): an exact phrase for google search to look out for
#   -excluded_terms (string): a phrase to exclude from the google search
#   -api_key (string): google custom search API key
#   -cse_id (string): google custom search engine ID
#   -excel_file (string): path to the excel file containing the list of cities
#   -city (boolean): a True value will lead to a city search
# Returns: a list of search objects that contain the search results
# Effect: performs a google search with the given parameters
def searchEngine(search_term, before, after, num_results, start_index, exact_terms, excluded_terms, api_key, cse_id, overwrite, excel_file, city):
    # if overwrite == True:
    #     searches = []
    # else:
    #     searches = utils.npyImportPathSpecific(savepathtodata, filename)

    searches = []

    if city == True: # search over cities?
        new_searches = search.searchByCity(before, after, num_results, start_index, exact_terms, excluded_terms, api_key, cse_id, excel_file)
    else:
        new_searches = search.googleSearch(search_term, num_results, start_index, exact_terms, excluded_terms, api_key, cse_id)
    searches.extend(new_searches)
    return searches

# Arguments:
#   -searchList: a list of search objects
# Effect: downloads PDFs onto the "data" directory if a search object references a PDF
def downloadPDFs(searchList):
    savepath = savepathtopdf
    for search in searchList:
        if search.is_pdf == True and search.downloaded == False:
            utils.downloadFile(search, savepath)

# Arguments:
#   -dir_name: the path to the directory that contains the PDFs
#   -searchList: a list of search objects
# Effect: reads through all PDFs and webpages to gather the text as a string and append to the associated search object
# Returns a list of search objects with 'text' attribute appended
def getText(dir_name, searchList):
    pathToFile = savepathtopdf + dir_name + os.sep
    searchList = analyzeResults.readFiles(pathToFile, searchList,  '.pdf') # returns searchList with text appended
    return searchList


# Arguments:
#   -key_phrases: a list of words to look for
#   -searchList: a list of search Objects
# Effect: find sentences in a search object's text that contains a key word and appends them to
#           the associated search object
# Returns a list of search object with 'key_sentences' attribute appended
def getKeySentences(key_phrases, searchList):
    searchList = analyzeResults.findKeySentences(searchList, key_phrases) #returns searchList with key phrases appended
    return searchList

# Arguments:
#   -overwrite: boolean to determine if the existing CSV file should be overwritten or added onto
#   -key_phrases: list of words to look for
#   -searchList: list of search Objects
# Effect: shows the data on a CSV file with each row in this format
#           |url|search term|key words contained in sentence|sentence|
def showSentences(overwrite, key_phrases, searchList):
    pathToFile = savepathtodata

    utils.sentences(pathToFile, searchList, key_phrases, overwrite)



"""Ignore this part while it is being developed"""
searching = True
shownpy = False
overwritenpy = True # ignore searches from npy file
# overwritesentences = False
displayPhrases = False # only set to True if searching is false (meaning show an existing npy file)
searchByCity = False # search all cities for a specific search term (appends city name to search term)
before = ""
after = ""

excel_file = savepathtodata + "City_Energy_Mobility_Data.xlsx"
cities = utils.findCityList(excel_file)




def main(*args):

    # set arguments from user input
    start_index = 1
    starting = str(start.get())
    if starting != '':
        start_index = int(start.get())
    num_results = int(numres.get())
    search_term = str(searchphrase.get())
    exact_terms = str(exact.get())
    excluded_terms = str(excluded.get())
    key_phrases = str(key.get())


    if "," in key_phrases:
        key_phrases = key_phrases.split(",")
        for i in range(len(key_phrases)):
            key_phrases[i] = utils.omitSpaces(key_phrases[i])
    else:
        key_phrases = [utils.omitSpaces(key_phrases)] # situation where only one word in key phrase list

    searchList = searchEngine(search_term, before, after, num_results, start_index, exact_terms, excluded_terms,
                              api_key, cse_id, overwritenpy, excel_file, searchByCity)
    downloadPDFs(searchList)  # downloads PDFs
    searchList = getText(search_term, searchList)
    searchList = getKeySentences(key_phrases, searchList)
    showSentences(overwritesentences, key_phrases, searchList) # write data to CSV file
    print("Done with current search")




##### Everything below is for the GUI#####
root = Tk()
root.title("Automated Google Search Engine")

mainframe = ttk.Frame(root, padding = "3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
# mainframe.columnconfigure(0, weight=1)
# mainframe.rowconfigure(0, weight=1)



numres = StringVar()
start = StringVar()
searchphrase = StringVar()
exact = StringVar()
excluded = StringVar()
key = StringVar()



ttk.Label(mainframe, text="Number of Results*").grid(column=1, row=1, sticky=E)
num_results_entry = ttk.Entry(mainframe, width = 7, textvariable = numres)
num_results_entry.grid(column = 2, row = 1, sticky = (W, E))

ttk.Label(mainframe, text="Starting Index").grid(column=1, row=2, sticky=E)
start_index_entry = ttk.Entry(mainframe, width = 7, textvariable = start)
start_index_entry.grid(column = 2, row = 2, sticky = (W,E))

ttk.Label(mainframe, text="Search Term*").grid(column=1, row=3, sticky=E)
search_term_entry = ttk.Entry(mainframe, width = 20, textvariable = searchphrase)
search_term_entry.grid(column = 2, row = 3, sticky = (W,E))

ttk.Label(mainframe, text="Exact Term").grid(column=1, row=4, sticky=E)
exact_terms_entry = ttk.Entry(mainframe, width = 20, textvariable = exact)
exact_terms_entry.grid(column = 2, row = 4, sticky = (W,E))

ttk.Label(mainframe, text="Excluded Term").grid(column=1, row=5, sticky=E)
excluded_terms_entry = ttk.Entry(mainframe, width = 20, textvariable = excluded)
excluded_terms_entry.grid(column = 2, row = 5, sticky = (W,E))

ttk.Label(mainframe, text="Key Phrases*").grid(column=1, row=6, sticky=E)
key_phrases_entry = ttk.Entry(mainframe, width = 20, textvariable = key)
key_phrases_entry.grid(column = 2, row = 6, sticky = (W,E))

ttk.Button(mainframe, text="Search", command=main).grid(column=3, row=7, sticky=W)

ttk.Label(mainframe, text="*: Required").grid(column=1, row=7, sticky=W)

for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

num_results_entry.focus()

root.mainloop()