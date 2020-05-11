import json
import logging as logger
import re

from . import parselib

logger.basicConfig(level=logger.INFO)


def get_stats():
    dom = parselib.get_url_dom('https://www.ecdc.europa.eu/en/covid-19-pandemic')

    selectors = {
        'updated': '.field--name-field-pt-outbreak-components .field--item:nth-child(2) h2',
        'all_cases': '.color-red .field--name-field-pt-primary-data',
        'all_deaths': '.color-orange .field--name-field-pt-primary-data',
        'eu_cases': '.color-darkblue .field--name-field-pt-primary-data',
        'eu_deaths': '.color-orange .field--name-field-pt-secondary-data',
    }
    result = {
        k: parselib.get_text_by_selector(dom, v) for k, v in selectors.items()
    }
    result['eu_deaths'] = re.sub(r'.*?([\d\s]+ deaths).*', '\\1', result['eu_deaths'])
    result['updated'] = re.sub(r'Situation update ([^,]+).*', '\\1', result['updated'])
    return result


def main():
    logger.info(get_stats())


if __name__ == "__main__":
    main()