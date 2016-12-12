import json

from automation import TaskManager, CommandSequence

# The list of sites that we wish to crawl
NUM_BROWSERS = 15
manager_params, browser_params = TaskManager.load_default_params(NUM_BROWSERS)

# set up the browser...
# Loads the manager preference and 3 copies of the default browser dictionaries
for i in xrange(NUM_BROWSERS):
    browser_params[i]['disable_flash'] = False #Enable flash for all three browsers
    browser_params[i]['headless'] = True #Launch only browser 0 headless
    browser_params[i]['profile_archive_dir'] = './profile_{0}'.format(i) #Launch only browser 0 headless

# Update browser configuration (use this for per-browser settings)
# Update TaskManager configuration (use this for crawl-wide settings)
manager_params['data_directory'] = './crawl_data'
manager_params['log_directory'] = './crawl_data'
manager_params['log_directory'] = './crawl_data'


# Instantiates the measurement platform
# Commands time out by default after 60 seconds
manager = TaskManager.TaskManager(manager_params, browser_params)


# load sites from alexa crawl
with open('alexa.json') as f:
    data = json.load(f)
categories = set([x['name'] for x in data])
category_sites = {}
for sites in data:
    c = sites['name']
    if c in category_sites:
        category_sites[c] += sites['links']
    else:
        category_sites[c] = sites['links']



# actually do the crawl
categories.remove('Adult')
categories = list(categories)
with open('categories.txt', 'w') as f:
    f.write('\n'.join(categories))
i = 0
for category in categories:
    sites = category_sites[category]
    print i, category
    for site in sites:
        site = site.lower()
        if not site.startswith('http'):
            site = 'http://'+site
        command_sequence = CommandSequence.CommandSequence(site, reset=False)
        # Start by visiting the page
        command_sequence.get(sleep=0, timeout=60)
        command_sequence.dump_page_source(site, timeout=60)
        # dump_profile_cookies/dump_flash_cookies closes the current tab.
        command_sequence.dump_profile_cookies(120)
        manager.execute_command_sequence(command_sequence, index='i') # ** = synchronized browsers
    i+=1


# Shuts down the browsers and waits for the data to finish logging
manager.close()
