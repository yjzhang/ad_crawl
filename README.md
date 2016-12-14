Web crawling/ad analysis pipeline:

1. use scrapy with alexa.py to gather json data
2. use text_extractor.py to build a mapping from websites to categories
3. use gather.py to build a user profile by browsing sites in a category
4. use extract_ads.py to collect ads by browsing
5. use extract_landing_pages.py to parse the ad data, collecting only the landing page urls
6. use analysis.py
