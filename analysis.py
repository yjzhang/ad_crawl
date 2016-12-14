from collections import Counter
import glob
import os
import sys
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.stats.proportion import proportions_chisquare, proportions_chisquare_allpairs

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
    # no_rem is short for no remarketing, which is what happens when you're
    # shown ads for a site you've visited.
    ad_cats_table_no_rem = pd.DataFrame(all_ad_cats_no_remarketing).transpose()
    ad_cats_table_no_rem[ad_cats_table_no_rem.isnull()] = 0
    ad_cats_freq_no_rem = ad_cats_table_no_rem.apply(lambda x: x/sum(x), 1)

    ad_cats_freq.to_csv('ad_cats_freq.tsv', sep='\t')
    ad_cats_table.to_csv('ad_cats_counts.tsv', sep='\t')

    ad_cats_table_no_rem.to_csv('ad_cats_counts_no_rem.tsv', sep='\t')
    ad_cats_freq_no_rem.to_csv('ad_cats_freq_no_rem.tsv', sep='\t')

    # do some statistical tests... chisquare?
    chi2_cats = proportions_chisquare_allpairs(ad_cats_table, ad_cats_table.sum(1))
    chi2_cats_no_rem = proportions_chisquare_allpairs(ad_cats_table_no_rem, ad_cats_table_no_rem.sum(1))

    # correlation coefficient
    ad_cats_corr = ad_cats_freq.T.corr()
    ad_cats_corr_no_rem = ad_cats_freq_no_rem.T.corr()

    # create bar plots for the ads targeted in each category?
    xlab = np.arange(ad_cats_table.shape[1])
    for category in ad_cats_table.index:
        plt.clf()
        plt.bar(xlab, ad_cats_freq.loc[category])
        plt.ylim(0, 0.3)
        plt.xticks(xlab+0.5, ad_cats_table.columns, rotation='vertical')
        plt.title(category.split('_')[0])
        plt.subplots_adjust()
        plt.subplots_adjust(bottom=0.21)
        plt.savefig('{0}.png'.format(category), dpi=240)

    # create heatmaps using the chi-square values
    heatmap1 = np.zeros((8,8))
    for pair, pval in zip(chi2_cats.all_pairs, chi2_cats.pval_corrected()):
        heatmap1[pair] = pval
        heatmap1[pair[1], pair[0]] = pval
        heatmap2 = np.zeros((8,8))
    for pair, pval in zip(chi2_cats.all_pairs, chi2_cats_no_rem.pval_corrected()):
        heatmap2[pair] = pval
        heatmap2[pair[1], pair[0]] = pval
    for i in range(8):
        heatmap1[i,i] = 1.0
        heatmap2[i,i] = 1.0
    plt.clf()
    plt.matshow(heatmap1, cmap=plt.cm.hot_r)
    plt.colorbar()
    ylab = np.arange(ad_cats_table.shape[0])
    labels = [x.split('_')[0] for x in ad_cats_table.index]
    plt.xticks(ylab, labels, rotation='vertical', verticalalignment='bottom')
    plt.yticks(ylab, labels)
    plt.subplots_adjust(bottom=0.5,left=0.5)
    plt.savefig('chi2.png', dpi=240)
    plt.clf()
    plt.matshow(heatmap2, cmap=plt.cm.hot_r)
    plt.colorbar()
    plt.xticks(ylab, labels, rotation='vertical', verticalalignment='bottom')
    plt.yticks(ylab, labels)
    plt.savefig('chi2_norem.png', dpi=240)
    plt.clf()

    plt.matshow(ad_cats_corr, cmap=plt.cm.hot_r)
    plt.colorbar()
    plt.xticks(ylab, labels, rotation='vertical', verticalalignment='bottom')
    plt.yticks(ylab, labels)
    plt.subplots_adjust(bottom=0.5,left=0.5)
    plt.savefig('corr.png', dpi=240)
    plt.clf()
    plt.matshow(ad_cats_corr_no_rem, cmap=plt.cm.hot_r)
    plt.colorbar()
    plt.xticks(ylab, labels, rotation='vertical', verticalalignment='bottom')
    plt.yticks(ylab, labels)
    plt.subplots_adjust(bottom=0.5,left=0.5)
    plt.savefig('corr_norem.png', dpi=240)
    plt.clf()
