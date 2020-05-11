import re
import logging as logger
import requests
import lxml.html
import lxml.html.html5parser
import lxml.etree
import json
import os
import dateparser
from lxml.cssselect import CSSSelector
from requests.exceptions import HTTPError
from urllib.parse import urljoin
import datetime


logger.basicConfig(level=logger.INFO)
CACHE_RESULTS_HOURS = 4
CACHE_PATH  = 'fetchers/cache'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


def _selector(dom, selector):
    selector = selector.lower().replace('>', ' > ')
    sel = CSSSelector(selector)
    nodes = sel(dom)
    # tbody fix, html5 browser use tbody node, but html may not have it
    # trying without tbody if selector contains it and nothing found
    if not nodes and 'tbody' in selector:
        # remove smth like tbody#jkajks.casdsad:nth-of-type(1)
        selector = re.sub(r'tbody\S* > ', '', selector)
        sel = CSSSelector(selector)
        nodes = sel(dom)
    return nodes


def get_html_by_selector(dom, selector, filter_html=True):
    nodes = _selector(dom, selector)
    if not nodes:
        return None
    return _etree_to_html(nodes[0], filter_html=filter_html)


def get_text_by_selector(dom, selector):
    nodes = _selector(dom, selector)
    if not nodes:
        return None
    return _etree_to_text(nodes[0]).strip()


def get_attr_by_selector(dom, selector, attr):
    nodes = _selector(dom, selector)
    if not nodes:
        return None
    return nodes[0].attrib.get(attr)


def _etree_to_html(node, filter_html=True):
    # links = selector(node, 'a[href]')
    # for link in links:
    #     link.attrib['href'] = urljoin()
    html = lxml.html.tostring(node,
        encoding='unicode',
        method='html',
        pretty_print=True
    )
    if filter_html:
        return _filter_html(html)
    return html


def _filter_html(html):
    html = re.sub(r'<(style|script|head)(>|\s[^>]*>).*?<\/\\1>', '',
                  html, flags=(re.S | re.I))
    good_tags = (
        'b', 'strong', 'img', 'a',
        'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'br', 'div', 'tr', 'table', 'body', 'td'
    )
    good_attributes = ('href', 'src')

    result = []
    for part in re.split(r'(<\/?\!?\w+[^>]*>)', html, flags=(re.I | re.S)):
        r = re.match(r'^<(\/?)\!?(\w+)(.*)>', part)
        if not r:
            result.append(part)
            continue
        is_close = True if r.group(1) else False
        tag = r.group(2)
        attrs = r.group(3)
        if tag not in good_tags:
            continue
        if is_close:
            result.append(part)
            continue
        filtered_tag = f'<{tag}'
        if attrs:
            logger.debug(f'filter_html: {attrs} in tag {tag}')
            for a in re.findall(r'([\w\:\-]+\s*(?:=[\'\"].*?[\'\"])?)', attrs, flags=(re.I | re.S)):
                r = re.match(r'([\w\:\-]+)', a)
                attr_name = r.group(1)
                if attr_name in good_attributes:
                    filtered_tag += f' {a}'
                else:
                    logger.debug(f'filter_html: {attr_name} is not white list ({a})')
        filtered_tag += '>'
        result.append(filtered_tag)
    return ''.join(result)


def _etree_to_text(node):
    return lxml.etree.tostring(node, method='text', encoding='unicode')


def get_url_dom(url, cache=True):
    if not os.path.exists(CACHE_PATH):
        os.makedirs(CACHE_PATH)
    cache_file = os.path.join(
        CACHE_PATH,
         '{}.json'.format(re.sub(r'[^\w\d\-\.]+', '', url))
    )
    data = None
    cache_valid = False
    unow = datetime.datetime.utcnow()
    if cache:
        try:
            with open(cache_file , 'r') as file:
                data = json.load(file)
        except (IOError, json.decoder.JSONDecodeError):
            pass
    if data and data.get('updated'):
        cache_valid = True
        updated = datetime.datetime.strptime(data['updated'], DATETIME_FORMAT)
        if unow - updated > datetime.timedelta(hours=CACHE_RESULTS_HOURS):
            cache_valid = False

    if not cache_valid:
        logger.info(f'Request url {url}')
        r = requests.get(url)
        r.raise_for_status()
        try:
            with open(cache_file, 'w') as file:
                file.write(json.dumps({
                    'results': r.text,
                    'updated': datetime.datetime.strftime(unow, DATETIME_FORMAT)
                }))
        except IOError:
            logger.warning('Can not save cache')
        data = r.text
    else:
        logger.info(f'Got from cache {url}')
        data = data['results']

    dom = lxml.html.html5parser.document_fromstring(data)
    lxml.html.xhtml_to_html(dom)
    # todo
    # lxml.html.make_links_absolute()
    lxml.etree.cleanup_namespaces(dom)
    return dom


def get_feed_content(feed):
    url = feed['url']
    logger.info(f'Get feed content {url}')
    dom = get_url_dom(url)

    result = []
    items = _selector(dom, feed['item_selector'])
    last_date = datetime.date.today()
    for item in items:
        res = {
            'content': _etree_to_html(item),
            'source': feed.get('source'),
            'source_pic': feed.get('source_pic'),
        }
        logger.info('got new item')
        if feed.get('link'):
            link = get_attr_by_selector(item, feed['link'], 'href')
            if link:
                res['source_url'] = urljoin(url, link)
        if feed.get('date'):
            date_str = get_text_by_selector(item, feed['date'])
            date = None
            if date_str:
                date = dateparser.parse(date_str)
            if date:
                date = date.date()
                last_date = date
            else:
                date = last_date
            res['date'] = date
        if feed.get('title'):
            res['title'] = get_text_by_selector(item, feed['title'])
        if feed.get('picture_preview'):
            pic = get_attr_by_selector(
                item, feed['picture_preview'], feed.get('picture_preview_attr', 'src')
            )
            if pic:
                pic = re.sub(r'^.*url\([\'\"](.*?)[\'\"]\).*$', '\\1', pic)
                res['picture_preview'] = urljoin(url, pic)
        if feed.get('full_selector') and res.get('source_url'):
            url = res['source_url']
            logger.info(f'Fetching subitem content by url {url} ()')
            subdom = None
            try:
                subdom = get_url_dom(url)
            except (requests.HTTPError) as err:
                logger.warning(f'Error while get url {url}: {err}')
            if len(subdom):
                res['content'] = get_html_by_selector(subdom, feed['full_selector'])
                if feed.get('picture_big'):
                    pic = get_attr_by_selector(
                        subdom, feed['picture_big'], feed.get('picture_big_attr', 'src')
                    )
                    if pic:
                        res['picture_big'] = urljoin(url, pic)
        else:
            res['source_url'] = url

        result.append(res)
    return result

