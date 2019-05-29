import urllib.request
from bs4 import BeautifulSoup
import re

# Get Links of cities in www.pararius.com


def get_pariarius_city_links():
    main_page = 'https://www.pararius.com/english'

    main_page_html = urllib.request.urlopen(main_page)

    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')

    city_list = main_page_soup.find(
        'div', attrs={'class': 'location-list-container'})

    city_links = []
    for each in city_list.findAll('li'):
        city_links.append(each.find('a').get('href'))

    return city_links

# Get all apartments in a given city
# Input is the link to the cities page
# Returns a list containing links to the apartments


def get_apartment_list(main_page):
    main_page_html = urllib.request.urlopen(main_page)

    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')

    search_results = main_page_soup.find(
        'div', attrs={'class': 'search-results-wrapper'})
    property_list = []
    for each in search_results.findAll('div', attrs={'class': 'details'}):
        # property_list.append(each.find('a').get('href'))
        property_list.append(
            "https://www.pararius.com{}".format(each.find('a').get('href')))

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
    details_dict['link'] = main_page
    for each in details.findAll('dt'):
        if each.text == 'Square meters':
            details_dict['square_meters'] = each.find_next_sibling().text

        if each.text == 'Rent per month':
            details_dict['rent_per_month'] = each.find_next_sibling().text

    return details_dict


