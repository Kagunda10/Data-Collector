from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

# get the link to cities
# returns a list containing links to the cities


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
            city_houses_for_sale.append(
                ['https://www.realo.be{}'.format(x.a['href']) for x in each.ul.findAll('li')])
        elif each.div.string.strip() == 'Houses to rent':
            city_houses_for_rent.append(
                ['https://www.realo.be{}'.format(x.a['href']) for x in each.ul.findAll('li')])

    return {'sale': city_houses_for_sale, 'rent': city_houses_for_rent}
# Get all apartments in a given city
# Input is the link to the cities page
# Returns a list containing links to the apartments


def get_listing_links_list():
    main_page = 'https://www.realo.be/en/search/house/for-sale/brugge-8000'
    req = Request(main_page, headers={'User-Agent': 'Mozilla/5.0'})
    main_page_html = urlopen(req).read()

    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')

    results_list = []
    for each in main_page_soup.findAll(
        'li', attrs={
            'data-id': 'componentEstateListGridItem'}):
        if each.div.div.a:
            results_list.append(each.div.div.a['href'])

    return results_list

# Function that gets the property info
# Takes the property link as input
# Returns a dict containing the square meters, Rent per month and link to
# property


def get_apartment_info():
    main_page = 'https://www.realo.be/en/sint-gillisdorpstraat-38-8000-brugge/3273431?l=480038643'
    req = Request(main_page, headers={'User-Agent': 'Mozilla/5.0'})
    main_page_html = urlopen(req).read()

    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')

    # price = main_page_soup.find('li', attrs={'class':'col module
    # module-price'}).find('div', attrs={'class':'value'}).span.text.strip())
    habitable_area = main_page_soup.find(
        'div', attrs={
            'class': 'component-property-features'}).div.table.tbody.findAll('tr')[3].findAll('td')[1].text

    return {'price': price, 'habitable_area': habitable_area}
