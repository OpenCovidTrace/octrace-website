import os.path
import datetime
import math

from copy import deepcopy
from itertools import chain
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
import logging

from pelican import signals, generators, contents, readers
from pelican.utils import process_translations, slugify

from fetchers import who as who_news

logger = logging.getLogger(__name__)


class DictReader(readers.BaseReader):
    enabled = True
    file_extensions = ['data']

    def read(self, fpath, data=None):
        pass


class NewsGenerator(generators.CachingGenerator):
    def __init__(self, *args, **kwargs):
        self.pages = []
        super(NewsGenerator, self).__init__(*args, **kwargs)
        signals.article_generator_init.send(self)

    def get_template(self, name):
        if name == 'news_list':
            return super(NewsGenerator, self).get_template(name)
        return super(NewsGenerator, self).get_template('news')

    def generate_context(self):
        all_pages = []
        limit = 20
        urls = []
        num = 0
        news = [i for i in who_news.get_feeds() if i['date'] and i['title'] ]
        news.sort( key=lambda i: i['date'], reverse=True )
        page_num = 0
        pages = math.ceil(len(news) / limit)
        for article in news:
            article['date_str'] = ''
            if article['date']:
                article['date_str'] = datetime.date.strftime(
                    article['date'], '%d %b %Y'
                )
            try:
                fpath = os.path.join(
                    'news',
                    slugify('{}-{}-{}'.format(
                        article['date_str'][:20], article['title'][:50], num
                    )) + '.html'
                )
            except UnicodeEncodeError:
                logger.info('Could not encode airline')
                continue
            num += 1
            metadata = {
                'title': article['title'],
                'article': article,
                'save_as': fpath
            }
            page = contents.Page(
                deepcopy(article), metadata=metadata
            )
            article['url'] = fpath
            all_pages.append(page)
            urls.append(article)
            if len(urls) >= limit:
                page_num += 1
                url = 'newsroom.html' if page_num == 1 else f'newsroom-{page_num}.html'
                all_pages.append(contents.Page(
                    {'urls': urls},
                    metadata={
                        'title': 'News list',
                        'save_as': url,
                        'template': 'news_list',
                        'urls': urls,
                        'pages_num': page_num,
                        'pages': pages
                    }
                ))
                urls = []
        if urls:
            page_num += 1
            url = 'newsroom.html' if page_num == 1 else f'newsroom-{page_num}.html'
            all_pages.append(contents.Page(
                {'urls': urls},
                metadata={
                    'title': 'News list',
                    'save_as': url,
                    'template': 'news_list',
                    'urls': urls,
                    'pages_num': page_num,
                    'pages': pages
                }
            ))
        self.pages, self.translations = process_translations(
            all_pages,
        )
        signals.page_generator_finalized.send(self)

    def generate_output(self, writer):
        for page in chain(self.translations, self.pages):
            writer.write_file(
                page.save_as, self.get_template(page.template),
                self.context, page=page,
                relative_urls=self.settings['RELATIVE_URLS'],
            )
        signals.article_writer_finalized.send(self, writer=writer)


def get_generators(pelican_object):
    return NewsGenerator


def register():
    signals.get_generators.connect(get_generators)
