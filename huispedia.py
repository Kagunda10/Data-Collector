from bs4 import BeautifulSoup
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import logging
import csv
import traceback
import re
import os
import time
import daiquiri
import sys
from lxml.html import fromstring

def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies

daiquiri.setup(level=logging.INFO, outputs=(
    daiquiri.output.Stream(sys.stdout),
    daiquiri.output.File("realo",
                         formatter=daiquiri.formatter.JSON_FORMATTER),
    ))

logger = daiquiri.getLogger(__name__, subsystem="example")

software_names = [SoftwareName.CHROME.value]
operating_systems = [
    OperatingSystem.WINDOWS.value,
    OperatingSystem.LINUX.value]

user_agent_rotator = UserAgent(
    software_names=software_names,
    operating_systems=operating_systems,
    limit=100)

# Get list of user agents.
user_agents = user_agent_rotator.get_user_agents()

# Get Random User Agent String.
user_agent = user_agent_rotator.get_random_user_agent()


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def make_request(link):
    t0 = time.time()
    try:
        response = requests_retry_session().get(
            link,
            headers={'User-Agent': user_agent}
        )
        logger.info('Parsing: {}'.format(link))
        return BeautifulSoup(response.content, 'html5lib')
    except Exception as x:
        print('It failed :(', x.__class__.__name__)
    else:
        print('It eventually worked', response.status_code)
# get the link to cities
# returns a list containing links to the cities


def get_huispedia_city_links():
    main_page = 'https://huispedia.nl/'

    main_page_soup = make_request(main_page)

    footer = main_page_soup.find('footer', attrs={'class': 'footer'})

    cities_div = footer.find('div', attrs={'class': 'd-none d-sm-block'})

    cities_list = cities_div.findAll('li')

    city_links = []
    city_names = []
    for each in cities_list:
        city_names.append(each.text)
        city_links.append(
            'https://huispedia.nl{}'.format(each.find('a').get('href')))
    return dict(zip(city_names, city_links))

# Get all apartments in a given city
# Input is the link to the cities page
# Returns a list containing links to the apartments


def get_apartment_list(link):
    main_page_soup = make_request(link)
    search_results = main_page_soup.find('ul', attrs={'id': 'resultlist'})

    property_list = []
    for each in search_results.findAll('li'):
        try:
            property_list.append('https://huispedia.nl/zoeken' + each.find('a').get('href'))
        except AttributeError as e:
            pass
    return property_list

# Get the number of pages oin the pagination
# Returns the number of pages in the resukt set


def get_no_of_pages(link):

    main_page_soup = make_request(link)

    pagination = main_page_soup.find('div', attrs={'id': 'pagination-wrapper'})

    page_list = pagination.findAll('li')

    no_of_pages = page_list[-2].find().attrs[u'data-id']

    return no_of_pages

def get_apartment_info(link):
    try:
        main_page_soup = make_request(link)
        price=main_page_soup.find('div', attrs={'class':'price-indication-main-container'}).span
        living_area = main_page_soup.find('div', attrs={
                                        'id': 'feature-big-woonoppervlak'}).find('div', attrs={'class': 'value'}).text

        return {'living_area': living_area, 'price': price}
    except AttributeError:
        logger.error("Attribute not found")

def main():
    csv_columns = ['city', 'link', 'habitable_area', 'price']
    sale_csv_file = 'huispedia.csv'
    try:
        with open(sale_csv_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=csv_columns)
            writer.writeheader()
            for k, v in get_huispedia_city_links().items():
                pages = int(get_no_of_pages(v))
                print(pages)
                if pages > 0:
                    for i in range(pages):
                        houses = get_apartment_list('{0}/op_termijn/default_sort/kze-otb-ovb_status/list_view//{1}_p'.format(v, i))
                        for each in houses:
                            print(each)
                            data = get_apartment_info(each)
                            data['city'] = k
                            data['link'] = each
                            writer.writerow(data)

    except Exception as e:
        logger.info('Type error: ' + str(e))
        logger.info(traceback.format_exc())
    #         # time.sleep(2)


# print(get_apartment_info('https://huispedia.nl/amsterdam/1018tn/plantage-muidergracht/75-b'))
# proxies = get_proxies()
# print(proxies)

if __name__ == "__main__":
    print(get_apartment_info('https://huispedia.nl/amsterdam/1033pc/nageljongenstraat/151'))
    