from utils import *
import json
import urllib
import pandas as pd

SIG = "GET\u0000[URL]\u0000[BODY]"

API_KEY = "abd17a9f250807b76ebbfa9997ca6ade"
TMDB_API_BASE = "https://api.themoviedb.org/3/"

@memoizeToFile(file="./tmdb_search_results.pkl")
def search_tmdb_movie(query):
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
def get_tmdb_movie_id(title):
    results = search_tmdb_movie(title)
    return results['results'][0]['id'] if results['results'] else None

@memoizeToFile(file="./tmdb_movie_details.pkl")
def get_tmdb_movie_details(movie_id):
    return run_api("movie/{0}", movie_id)

@memoizeToFile(file="./tmdb_movie_crews.pkl")
def get_tmdb_movie_crew(movie_id):
    return run_api("movie/{0}/credits", movie_id)

@memoizeToFile(file="./tmdb_person_details.pkl")
def get_tmdb_person_details(person_id):
    return run_api("person/{0}", person_id)


br2049_id = get_tmdb_movie_id("Blade Runner 2049")
br2049_details = get_tmdb_movie_details(br2049_id)
br2049_ppl = get_tmdb_movie_crew(br2049_id)
gosling_details = get_tmdb_person_details(br2049_ppl['cast'][0]['id'])


x = 2