import os
import pickle
import random

from automation import TaskManager, CommandSequence
from automation.SocketInterface import clientsocket

from text_extractor import process_url

def get_iframes(site, save_dir, **kwargs):
    """
    Extracts all the data from the iframes on the page.
    """
    driver = kwargs['driver']
    iframe_elements = driver.find_elements_by_tag_name('iframe')
    ad_contents = []
    for i, e in enumerate(iframe_elements):
        driver.switch_to.frame(e)
        el = driver.find_element_by_xpath('html/body')
        data = el.get_attribute('innerHTML')
        with open(save_dir + '/' + site.split('/')[2] + '-iframes.txt', 'a') as f:
            f.write('<potential-ad-iframe>\n\n')
            f.write(data)
            f.write('</potential-ad-iframe>\n\n')
        ad_contents.append(data)
        driver.switch_to.default_content()
    #sock = clientsocket()
    #table_name = 'iframes'
    #manager_params = kwargs['manager_params']
    #print manager_params['aggregator_address']
    #sock.connect(manager_params['aggregator_address'][0], manager_params['aggregator_address'][1])
    #query = ("CREATE TABLE IF NOT EXISTS %s ("
    #                    "top_url TEXT, link TEXT);" % table_name)
    #sock.send((query, ()))
    #current_url = driver.current_url
    #for content in ad_contents:
    #    query = ("INSERT INTO %s (top_url, link) "
    #                 "VALUES (?, ?)" % table_name)
    #    sock.send((query, (current_url, content)))
    #    sock.close()


if __name__=='__main__':
    category_sites = pickle.load(open('category_sites.pkl'))
    site_categories = pickle.load(open('site_categories.pkl'))
    NUM_BROWSERS = 1
    manager_params, browser_params = TaskManager.load_default_params(NUM_BROWSERS)
    browser_params[0]['headless'] = True
    browser_params[0]['save_javascript'] = True
    profiles = [None, './Health_profile',
            './News_profile',
            './Kids and Teens_profile',
            './Shopping_profile',
            './Sports_profile',
            './Science_profile',
            './Reference_profile']
    # ad category
    sites = category_sites['News'][:25]
    #sites = ['http://www.accuweather.com','http://www.localconditions.com',
    #        'http://www.wunderground.com',
    #        'http://www.myforecast.com', 'http://www.weatherbase.com']

    # load one of the existing built profiles
    # do this ten times for repeatability?
    for profile in profiles:
        if profile:
            profile_name = profile.split('_')[0].split('/')[1]
        else:
            profile_name = 'None'
        try:
            os.mkdir('{0}_News'.format(profile_name))
        except:
            pass
        for i in range(10):
            random.shuffle(sites)
            browser_params[0]['profile_tar'] = profile
            manager_params['data_directory'] = 'ads'
            manager_params['log_directory'] = 'ads'
            manager_params['database_name'] = 'crawl-data.sqlite'
            manager_params['log_file'] = 'openwpm.log'
            manager = TaskManager.TaskManager(manager_params, browser_params)
            for site in sites:
                try:
                    site = site.lower()
                    if not site.startswith('http'):
                        site = 'http://'+site
                    command_sequence = CommandSequence.CommandSequence(site, reset=False)
                    command_sequence.get(sleep=0, timeout=60)
                    command_sequence.run_custom_function(get_iframes, (site, './{0}_News'.format(profile_name)))
                    manager.execute_command_sequence(command_sequence, index=0)
                except:
                    print 'failed on site'
                    manager.close()
                    exit(1)
            manager.close()

