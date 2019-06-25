from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import csv
import traceback
import re
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem


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


# get the link to cities
# returns a list containing links to the cities


def get_zimmo_city_links():
    main_page = 'https://www.zimmo.be/nl/'
    req = Request(main_page, headers={'User-Agent': user_agent})
    main_page_html = urlopen(req).read()

    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')

    try:

        cities_link_sale = main_page_soup.find(
            'div', attrs={'class': 'col1 sitemap-block'})
        # print(cities_link_sale)
        cities_link_sale_list = []
        for each in cities_link_sale.findAll('li'):
            cities_link_sale_list.append(
                ['https://www.zimmo.be{}'.format(each.find('a').get('href')), each.text])

        # return cities_link_sale_list
        cities_link_rent = main_page_soup.find(
            'div', attrs={'class': 'col2 sitemap-block'})

        cities_link_rent_list = []
        for each in cities_link_sale.findAll('li'):
            cities_link_rent_list.append(
                ['https://www.zimmo.be{}'.format(each.find('a').get('href')), each.text])

        # return cities_link_rent_list

        return {'sale': cities_link_sale_list, 'rent': cities_link_rent_list}

    except (AttributeError, TypeError):
        print('Captcha Implemented')

# Get all apartments in a given city
# Input is the link to the cities page
# Returns a list containing links to the apartments


def get_zimmo_appartment_list(link):
    main_page = link
    req = Request(main_page, headers={'User-Agent': user_agent})
    main_page_html = urlopen(req).read()

    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')

    listing_links = []
    for each in main_page_soup.findAll('a',
                                       attrs={'class': 'property-item_link'}):
        listing_links.append('https://www.zimmo.be{}'.format(each.get('href')))
    return listing_links

# Get the number of pages oin the pagination
# Returns the number of pages in the resukt set


def get_no_of_pages(link):
    main_page = link
    req = Request(main_page, headers={'User-Agent': user_agent})
    main_page_html = urlopen(req).read()

    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')

    no_of_pages = main_page_soup.find(
        'ul', attrs={'class': 'dropdown-menu inner selectpicker'}).findAll('li')[-1].text

    return int(no_of_pages)
# Function that gets the property info
# Takes the property link as input
# Returns a dict containing the square meters, Rent per month and link to
# property


def get_listing_details(link):
    # To be done getting the living area
    main_page = link
    req = Request(main_page, headers={'User-Agent': user_agent})
    main_page_html = urlopen(req).read()

    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')
    try:

        price = main_page_soup.find('div',
                                    attrs={'class': 'price-value'}).find('span',
                                                                        attrs={'class',
                                                                                'feature-value'}).text.strip()
        price = int((re.sub(r'[^0-9\.]', '', price)).replace('.', ''))
        # return {'price': price}
        living_area = int(main_page_soup.find(
            'ul', attrs={
                'class': 'main-features'}).findAll('li')[3].span.text.strip().split()[0])
        if isinstance(price, int) and isinstance(living_area, int):
            return {'price': price, 'living_area': living_area}
    except Exception as e:
        print('Type error: ' + str(e))
        print(traceback.format_exc())

def main():
    csv_columns = ['city', 'link', 'living_area', 'price']
    sale_csv_file = 'zimmo_sale.csv'
    rent_csv_file = 'zimmo_rent.csv'

    try:
        with open(sale_csv_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=csv_columns)
            writer.writeheader()
            for each in get_zimmo_city_links()['sale']:
                if (get_no_of_pages(each[0])) > 0:
                    for i in range(get_no_of_pages(each[0])):
                        for i in [x for x in get_zimmo_appartment_list(each[0]+'?pagina={}'.format(i))]:
                            if get_listing_details(i) is not None:
                                data = get_listing_details(i)
                                if data:
                                    data['city'] = each[1]
                                    data['link'] = i
                                    print(data)
                                    writer.writerow(data)
        with open(rent_csv_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=csv_columns)
            writer.writeheader()
            for each in get_zimmo_city_links()['rent']:
                for i in [x for x in get_zimmo_appartment_list(each[0])]:
                    if get_listing_details(i) is not None:
                        data = get_listing_details(i)
                        data['city'] = each[1]
                        print(data)
                        writer.writerow(data)

    except Exception as e:
        print('Type error: ' + str(e))
        print(traceback.format_exc())
    #         # time.sleep(2)

if __name__ == '__main__':
    main()