from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

def get_jaap_city_links():
    url = 'https://www.jaap.nl/koophuizen/'
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    main_page_html = urlopen(req).read()

    main_page_soup = BeautifulSoup(main_page_html, 'html.parser')

    city_sale_links = []
    city_rent_links = []

    # for each in main_page_soup.findAll('div', attrs={'class':'p50 link-list'}):
    #     if each.div.text == "Aangeboden koopwoningen":
            
    #     elif each.div.text == "Aangeboden huurwoningen":
    #         print('No')
    for each in main_page_soup.findAll('a', attrs={'data-category': 'footer province sale'}):
        city_sale_links.append(url + each.get('href'))
    for each in main_page_soup.findAll('a', attrs={'data-category': 'footer province rent'}):
        city_rent_links.append(url + each.get('href'))

    return {'sale':city_sale_links, 'rent':city_rent_links}
        
def get_zimmo_apartment_list():
    

print(get_jaap_city_links())