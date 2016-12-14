import scrapy

class AlexaSpider(scrapy.Spider):
    name = 'alexa'
    start_urls = ['http://www.alexa.com/topsites/category']

    # store the top 500 links associated with each Alexa category
    name_links_dict = {}

    def parse(self, response):
        for categories in response.css('ul.subcategories'):
            for link in categories.css('li'):
                link_url = link.css('a::attr("href")').extract_first()
                link_name = link.css('a::text').extract_first()
                next_page = response.urljoin(link_url)
                r = scrapy.http.Request(next_page, callback=
                        self.parse_webpage_list)
                r.meta['link'] = link_url
                r.meta['name'] = link_name
                r.meta['depth'] = 1
                r.meta['subcategories'] = True
                yield r

    def parse_webpage_list(self, response):
        """
        parses something like http://www.alexa.com/topsites/category/Top/Health
        """
        links = []
        for site in response.css('li.site-listing'):
            link = site.css('p.desc-paragraph a::text').extract_first()
            links.append(link)
        page = response.css('div.alexa-pagination')
        b = page.css('b::text').extract_first()
        page_num = int(b)/25
        next_link = response.css('a.next::attr("href")').extract_first()
        yield {'name': response.meta['name'], 'page_num': page_num, 'links': links}
        r = scrapy.Request(response.urljoin(next_link), callback=self.parse_webpage_list)
        r.meta['link'] = response.meta['link']
        r.meta['name'] = response.meta['name']
        r.meta['depth'] = response.meta['depth']
        r.meta['subcategories'] = False
        yield r
        if response.meta['subcategories']:
            subcategories = response.css('ul.subcategories li')
            for category in subcategories:
                url = category.css('a::attr("href")').extract_first()
                category_name = category.css('a::text').extract_first()
                r = scrapy.Request(response.urljoin(url), callback=self.parse_webpage_list)
                r.meta['link'] = url
                r.meta['name'] = response.meta['name'] + '-' + category_name
                r.meta['depth'] = response.meta['depth'] + 1
                r.meta['subcategories'] = False
                yield r
