from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
from lxml.html.soupparser import fromstring
from models.utils import *
from selenium import webdriver



# SEARCHERS
def search_lb(query, first_result=True, query_type=""):
    formatted_query = query.lower().replace(" ", "+")
    search_page = "https://letterboxd.com/search/{0}/{1}/".format(query_type, formatted_query)
    if first_result:
        driver = webdriver.Chrome()
        driver.get(search_page)
        first_result = driver.find_element_by_class_name('search-result').find_element_by_tag_name("a")
        first_result.click()
        finish_url = driver.current_url
        driver.close()
        return finish_url
    return search_page


# PAGE SCRAPERS
def scrape_lb_studio_using_search_results(url):
    src = urllib.request.urlopen(url, context=UNVERIFIED_CONTEXT).read()
    soup = BeautifulSoup(src, "html.parser")
    first_result = soup.find("li", class_="search-result")
    first_result_metadata = first_result.find("p", class_="film-metadata")
    first_result_meta_string = first_result_metadata.contents[0]
    num_movies = int(re.search("[0-9]+", first_result_meta_string)[0])
    return {"num_movies": num_movies}



# GETTERS (combine search and scrape functions)
@memoizeToFile(file="./get_lb_studio_data.pkl")
def get_lb_studio_data(studio):
    studio_url = search_lb(studio, first_result=False, query_type="studios")
    return scrape_lb_studio_using_search_results(studio_url)

def get_studios_data(studios):
    return apply_dicts_keywise([get_lb_studio_data(s) for s in studios.split(", ")], max, 0)



#test = get_tmbb_title_data("Blade Runner 2049")

x = 2
