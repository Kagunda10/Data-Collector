from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

# get the link to cities
#returns a list containing links to the cities
def get_huispedia_city_links():
    main_page = 'https://huispedia.nl/'
    req = Request(main_page, headers={'User-Agent': 'Mozilla/5.0'})
    main_page_html = urlopen(req).read()

    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')

    footer = main_page_soup.find('footer', attrs={'class':'footer'})

    cities_div = footer.find('div', attrs={'class':'d-none d-sm-block'})

    cities_list = cities_div.findAll('li')

    city_links = []
    for each in cities_list:
        city_links.append('https://huispedia.nl{}'.format(each.find('a').get('href')))
    return city_links

# Get all apartments in a given city
# Input is the link to the cities page
# Returns a list containing links to the apartments

def get_apartment_list():
    main_page = 'https://huispedia.nl/zoeken/enschede'
    req = Request(main_page, headers={'User-Agent': 'Mozilla/5.0'})
    main_page_html = urlopen(req).read()

    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')

    search_results = main_page_soup.find('ul', attrs={'id':'resultlist'})

    property_list = []
    for each in search_results.findAll('li'):
        try:
            property_list.append(each.find('a').get('href'))
        except AttributeError as e:
            pass
    return property_list

# Get the number of pages oin the pagination
# Returns the number of pages in the resukt set
def get_no_of_pages(main_page):
    req = Request(main_page, headers={'User-Agent': 'Mozilla/5.0'})
    main_page_html = urlopen(req).read()

    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')

    pagination = main_page_soup.find('div', attrs={'id': 'pagination-wrapper'})

    page_list = pagination.findAll('li')

    no_of_pages = page_list[-2].find().attrs[u'data-id']

    return no_of_pages

# To be done get price

def get_apartment_info():
    main_page = 'https://huispedia.nl/amsterdam/1018tn/plantage-muidergracht/75-b'
    req = Request(main_page, headers={'User-Agent': 'Mozilla/5.0'})
    main_page_html = urlopen(req).read()

    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')
    living_area = main_page_soup.find('div', attrs={'id': 'feature-big-woonoppervlak'}).find('div', attrs={'class': 'value'}).text

    return {'living_area':living_area, 'price':price}
    