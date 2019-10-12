from utils import *
import json
import urllib
import pandas as pd


class TMDB_Scraper:
    TMDB_API_BASE = "https://api.themoviedb.org/3/"
    def __init__(self, api_key):
        """We use the TMDB API to get our data, so the user must pass in their API key after registering with tMDb."""
        self.api_key = api_key

    #@memoizeToFile(file="./tmdb_search_results.pkl")
    def search_movie(self, query):
        formatted_query = urllib.parse.quote_plus(query)
        url = TMDB_Scraper.TMDB_API_BASE + "search/movie" \
                              "?query={0}&api_key={1}&language=en-US&page=1&include_adult=false".format(formatted_query,
                                                                                                        self.api_key)
        response = urllib.request.urlopen(url, context=UNVERIFIED_CONTEXT)
        data = json.loads(response.read())
        return data

    def run_api(self, path_string, *args, js_query_args=None):
        # TODO: Might be able to also incorporate kwargs for this method
        if any([pd.isnull(e) for e in args]):
            return {}
        json_url = f"{TMDB_Scraper.TMDB_API_BASE}{path_string.format(*args)}?api_key={self.api_key}"
        if js_query_args:
            json_url += f"&{dict_to_query_string(js_query_args)}"
        return get_json(json_url)

    #@memoizeToFile(file="./tmdb_movie_ids.pkl")
    def movie_id(self, title):
        results = self.search_movie(title)
        return results['results'][0]['id'] if results['results'] else None

    #@memoizeToFile(file="./tmdb_movie_details.pkl")
    def movie_details(self, movie_id):
        return self.run_api("movie/{0}", movie_id)

    #@memoizeToFile(file="./tmdb_movie_crews.pkl")
    def movie_crew(self, movie_id):
        return self.run_api("movie/{0}/credits", movie_id)

    #@memoizeToFile(file="./tmdb_person_details.pkl")
    def person_details(self, person_id):
        return self.run_api("person/{0}", person_id)

    def movie_videos(self, movie_id):
        return self.run_api("movie/{0}/videos", movie_id)

"""

@memoizeToFile(file="./tmdb_search_results.pkl")
def search_movie(query):
    formatted_query = urllib.parse.quote_plus(query)
    url = TMDB_API_BASE + "search/movie" \
              "?query={0}&api_key={1}&language=en-US&page=1&include_adult=false".format(formatted_query, API_KEY)
    response = urllib.request.urlopen(url, context=UNVERIFIED_CONTEXT)
    data = json.loads(response.read())
    return data

def run_api(path_string, *args):
    # TODO: Might be able to also incorporate kwargs for this method
    if any([pd.isnull(e) for e in args]):
        return {}
    json_url = TMDB_API_BASE + path_string.format(*args) + "?api_key={0}".format(API_KEY)
    return get_json(json_url)


def get_json(json_url):
    response = urllib.request.urlopen(json_url, context=UNVERIFIED_CONTEXT)
    data = json.loads(response.read())
    return data

@memoizeToFile(file="./tmdb_movie_ids.pkl")
def get_movie_id(title):
    results = search_movie(title)
    return results['results'][0]['id'] if results['results'] else None

@memoizeToFile(file="./tmdb_movie_details.pkl")
def get_movie_details(movie_id):
    return run_api("movie/{0}", movie_id)

@memoizeToFile(file="./tmdb_movie_crews.pkl")
def get_movie_crew(movie_id):
    return run_api("movie/{0}/credits", movie_id)

@memoizeToFile(file="./tmdb_person_details.pkl")
def get_person_details(person_id):
    return run_api("person/{0}", person_id)

"""

if __name__ == "__main__":
    tmdb_scraper = TMDB_Scraper("abd17a9f250807b76ebbfa9997ca6ade")
    br2049_id = tmdb_scraper.movie_id("Blade Runner 2049")
    br2049_details = tmdb_scraper.movie_details(br2049_id)
    br2049_ppl = tmdb_scraper.movie_crew(br2049_id)
    br2049_vids = tmdb_scraper.movie_videos(br2049_id)
    gosling_details = tmdb_scraper.person_details(br2049_ppl['cast'][0]['id'])
    ...
