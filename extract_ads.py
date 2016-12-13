import pickle

from automation import TaskManager, CommandSequence
from automation.SocketInterface import clientsocket

from text_extractor import process_url

def get_iframes(**kwargs):
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
        print str(data)
        ad_contents.append(data)
        driver.switch_to.default_content()
    sock = clientsocket()
    table_name = 'iframes'
    sock.connect(*manager_params['aggregator_address'])
    query = ("CREATE TABLE IF NOT EXISTS %s ("
                        "top_url TEXT, link TEXT);" % table_name)
    sock.send((query, ()))
    current_url = driver.current_url
    for content in ad_contents:
        query = ("INSERT INTO %s (top_url, link) "
                     "VALUES (?, ?)" % table_name)
        sock.send((query, (current_url, content)))
        sock.close()

if __name__=='__main__':
    category_sites = pickle.load(open('category_sites.pkl'))
    site_categories = pickle.load(open('site_categories.pkl'))
    NUM_BROWSERS = 1
    manager_params, browser_params = TaskManager.load_default_params(NUM_BROWSERS)
    browser_params[0]['headless'] = True
    browser_params[0]['save_javascript'] = True
    browser_params[0]['profile_tar'] = './Games_profile'
    # ad category
    sites = category_sites['Recreation'][:20]
    manager_params['data_directory'] = 'ads'
    manager_params['log_directory'] = 'ads'
    manager = TaskManager.TaskManager(manager_params, browser_params)
    # load one of the existing built profiles
    for site in sites:
        try:
            site = site.lower()
            if not site.startswith('http'):
                site = 'http://'+site
            command_sequence = CommandSequence.CommandSequence(site, reset=False)
            command_sequence.get(sleep=0, timeout=60)
            command_sequence.run_custom_function(get_iframes)
            manager.execute_command_sequence(command_sequence, index=0)
        except:
            print 'failed on site'
            manager.close()
            exit(1)
    manager.close()

