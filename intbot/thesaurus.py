import re
import sys
import urllib.error
from urllib.request import urlopen
from bs4 import BeautifulSoup

import argparse

parser = argparse.ArgumentParser(
    description='Get the thesaurus of word from  thesaurus.com/dictionary.com')
parser.add_argument('word', help="Word to get definition/synonym/antonym for")
parser.add_argument('-d', action='store_true',
                    help="get definition")
parser.add_argument('-s', choices=['noun', 'verb', 'adj'],
                    help="get POS specific synonyms")
parser.add_argument('-a', action='store_true',
                    help="get antonyms")

args = parser.parse_args()
# print(args.word)
# print(args.method)


class PosTagError(Exception):
    """Exception raised when incorrect pos tag is passed to Thesaurus.get_synonym"""

    def __init__(self, message):
        super(PosTagError, self).__init__(message)
        self.message = message

    # __str__ is to print() the value
    def __str__(self):
        return(repr(self.message))

def main():
    new_instance = Thesaurus(args.word)
    if args.d:
        print("Definitions")
        print(new_instance.get_definition())
    if args.s:
        print("Synonyms")
        print(new_instance.get_synonym(args.s))
    if args.a:
        print("Antonyms")
        print(new_instance.get_antonym())
    if not args.d and not args.s and not args.a:
        print("You must specify atleast one of the -d -s -a flags")

class Thesaurus():

    """
    A class to fetch synonyms of a word from thesaurus.com
    using selenium or beautiful soup
    """

    def __init__(self, word):
        self.entry = word

    def valid_entry_check(self):
        """
        Check if input is null or contains only spaces or numbers or special characters
        """
        temp = re.sub(r'[^A-Za-z ]', ' ', self.entry)
        temp = re.sub(r"\s+", " ", temp)
        temp = temp.strip()
        if temp != "":
            return True
        return False

    def get_synonym(self, pos="noun"):
        """
        Fetches the synonyms from the thesaurus.com using Beautiful Soup
        """
        try:
            if self.valid_entry_check():
                if pos == "noun":
                    response = urlopen(
                        'http://www.thesaurus.com/browse/{}/noun'.format(self.entry))
                elif pos == "verb":
                    response = urlopen(
                        'http://www.thesaurus.com/browse/{}/verb'.format(self.entry))
                elif pos == "adj":
                    response = urlopen(
                        'http://www.thesaurus.com/browse/{}/adjective'.format(self.entry))
                else:
                    raise PosTagError(
                        'invalid pos tag: {}, valid POS tags: {{noun,verb,adj}}'.format(pos))
                html = response.read().decode('utf-8')
                soup = BeautifulSoup(html, 'lxml')
                result = []
                for main_div in soup.findAll('div', {'id': 'synonyms-0'}):
                    for element in main_div.findAll('div', {'class': 'relevancy-list'}):
                        for sub_elem in element.findAll('span', {'class': 'text'}):
                            if sub_elem.text not in result:
                                result.append(sub_elem.text)
                return result
            else:
                print("Provide a not-null input word")
                return []
        except urllib.error.HTTPError as err:
            if err.code == 404:
                return []
        except urllib.error.URLError:
            print("No Internet Connection")
            return []
        except PosTagError as err:
            print(err)
        except:
            print(sys.exc_info())
            return []

    def get_definition(self):
        """
        Fetches the definitions from the dictionary.com \
        using Beautiful Soup
        """
        try:
            if self.valid_entry_check():
                response = urlopen(
                    'http://www.dictionary.com/browse/{}'.format(self.entry))
                html = response.read().decode('utf-8')
                soup = BeautifulSoup(html, 'lxml')
                result = []
                section = soup.select(
                    '#source-luna > div:nth-of-type(1) > section > div.source-data > \
                    div.def-list > section')[0]
                elements = section.select("> div.def-set > div.def-content")
                for elem in elements:
                    for remove in elem.findAll("div", {"class": "def-block \
                    def-inline-example"}):
                        remove.decompose()
                    temp = elem.text
                    temp = re.sub(r"\s+", " ", temp)
                    temp = temp.strip()
                    temp = temp.rstrip(":")
                    temp = temp.capitalize()
                    if temp not in result:
                        result.append(temp)
                if len(result) > 5:
                    return result[:5]
                return result
            else:
                print("Provide a not-null input word")
                return []
        except urllib.error.HTTPError as err:
            if err.code == 404:
                print("Word is not valid")
                return []
        except IndexError:
            print("Give a non-empty argument")
            return []
        except urllib.error.URLError:
            print("No Internet Connection")
            return []

    def get_antonym(self):
        """
        Fetch the antonyms for the inserted word
        """
        try:
            if self.valid_entry_check():
                response = urlopen(
                    'http://www.thesaurus.com/browse/{}/noun'.format(self.entry))
                html = response.read().decode('utf-8')
                soup = BeautifulSoup(html, 'lxml')
                result = []
                for main_div in soup.findAll('div', {'id': 'synonyms-0'}):
                    for super_element in main_div.findAll("section", {"class": "container-info antonyms"}):
                        for element in super_element.findAll('div', {'class': 'list-holder'}):
                            for sub_elem in element.findAll('span', {'class': 'text'}):
                                if sub_elem.text not in result:
                                    result.append(sub_elem.text)
                    break
                return result
            else:
                print("Provide a not-null input word")
                return []
        except urllib.error.HTTPError as err:
            if err.code == 404:
                return []
        except urllib.error.URLError:
            print("No Internet Connection")
            return []
        except:
            print(sys.exc_info())
            return []
