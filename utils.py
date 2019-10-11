import re
import pandas as pd
import os
import csv
import pickle
import ssl
import urllib

UNVERIFIED_CONTEXT = ssl._create_unverified_context()

class Memoizer:
    def __init__(self, func, file):
        self.f = func
        self.file = file
        if os.path.isfile(file):
            with open(file, 'rb') as input_stream:
                self.memo = pickle.load(input_stream)
        else:
            self.memo = dict()

    def __call__(self, key, update=False, save=True):
        if not update and key in self.memo:
            return self.memo[key]
        else:
            value = self.f(key)
            self.memo[key] = value
            if save:
                self.save()
            return value

    def save(self, output_file=None):
        if not output_file:
            output_file = self.file
        with open(output_file, 'wb') as output:
            pickle.dump(self.memo, output, 2)

    def dict(self, iterable, update=False, save_at_end=False):
        remaining = iterable if update else set(iterable) - set(self.memo)
        data = {}
        for c, k in enumerate(remaining):
            print_status("Processing remaining input {0} out of {1} ({2} Total)".format(c, len(remaining), len(iterable)))
            data[k] = self(k, update=True, save=(not save_at_end))
        if save_at_end:
            self.save()
        return {k: self(k) for k in iterable}

    def process(self, *args, **kwargs):
        self.dict(*args, **kwargs)

    def historical_dict(self):
        return self.memo

    def df(self, *args, **kwargs):
        data = self.dict(*args, **kwargs)
        return pd.DataFrame.from_dict(data=data, orient="index")

    def historical_df(self):
        return pd.DataFrame.from_dict(data=self.historical_dict(), orient="index")

def memoizeToFile(file):
    return lambda func: Memoizer(func, file)



def print_status(*args, sep = " "):
    print('\r' + sep.join(args), end='')

def split_list(iterable, splitters):
    """Splits the input iterable into a list of lists at each occurrence of anything in splitters.
    :param iterable: An iterable to split
    :param splitters: An iterable of elements to split the iterable by
    :return: A list of lists - the original iterable split by splitters.
    """
    splitters = set(splitters)
    lists = []
    this_list = []
    for elem in iterable:
        if elem in splitters:
            if len(this_list) > 0:
                lists.append(this_list)
                this_list = []
            continue
        else:
            this_list.append(elem)
    return lists


def writeTable(table, filename):
    """Writes table to csv.
    :param table: The table to write (should be indexed by rows then columns)
    :param filename: The directory to write the csv to
    :return: None
    """
    with open(filename, "w") as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerows(table)


def parse_digit(string, caster):
    """Parses the digits of a string, and casts them using input caster.
    :param string: Input string to parse for digits
    :param caster: Input function used to cast parsed string (e.g. int, float, or str). Defaults to float.
    :return: The casted, parsed value.
    """
    return caster(re.sub("[^0-9.-]", "", string)) if isinstance(string, str) else string


def replace_list(iterable, mappings):
    """Returns a new list where all instances of any key in mappings are replaced with their corresponding replacement.
    :param iterable: Iterable to replace values in.
    :param mappings: A dictionary having each value we want to replace as a key with it's corresponding replacement
    as its value.
    :return: New list with replacements
    """
    return [(mappings[k] if (k in mappings) else k) for k in iterable]

def one_hot_encode(keys, values, split_func):
    one_hot_encoder = lambda x: {k: 1 for k in split_func(x)}
    data = {k: one_hot_encoder(v) for k, v in zip(keys, values)}
    df = pd.DataFrame.from_dict(data, orient='index')
    df = df.fillna(0)
    return df

def apply_to_df(df, f, columns = None):
    """MIGHT BE DELETABLE"""
    if not columns:
        columns = df.columns
    for column in columns:
        df[column] = [f(e) for e in df[column]]


def clean_query(query):
    return urllib.parse.quote_plus(query)

def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def apply_dicts_keywise(dicts, f, default):
    max_dict = {}
    all_keys = reduce(lambda x, y: x | y, [set(d.keys()) for d in dicts])
    for key in all_keys:
        max_dict[key] = f((d[key] if (key in d) else default) for d in dicts)
    return max_dict