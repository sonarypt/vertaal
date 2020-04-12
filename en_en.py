#!/usr/bin/env python3

# this project translate one word 
# using www.dictionary.com with requests and xpath
# TODO: synonyms of the word

import os
import sys
import langid
import requests
import textwrap
from lxml import html
from tabulate import tabulate
import xml.etree.cElementTree as ET
from xml.etree.ElementTree import fromstring

class format:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

host = "www.dictionary.com"
main_link = "https://" + host + "/"
api_host = "api-portal.dictionary.com"

global WIDTH
WIDTH = int(int(os.popen('stty size', 'r').read().split()[1])*3/4)

word = sys.argv[1]

if langid.classify(word)[0] != "en":    # check if input word is English
    print("Your word \"" + word + "\" is not English")
    sys.exit()

# get seaerch result in html
s_link = main_link + "browse/" + word

headers = { # specify headers for requests
      'Host': host,
      'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/75.0",
      'Accept': '*/*',
      'Accept-Language': 'en-US,en;q=0.5',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1'
      }

res = requests.get(s_link, headers=headers)

hx = html.fromstring(res.content)

global tbl
tbl = []     # the main table

def tw(content):
    return textwrap.fill(content, width=WIDTH)

def ft(content, ttype):
    return getattr(format, ttype) + content + format.END

def get_subdef(subsection, table):   # increment subindex and definitions
    subindex = "a"
    for subsubsection in subsection.xpath("./ol/li"):
        table.append(["", subindex, tw(subsubsection.text_content())])
        subindex = chr(ord(subindex) + 1)

def add_examples(subsection, table):    # add examples to table
    example = subsection.xpath("./span/span[@class='luna-example italic']")[0].text
    table.append(["", "", tw(ft(example, 'BLUE'))])

# this function get text from remaining <span> after luna-label 
def txt_in_span(subsection, start_index):     # get text from direct tag, not from children
    span_list = subsection.xpath("./span")[start_index:]    # cut the list from start_index
    span_str_list = [i.text_content() for i in span_list]
    return ' '.join(span_str_list)

def arrange_lab_exp(subsection, index, table):    # arrange output of subsection base on structure
    subindex = ""
    examples = subsection.xpath(".//span[@class='luna-example italic']")
    label = subsection.xpath(".//span[@class='luna-label italic']")
    if label != []:
        table.append([index, subindex, tw(ft(label[0].text_content(), 'UNDERLINE'))])
        #  table.append(["", "", tw(subsection.xpath("./span")[1].text)])
        table.append(["", "", tw(txt_in_span(subsection, 1))])
        if examples != []:      # with luna-label and luna-example
            add_examples(subsection, table)
    else:
        if examples == []:      # without luna-label and luna-example
            table.append([index, subindex, tw(subsection.text_content())])
        else:                   # without luna-label but with luna-example
            table.append([index, subindex, tw(subsection.xpath("./span")[0].text)])
            add_examples(subsection, table)

def get_def(section, table):
    index = "1"
    for subsection in section.xpath("./div[@class='css-1o58fj8 e1hk9ate4']//div[@value]"):
        #  print(index + "\t" + subsection.text_content())
        #  print(subsection.xpath("./span")[0].text_content())
        #  print(subsection.xpath("./span"))
        subindex = ""
        sublist = subsection.xpath("./ol/li")
        if sublist == []:
            arrange_lab_exp(subsection, index, table)
        else:
            label = subsection.xpath("./span")[0].text_content()
            table.append([index, subindex, label])
            get_subdef(subsection, index, table)
        index = str(int(index) + 1)

# list of all possible definitions
msec = hx.xpath("//div[not(@id) and @class='css-1urpfgu e16867sm0']")[0]    # first master section in definitions
for sec in msec.xpath(".//section[@class='css-pnw38j e1hk9ate0']"):         # smaller sections contain information
    dn = sec.xpath("./h3")[0].text_content()        # type of words
    tbl.append(["", "", ft(dn, 'BOLD')])              # bold text
    get_def(sec, tbl)                                    # print all definitions of this type
#  print("----------")
print(tabulate(tbl, tablefmt="plain"))    # print formatted string of definitions
