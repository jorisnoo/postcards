#!/usr/bin/env python
# encoding: utf-8

from postcards import Postcards
import urllib
from util.random_search_term.random_search_term import get_random_search_term
from bs4 import BeautifulSoup
import json
import urllib.request, urllib.error, urllib.parse
import random
import sys


class PostcardsBingRandom(Postcards):
    """
    Get an arbitrary picture from the internet as postcard image.
    Note: image content may be inappropriate
    """

    def get_img_and_text(self, plugin_config, cli_args):
        found = False
        counter = 0

        imgs = []
        while not found and counter < 10:
            keyword = self._get_search_term()
            self.logger.debug('using keyword=' + keyword)

            imgs = self._fetch_img_urls(keyword)
            random.shuffle(imgs)
            self.logger.trace(imgs)
            self.logger.debug('fetched {} images'.format(len(imgs)))

            counter += 1
            if len(imgs) > 0:
                found = True

        if not found:
            self.logger.error('no images found although {} times tried'.format(counter))
            exit(1)

        img = random.choice(imgs)[2]
        self.logger.info('choosing image {}'.format(img))

        return {
            'img': img,
            'text': ''
        }

    def _get_search_term(self):
        try:
            return get_random_search_term()
        except Exception as e:
            self.logger.error('something broke with the generated python code')
            raise e

    def _get_bing_url(self, keyword, adult_content=True, large_size=True):
        if large_size:
            keyword += '+filterui:imagesize-large'

        url = "http://www.bing.com/images/search?q=" + keyword + "&FORM=HDRSC2"

        if adult_content:
            url += '&adlt=off'

        return url

    def _fetch_img_urls(self, keyword):
        # bing img search, https://gist.github.com/stephenhouser/c5e2b921c3770ed47eb3b75efbc94799

        url = self._get_bing_url(keyword)
        self.logger.debug('search url {}'.format(url))

        header = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/43.0.2357.134 Safari/537.36"}

        soup = BeautifulSoup(urllib.request.urlopen(urllib.request.Request(url, headers=header)), 'html.parser')
        imgs = []  # contains the link for Large original images, type of  image
        for a in soup.find_all("a", {"class": "iusc"}):
            mad = json.loads(a["mad"])
            turl = mad["turl"]
            m = json.loads(a["m"])
            murl = m["murl"]

            image_name = urllib.parse.urlsplit(murl).path.split("/")[-1]
            imgs.append((image_name, turl, murl))

        return imgs


if __name__ == '__main__':
    PostcardsBingRandom().main(sys.argv[1:])
