#!/usr/bin/env python3

import re

def get_args():
    import argparse
    parser = argparse.ArgumentParser(
        description='Parse ebay kleinanzeigen car search result and extract price information',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--url', help='The initial search url. ')
    args = parser.parse_args()
    return args


def search_by_regexp(regexp, iterator):
    for item in iterator:
        r = regexp.search(item)
        if r:
            yield r.group(1)


def get_results(url):
    import mechanicalsoup
    re_year = re.compile("(\d{4})")
    re_km = re.compile("([.\d]+) km")

    browser = mechanicalsoup.StatefulBrowser()
    results = []

    page = browser.open(url)
    while page:
        for el in page.soup.select('article.aditem'):
            tags = [v.text.strip() for v in el.select('.text-module-end span')]
            addetails = el.select('.aditem-details')[0]
            price = re.sub(r"[^\d]", '', addetails.select('strong')[0].text.strip())
            item = {
                'name': el.select('.text-module-begin a')[0].text.strip().replace(',',' '),
                'price': price,
                'km': next(search_by_regexp(re_km, tags), None),
                'year': next(search_by_regexp(re_year, tags), None),
            }
            results.append(item)

        next_page = page.soup.select('a.pagination-next')
        if next_page:
            page = browser.follow_link(next_page[0])
        else:
            page = None
    return results


if __name__ == '__main__':
    args = get_args()
    results = get_results(args.url)
    for result in results:
        if result['km'] and result['year']:
            print("\"{name}\",{km},{year},{price}".format(**result))
