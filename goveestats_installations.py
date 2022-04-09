# Copyright (c) 2021 Florian Lagg
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import scrapy
import json
import datetime
import re

class GoveestatsInstallationsSpider(scrapy.Spider):
    name = 'goveestats-installations'
    #allowed_domains = ['analytics.home-assistant.io']
    start_urls = ['https://analytics.home-assistant.io/custom_integrations.json']

    def parse(self, response):

        jsonresponse = json.loads(response.body)

        line = jsonresponse['govee']
        keys = set(line['versions'])
        # somehow there is a version "1.0" - this isn't from us, we use x.x.x as version format.
        for key in keys:
            if not re.match('^\d+\.\d+\.\d+$', key):
                del line['versions'][key]
            elif key.startswith("1."):
                # for now we do not have an 1.x version, but some other "govee" custom component does
                del line['versions'][key]

        return {
            'timestamp': datetime.datetime.now(datetime.timezone.utc),
            'installations': line
        }
