import re
import pickle
import glob
import os

from text_extractor import URL_RE, process_url

def extract_ad_urls(base_dir, site_categories):
    """
    Dumps ad urls and categories into two pickes
    """
    iframe_links = glob.glob(base_dir+'/'+'*-iframe*')
    # dict of sites to all urls contained in iframes in that site.
    site_links = {}
    for site in iframe_links:
        site_name = site.split('iframe')[0][:-1]
        site_name = site_name.split('/')[1]
        print site_name
        site_links[site_name] = []
        with open(site) as f:
            site_data = f.readlines()
            iframes = []
            iframe = ''
            for line in site_data:
                line = line.strip()
                if line.endswith('</potential-ad-iframe>'):
                    iframe += line
                    iframes.append(iframe)
                elif line.startswith('<potential-ad-iframe>'):
                    iframe = ''
                    iframe += line
                else:
                    iframe += line
            # each iframe can only contain one landing page of a given url...
            for iframe in iframes:
                m = re.findall(URL_RE, iframe)
                links = set()
                for link in m:
                    #if '.com' in link or '.net' in m:
                        links.add(link)
                        links.add('.'.join(link.split('.')[-2:]))
                site_links[site_name].extend(links)
    with open(base_dir+'ad_site_links.pkl', 'w') as f:
        pickle.dump(site_links, f)
    site_link_categories = {}
    for site, links in site_links.iteritems():
        site = site.split('/')[-1]
        site_link_categories[site] = []
        for link in links:
            if link not in site and site not in link and 'facebook' not in link and 'youtube' not in link and 'google' not in link and 'twitter' not in link and 'yahoo' not in link:
                try:
                    category = site_categories[link]
                    site_link_categories[site].append((link, category))
                except:
                    pass
    with open(base_dir+'ad_site_cats.pkl', 'w') as f:
        pickle.dump(site_link_categories, f)

if __name__=='__main__':
    base_dirs = ['Health_News', 'None_News', 'Kids and Teens_news', 'Shopping_News', 'Sports_News', 'Science_News', 'Reference_News', 'News_News']
    site_categories = pickle.load(open('site_categories.pkl'))
    for b in base_dirs:
        extract_ad_urls(b, site_categories)
