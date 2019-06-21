from urllib.request import Request, urlopen
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

# get the link to cities
# returns a dictionary containing  lists of links and city names


def get_realo_city_links():
    main_page = 'https://www.realo.be/en'
    req = Request(main_page, headers={'User-Agent': 'Mozilla/5.0'})
    main_page_html = urlopen(req).read()

    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')

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
    main_page = link

    req = Request(main_page, headers={'User-Agent': user_agent})
    main_page_html = urlopen(req).read()

    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')

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
    main_page = link

    s = requests.Session()
    s.headers.update({'x-test': 'true', 'User-Agent': user_agent})

    response = requests_retry_session(session=s).get(link)
    main_page_html = response.content
    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')

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
        print('Type error: ' + str(e))
        print(traceback.format_exc())
    #         # time.sleep(2)


if __name__ == '__main__':
    log_file = os.path.basename(__file__)
    logging.basicConfig(level=logging.INFO, filename=log_file)
    logger = logging.getLogger('scraper')
    logger.info('Scraper Started')
    print(log_file)
    main()
