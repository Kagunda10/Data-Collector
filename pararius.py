import urllib.request
from bs4 import BeautifulSoup
import re
import csv
import time
import logging
# Get Links of cities in www.pararius.com

logging.basicConfig(level = logging.INFO, filename = 'pararius_logs.txt')
logging = logging.getLogger('scraper')

def get_pariarius_city_links():
    main_page = 'https://www.pararius.com/english'

    main_page_html = urllib.request.urlopen(main_page)

    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')

    city_list = main_page_soup.find(
        'div', attrs={'class': 'location-list-container'})

    city_links = []
    for each in city_list.findAll('li'):
        link = each.find('a').get('href')
        city = each.text.split(" ")[3]
        city_links.append({"City": city, "Link": link})
        # time.sleep(2)

    return city_links

# Get all apartments in a given city
# Input is the link to the cities page
# Returns a list containing links to the apartments


def get_apartment_list(main_page):
    main_page_html = urllib.request.urlopen(main_page['Link'])

    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')

    search_results = main_page_soup.find(
        'div', attrs={'class': 'search-results-wrapper'})
    property_list = []
    for each in search_results.findAll('div', attrs={'class': 'details'}):
        # property_list.append(each.find('a').get('href'))
        property_list.append(
            "https://www.pararius.com{}".format(each.find('a').get('href')))
        # time.sleep(2)

    return property_list

# Function that gets the property info
# Takes the property link as input
# Returns a dict containing the square meters, Rent per month and link to
# property


def get_property_info(main_page):
    main_page_html = urllib.request.urlopen(main_page)

    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')

    details = main_page_soup.find('div', attrs={'class': 'details-container'})

    details_dict = {}
    details_dict['Link'] = main_page
    for each in details.findAll('dt'):
        if each.text == 'Square meters':
            details_dict['Living Area'] = each.find_next_sibling().text

        if each.text == 'Rent per month':
            details_dict['Rent(pm)'] = each.find_next_sibling().text
        # time.sleep(2)

    return details_dict


def main():
    csv_columns = ['City', 'Link', 'Living Area', 'Rent(pm)']
    csv_file = 'Pararius.csv'
    # Get city links
    logger.info('Scraper Started')
    try:
        with open(csv_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=csv_columns)
            writer.writeheader()
            for each_city in get_pariarius_city_links():
                for each in [x for x in [y for y in get_apartment_list(each_city)]]:
                    data = get_property_info(each)
                    data['City'] = each_city['City']
                    logger.info('Extracted: {}'.format(data['Link']))
                    writer.writerow(data)
    except IOError:
        print("I/O Error")
            # time.sleep(2)    

        # print([x for x in get_apartment_list(each_city)])
if __name__ == "__main__":
    # print(get_pariarius_city_links())
    main()
