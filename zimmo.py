from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

# get the link to cities
# returns a list containing links to the cities


def get_zimmo_city_links():
    main_page = 'https://www.zimmo.be/nl/'
    req = Request(main_page, headers={'User-Agent': 'Mozilla/5.0'})
    main_page_html = urlopen(req).read()

    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')

    cities_link_sale = main_page_soup.find(
        'div', attrs={'class': 'col1 sitemap-block'})

    cities_link_sale_list = []
    for each in cities_link_sale.findAll('li'):
        cities_link_sale_list.append(
            'https://www.zimmo.be{}'.format(each.find('a').get('href')))

    # return cities_link_sale_list
    cities_link_rent = main_page_soup.find(
        'div', attrs={'class': 'col2 sitemap-block'})

    cities_link_rent_list = []
    for each in cities_link_sale.findAll('li'):
        cities_link_rent_list.append(
            'https://www.zimmo.be{}'.format(each.find('a').get('href')))
    # return cities_link_rent_list

    return {'sale': cities_link_sale_list, 'rent': cities_link_rent_list}

# Get all apartments in a given city
# Input is the link to the cities page
# Returns a list containing links to the apartments


def get_zimmo_appartment_list():
    main_page = 'https://www.zimmo.be/nl/antwerpen-2000/te-koop/'
    req = Request(main_page, headers={'User-Agent': 'Mozilla/5.0'})
    main_page_html = urlopen(req).read()

    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')

    listing_links = []
    for each in main_page_soup.findAll('a',
                                       attrs={'class': 'property-item_link'}):
        listing_links.append('https://www.zimmo.be{}'.format(each.get('href')))

    return listing_links

# Get the number of pages oin the pagination
# Returns the number of pages in the resukt set


def get_no_of_pages():
    main_page = 'https://www.zimmo.be/nl/antwerpen-2000/te-koop/'
    req = Request(main_page, headers={'User-Agent': 'Mozilla/5.0'})
    main_page_html = urlopen(req).read()

    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')

    no_of_pages = main_page_soup.find(
        'ul', attrs={'class': 'dropdown-menu inner selectpicker'}).findAll('li')[-1].text

    return no_of_pages
# Function that gets the property info
# Takes the property link as input
# Returns a dict containing the square meters, Rent per month and link to
# property


def get_listing_details():
    # To be done getting the living area
    main_page = 'https://www.zimmo.be/nl/antwerpen-2000/te-koop/nieuwbouwproject/1003HSE/'
    req = Request(main_page, headers={'User-Agent': 'Mozilla/5.0'})
    main_page_html = urlopen(req).read()

    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')

    price = main_page_soup.find('div',
                                attrs={'class': 'price-value'}).find('span',
                                                                     attrs={'class',
                                                                            'feature-value'}).text.strip()

    # return {'price': price}
    area = main_page_soup.find(
        'ul', attrs={
            'class': 'main-features'}).findAll('li')
    living_area = area[3].span.text.strip().split()[1]
    return {'price': price, 'living_area': living_area}
