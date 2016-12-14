from collections import Counter
import glob
import os
import sys
import pickle

import matplotlib.pyplot as plt
import pandas as pd

from text_extractor import process_url

def filter_category(categories):
    """
    Given a set of categories, returns the first non-subcategory,
    else just return the first one
    """
    for c in categories:
        if '-' not in c:
            return c
    for c in categories:
        return c.split('-')[0]

if __name__=='__main__':
    category_sites = pickle.load(open('category_sites.pkl'))
    site_categories = pickle.load(open('site_categories.pkl'))
    print sys.argv
    dirs = sys.argv[1:]
    all_ad_cats = {}
    all_ad_cats_broad = {}
    all_ad_links = {}
    all_ad_links_no_remarketing = {}
    all_ad_cats_no_remarketing = {}
    for d in dirs:
        dir_category = d.split('_')[0]
        print dir_category
        visited_sites = set()
        if dir_category!='None':
            visited_sites = set([process_url(x) for x in category_sites[dir_category][:150]])
        ad_categories = pickle.load(open(os.path.join(d, 'ad_site_cats.pkl')))
        ad_cats = []
        ad_links = []
        ad_links_not_visited = []
        ad_cats_not_visited = []
        for site, ad_link_cats in ad_categories.iteritems():
            for link,cats in ad_link_cats:
                if link=='bbc.com' or link=='aol.com':
                    continue
                ad_links.append(link)
                ad_cats.extend(cats)
                if link not in visited_sites:
                    ad_links_not_visited.append(link)
                    ad_cats_not_visited.extend(cats)
        all_ad_cats[d] = Counter(ad_cats)
        all_ad_links[d] = Counter(ad_links)
        all_ad_cats_broad[d] = Counter(filter_category(site_categories[x]) for x in ad_links)
        all_ad_links_no_remarketing[d] = Counter(ad_links_not_visited)
        all_ad_cats_no_remarketing[d] = Counter(filter_category(site_categories[x]) for x in ad_links_not_visited)
    # create a data table
    ad_cats_table = pd.DataFrame(all_ad_cats_broad).transpose()
    ad_cats_table[ad_cats_table.isnull()] = 0
    ad_cats_freq = ad_cats_table.apply(lambda x: x/sum(x), 1)
    ad_cats_table_no_rem = pd.DataFrame(all_ad_cats_no_remarketing).transpose()
    ad_cats_table_no_rem[ad_cats_table_no_rem.isnull()] = 0
    ad_cats_freq_no_rem = ad_cats_table_no_rem.apply(lambda x: x/sum(x), 1)

    ad_cats_freq.to_csv('ad_cats_freq.tsv', sep='\t')
    ad_cats_table.to_csv('ad_cats_counts.tsv', sep='\t')

    ad_cats_table_no_rem.to_csv('ad_cats_counts_no_rem.tsv', sep='\t')
    ad_cats_freq_no_rem.to_csv('ad_cats_freq_no_rem.tsv', sep='\t')

