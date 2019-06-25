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
        return BeautifulSoup(response.content, 'html.parser')
    except Exception as x:
        print('It failed :(', x.__class__.__name__)
    else:
        print('It eventually worked', response.status_code)


# get the link to cities
# returns a dictionary containing  lists of links and city names


def get_realo_city_links():
    main_page = 'https://www.realo.be/en'
    main_page_soup = make_request(main_page)
    city_houses_for_sale = []
    city_houses_for_rent = []
    for each in main_page_soup.findAll(
        'li', attrs={
            'data-id': 'listContainer'}):
        if each.div.string.strip() == 'Houses for sale':
            for x in each.ul.findAll('li'):
                city_houses_for_sale.append(
                    ['https://www.realo.be{}'.format(x.a['href']), x.text.strip()])

        elif each.div.string.strip() == 'Houses to rent':
            for x in each.ul.findAll('li'):
                city_houses_for_rent.append(
                    ['https://www.realo.be{}'.format(x.a['href']), x.text.strip()])

    return {'sale': city_houses_for_sale, 'rent': city_houses_for_rent}
# Get all apartments in a given city
# Input is the link to the cities page
# Returns a list containing links to the apartments


def get_listing_links_list(link):
    main_page_soup = make_request(link)

    results_list = []
    for each in main_page_soup.findAll(
        'li', attrs={
            'data-id': 'componentEstateListGridItem'}):
        if each.div.div.a:
            link = 'https://www.realo.be{}'.format(each.div.div.a['href'])
            link.strip()
            results_list.append(link)

    return results_list

# Function that gets the property info
# Takes the property link as input
# Returns a dict containing the square meters, Rent per month and link to
# property


def get_apartment_info(link):
    main_page_soup = make_request(link)

    if link is not None:
        try:
            habitable_area = main_page_soup.find(
                'div', attrs={
                    'class': 'component-property-features'}).div.table.tbody.findAll('tr')[3].findAll('td')[1].text
            habitable_area = int(habitable_area.replace('m2', ''))
            price = main_page_soup.find('li',
                                        attrs={'class': 'col module module-price'}).find('div',
                                                                                         attrs={'class': 'value'}).text.split(' ')[1].strip()
            price = int((re.sub(r'[^0-9\.]', '', price)).replace('.', ''))
            return {
                'price': price,
                'habitable_area': habitable_area,
                'link': link}
        except Exception as e:
            print('Type error: ' + str(e))
            print(traceback.format_exc())
            print('Link Not Valid')
            return None


def main():
    csv_columns = ['city', 'link', 'habitable_area', 'price']
    sale_csv_file = 'Realo_sale.csv'
    rent_csv_file = 'Realo_rent.csv'

    try:
        with open(sale_csv_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=csv_columns)
            writer.writeheader()
            for each in get_realo_city_links()['sale']:
                for i in [x for x in get_listing_links_list(each[0])]:
                    if get_apartment_info(i) is not None:
                        data = get_apartment_info(i)
                        data['city'] = each[1]
                        print(data)
                        writer.writerow(data)
        with open(rent_csv_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=csv_columns)
            writer.writeheader()
            for each in get_realo_city_links()['rent']:
                for i in [x for x in get_listing_links_list(each[0])]:
                    if get_apartment_info(i) is not None:
                        data = get_apartment_info(i)
                        data['city'] = each[1]
                        print(data)
                        writer.writerow(data)

    except Exception as e:
        logger.info('Type error: ' + str(e))
        logger.info(traceback.format_exc())
    #         # time.sleep(2)


if __name__ == '__main__':
    main()

