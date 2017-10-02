# import numpy as np
import os
from .utils import loadURL, appendCityToTerm
import sys

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class Search:
    def __init__(self, search_term, url, response, is_pdf):
        self.search_term = search_term
        self.url = url
        self.response = response
        self.is_pdf = is_pdf
        self.downloaded = False
        self.text = None
        self.key_sentences = None
        self.errored = False




"""Returns a list of searches"""
def googleSearch(search_term, num_results, start_index, exact_terms, excluded_terms, api_key, cse_id, **kwargs):
    print("\nPerforming Google Search and loading ", num_results, "results...")
    items = [] #stores the URL results
    num_calls = (num_results // 10) + 1
    service = build("customsearch", "v1", developerKey=api_key)
    maxed_out = False # haven't maxed out at beginning
    counter = 0 # Ordering websites found
    while num_calls > 0 and maxed_out is False:
        # for num_results > 10, I have to break up the search
        # into mulitiple searches, since each search yields a max of 10 results
        if num_calls == 1:
            numberofresults = num_results - ((num_results // 10) * 10)
            if numberofresults == 0:
                break
        else:
            numberofresults = 10
        try:
            res = service.cse().list(q=search_term, cx=cse_id, num=numberofresults, start=start_index, exactTerms = exact_terms, excludeTerms = excluded_terms, **kwargs).execute()
        except HttpError:
            print("Max searches reached")
            maxed_out = True
            break
        else:
            num_calls -= 1
            start_index += 10
            items.extend([x["link"] for x in res['items']])
    searches = []
    for url in items:
        try:
            search = Search(search_term, url, loadURL(url), url[-4:] == '.pdf')
            searches.append(search)
        except:
            print("\nCouldn't load ", url, "\n")
            continue
        else:
            counter += 1
            print(counter, ". ", url)

    if searches == []:
        sys.exit()
    return searches


# Deprecated
def searchByCity(before, after, num_results, start_index, exact_terms, excluded_terms, api_key, cse_id, filename):
    searches = []
    search_terms = appendCityToTerm(filename, before, after)
    for search_term in search_terms:
        searches.extend(googleSearch(search_term, num_results, start_index, exact_terms, excluded_terms, api_key, cse_id))
    return searches

