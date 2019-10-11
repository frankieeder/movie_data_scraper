from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
from lxml.html.soupparser import fromstring
from models.utils import *

# SEARCHERS
def search_imdb(query, results=True, query_type=None):
    base_url = "https://www.imdb.com"
    formatted_query = clean_query(query)
    query_type = query_type if query_type else "all"
    search_page = "https://www.imdb.com/find?q={0}&s={1}".format(formatted_query, query_type)
    if results:
        src = urllib.request.urlopen(search_page, context=UNVERIFIED_CONTEXT).read()
        pg = fromstring(src)
        results = pg.xpath('//table[@class="findList"]//td[@class="result_text"]/a/@href')
        results = [base_url + r for r in results]
        return results
    return search_page

# PAGE SCRAPERS
def scrape_imdb_person(url):
    """Defines how to scrape data once we are on an imdb person main page."""
    base_url = re.search(".*/", url)[0]

    src = urllib.request.urlopen(base_url, context=UNVERIFIED_CONTEXT).read()
    soup = BeautifulSoup(src, "html.parser")

    filmography = soup.find(id="filmography")
    filmo_headers = filmography.find_all(class_="head")
    filmo_header_texts = [e.find("a") for e in filmo_headers]
    filmo_titles = [e.text for e in filmo_header_texts]
    filmo_counts = [e.next_sibling[2:-10] for e in filmo_header_texts]
    filmography_counts = {t: c for t, c in zip(filmo_titles, filmo_counts)}

    awards = scrape_imdb_person_awards(base_url + "awards/")

    meta = {}
    max_star_rank = 10000
    star_rank = soup.find("div",id="prometer_container").find("a").text
    if star_rank == "Top 500":
        meta["star_rank"] = max_star_rank - 500
    elif star_rank == "Top 5000":
        meta["star_rank"] = max_star_rank - 5000
    elif star_rank == "SEE RANK":
        pass
    else:
        meta["star_rank"] = max_star_rank - int(star_rank)
    # TODO: Could add more analysis here, number of photos and videos?
    return merge_dicts(filmography_counts, awards, meta)

def scrape_imdb_person_awards(url):
    """Defines how to scrape data once we are on an imdb person awards page."""
    base_url = re.search(".*/", url)[0]

    src = urllib.request.urlopen(base_url, context=UNVERIFIED_CONTEXT).read()
    soup = BeautifulSoup(src, "html.parser")

    results = {}
    award_count_string = soup.find("div", class_="desc").text
    if award_count_string:
        award_count_words = award_count_string.split()
        results["num_wins"] = int(award_count_words[2])
        results["num_noms"] = int(award_count_words[5])
        results["win_nom_ratio"] = results["num_wins"] / results["num_noms"]
    return results

def scrape_imdb_title(url):
    base_url = re.search(".*/", url)[0]
    src = urllib.request.urlopen(base_url, context=UNVERIFIED_CONTEXT).read()
    pg = fromstring(src)
    data = {}
    xpaths = {
        'actual_title': '//meta[@property="og:title"]/@content',
        'imdb_rating': '//div[@class="imdbRating"]//span[@itemprop="ratingValue"]/text()',
        'metacritic_rating': '//div[contains(@class,"metacriticScore")]/span/text()',
        'directors': '//div[@class="plot_summary_wrapper"]//span[@itemprop="director"]/a/span/text()',
        'writers': '//div[@class="plot_summary_wrapper"]//span[@itemprop="creator"]/a/span/text()',
        'actors': '//div[@class="plot_summary_wrapper"]//span[@itemprop="actors"]/a/span/text()',
        'genres': '//h4[contains(text(), "Genres:")]/../a/text()',
        'runtime': '//h4[contains(text(), "Runtime:")]/following-sibling::time/text()',
        'budget': '//h4[contains(text(), "Budget:")]/following-sibling::text()[1]',
        'studios': '//h4[contains(text(), "Production Co:")]/../span/a/span/text()'
    }
    for key in xpaths:
        try:
            data[key] = ", ".join(pg.xpath(xpaths[key]))
        except Exception:
            pass
    return data


# GETTERS (combine search and scrape functions)
@memoizeToFile(file = "./imdb_title_data.pkl")
def get_imdb_title_data(title):
    results = search_imdb(title, results=True, query_type='tt')
    return scrape_imdb_title(results[0]) if results else {}

@memoizeToFile(file="./imdb_title_data_by_id")
def get_imdb_title_data_from_id(id):
    if not id:
        return {}
    url = "https://www.imdb.com/title/{0}/".format(id)
    return scrape_imdb_title(url)

@memoizeToFile(file="./imdb_person_data.pkl")
def get_imdb_person_data(person):
    person_url = search_imdb(person, results=True, query_type='nm')[0]
    return scrape_imdb_person(person_url)

def get_imdb_people_data(people):
    return {} if pd.isnull(people) else apply_dicts_keywise([get_imdb_person_data(d) for d in people.split(", ")], max, 0)


x = 2
