import json

from automation import TaskManager, CommandSequence

# load sites from alexa crawl
with open('alexa.json') as f:
    data = json.load(f)
categories = set([x['name'] for x in data])
category_sites = {}
for sites in data:
    c = sites['name']
    # only take the top 100 sites
    if sites['page_num']>5:
        continue
    if c in category_sites:
        category_sites[c] += sites['links']
    else:
        category_sites[c] = sites['links']

# actually do the crawl
categories.remove('Adult')
categories = list(categories)
print categories
print category_sites
f = open('categories.txt', 'w')
f.write('\n'.join(categories))

# The list of sites that we wish to crawl
NUM_BROWSERS = 1
manager_params, browser_params = TaskManager.load_default_params(NUM_BROWSERS)

# set up the browser...
# Loads the manager preference and 3 copies of the default browser dictionaries
for i in xrange(NUM_BROWSERS):
    browser_params[i]['disable_flash'] = False #Enable flash for all three browsers
    browser_params[i]['headless'] = True #Launch only browser 0 headless
    browser_params[i]['save_javascript'] = True
    browser_params[i]['profile_archive_dir'] = './profile_{0}'.format(i)

# Update browser configuration (use this for per-browser settings)
# Update TaskManager configuration (use this for crawl-wide settings)
manager_params['data_directory'] = './crawl_data_2'
manager_params['log_directory'] = './crawl_data_2'


# Instantiates the measurement platform
# Commands time out by default after 60 seconds


i = 0
for category in categories:
    #if categories=='Recreation' or categories=='Computers':
    #    continue
    sites = category_sites[category]
    if category in set(['Recreation', 'Computers', 'Shopping']):
        continue
    f.write('{0}, {1}'.format(i, category))
    manager_params['data_directory'] = './{0}_data'.format(category)
    manager_params['database_name'] = 'crawl-data.sqlite'
    manager_params['log_file'] = 'openwpm.log'
    browser_params[0]['profile_archive_dir'] = './{0}_profile'.format(category)
    browser_params[0]['profile_tar'] = None
    manager = TaskManager.TaskManager(manager_params, browser_params)
    for site in sites:
        try:
            site = site.lower()
            if not site.startswith('http'):
                site = 'http://'+site
            command_sequence = CommandSequence.CommandSequence(site, reset=False)
            # Start by visiting the page
            command_sequence.get(sleep=0, timeout=60)
            command_sequence.dump_page_source(site.split('/')[2], timeout=60)
            # dump_profile_cookies/dump_flash_cookies closes the current tab.
            command_sequence.dump_profile_cookies(120)
            command_sequence.dump_profile(category)
            # execute on the ith browser
            manager.execute_command_sequence(command_sequence, index=0)
        except:
            print 'failed on site: ' + site
            pass
    manager.close()
    i+=1



manager.close()
# Shuts down the browsers and waits for the data to finish logging
