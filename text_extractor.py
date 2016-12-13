import json
import re
import pickle

from bs4 import BeautifulSoup

# use beautifulsoup to extract text from web pages, somehow look at ad landing pages too? how would you do classification/learning?

def extract_text_links(filename):
    """
    Extracts all the text and links from a web page.
    """
    with open(filename) as f:
        data = BeautifulSoup(f)
        text = data.get_text()
        links = []
        for link in data.find_all('a'):
            links.append(link.get('href'))
        return text, links

def build_category_classifier(categories):
    """
    Builds a bag-of-words logistic classifier to classify
    """

URL_RE = '[a-z0-9\-\.]+\.[a-z]+'

def process_url(url):
    """
    Given a url, this extracts only the 'main' part of the address.
    """
    url = url.lower()
    m = re.search(URL_RE, url)
    return m.group()

if __name__ == '__main__':
    with open('alexa_subcategories.json') as f:
        data = json.load(f)
    categories = set([x['name'] for x in data])
    category_sites = {}
    site_categories = {}
    for sites in data:
        c = sites['name']
        # only take the top 100 sites
        if sites['page_num']>5:
            continue
        if c in category_sites:
            category_sites[c] += sites['links']
        else:
            category_sites[c] = sites['links']
        for link in sites['links']:
            try:
                link = process_url(link)
                if link in site_categories:
                    site_categories[link].add(c)
                else:
                    site_categories[link] = set([c])
            except:
                print link
    with open('category_sites.pkl', 'w') as f:
        pickle.dump(category_sites, f)
    with open('site_categories.pkl', 'w') as f:
        pickle.dump(site_categories, f)


