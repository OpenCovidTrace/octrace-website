import json
import logging as logger
import datetime

from .parselib import get_feed_content

logger.basicConfig(level=logger.INFO)



FEED = [
    {
        'url': 'https://www.who.int/emergencies/diseases/novel-coronavirus-2019/events-as-they-happen',
        'source': 'WHO Events',
        'source_pic': '/images/ext-WHO.svg',
        'item_selector': '.highlight-widget--content, .sf-content-block',
        'date': 'h2+p',
        'title': 'h2',
        'link': None,
    },
    {
        'url': 'https://www.who.int/dg/speeches',
        'source': 'WHO Speeches',
        'source_pic': '/images/ext-WHO.svg',
        'item_selector': '.list-view--item.vertical-list-item',
        'date': '.date',
        'title': '.heading',
        'link': 'a',
        'full_selector': '.sf-detail-body-wrapper',
        # 'picture_big': '[data-image]',
        # 'picture_big_attr': 'data-image',
        'picture_preview': '[data-image]',
        'picture_preview_attr': 'data-image',
    },
    {
        'url': 'https://www.ecdc.europa.eu/en/search?s=&sort_by=field_ct_publication_date&sort_order=DESC&f%5B0%5D=diseases%3A2942',
        'source': 'ECDC',
        'source_pic': '/images/ext-ECDC.svg',
        'item_selector': 'article',
        'date': '.ct__meta-type-and-date .ct__meta__value',
        'title': '.ct__title',
        'link': 'a',
        'full_selector': '.region-content .text-image',
        'picture_preview': '.ct__image-container',
        'picture_preview_attr': 'style',
    },

]


def get_feeds():
    data = None
    results = []
    for feed in FEED:
        results += get_feed_content(feed)
    return results


def main():
    for content in get_feeds():
        logger.info(content)


if __name__ == "__main__":
    main()
