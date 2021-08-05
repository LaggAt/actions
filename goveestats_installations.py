# Copyright (c) 2021 Florian Lagg
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import scrapy
import json
import datetime

class GoveestatsInstallationsSpider(scrapy.Spider):
    name = 'goveestats-installations'
    #allowed_domains = ['analytics.home-assistant.io']
    start_urls = ['https://analytics.home-assistant.io/custom_integrations.json']

    def parse(self, response):

        jsonresponse = json.loads(response.body_as_unicode())
        return {
            'timestamp': datetime.datetime.now(datetime.timezone.utc),
            'installations': jsonresponse['govee']
        }
