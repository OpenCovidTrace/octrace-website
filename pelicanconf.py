#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import sys
import os
import datetime
from collections import OrderedDict

sys.path.append(os.curdir)
from fetchers import get_stats as ecdc_stats


ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

AUTHOR = 'OpenCovidTrace'
SITENAME = 'opencovidtrace.org'
SITEURL = 'https://opencovidtrace.org'
PATH = 'content'

TIMEZONE = 'Asia/Nicosia'

DEFAULT_LANG = 'en'
THEME = 'theme'
CURRENT_YEAR    = datetime.datetime.now().year
SLUGIFY_SOURCE = 'title'

GOOGLE_ANALYTICS = None
YANDEX_ANALYTICS = None

COVID_STATS = ecdc_stats.get_stats()

DIRECT_TEMPLATES = []
STATIC_PATHS = [
    'images', 'extra/favicon.ico',
    'extra/android-chrome-192x192.png',
    'extra/android-chrome-512x512.png',
    'extra/apple-touch-icon.png',
    'extra/browserconfig.xml',
    'extra/favicon-16x16.png',
    'extra/favicon-32x32.png',
    'extra/favicon.ico',
    'extra/mstile-144x144.png',
    'extra/mstile-150x150.png',
    'extra/mstile-310x150.png',
    'extra/mstile-310x310.png',
    'extra/mstile-70x70.png',
    'extra/robots.txt',
    'extra/safari-pinned-tab.svg',
    'extra/site.webmanifest',
    'extra/sitemap.xml'
]
EXTRA_PATH_METADATA = {
        k: {'path': k.split('/')[-1]} for k in STATIC_PATHS
    }

PLUGIN_PATHS = ['plugins']
PLUGINS = ['i18n_subsites', 'assets', 'news_generator', 'jinja2content']

# assets config
ASSET_CONFIG = (
        ('BABEL_BIN', os.path.join(
            ROOT_PATH, 'node_modules', '.bin', 'babel'
        )),
        ('CUSTOM_UGLIFYJS_BIN', os.path.join(
            ROOT_PATH, 'node_modules', '.bin', 'uglifyjs'
        )),
        ('CUSTOM_UGLIFYJS_OUTDIR', os.path.join(
            ROOT_PATH, 'output', 'theme', 'scripts'
        )),
        ('CUSTOM_UGLIFYJS_EXTRA_ARGS', [
            '--source-map',
            'url=packed.js.map,includeSources'
        ])
)

BASE_URL = '/'


# i18n
JINJA_ENVIRONMENT = {
        'extensions': ['jinja2.ext.i18n']
        }

JINJA_FILTERS = {}

LANG_SITEURLS = OrderedDict(
    [('en', '')]
)
LANG_NAMES = {
    'en': 'english'
}

I18N_SUBSITES = OrderedDict({})

I18N_TEMPLATES_LANG = None
I18N_GETTEXT_LOCALEDIR = 'theme/translations'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = None

# Social widget
SOCIAL = None

DEFAULT_PAGINATION = False

TAGS_SAVE_AS = ''
TAG_SAVE_AS = ''

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True
