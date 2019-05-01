import pickle
import numpy as np
import pandas


class DataParser:

    def __init__(self):
        self.links_path = "../ml-latest-small/links.csv"
        self.links_pickle_name = "links.pkl"
        self.movies_path = "../ml-latest-small/movies.csv"
        self.movies_pickle_name = "movies.pkl"
        self.ratings_path = "../ml-latest-small/ratings.csv"
        self.ratings_pickle_name = "ratings.pkl"
        self.tags_path = "../ml-latest-small/tags.csv"
        self.tags_pickle_name = "tags.pkl"

        self.links = np.array([])
        self.movies = np.array([])
        self.ratings = np.array([])
        self.tags = np.array([])

    def dump_pickle(self, data, filename):
        pickle_out = open(filename, "wb")
        pickle.dump(data, pickle_out)
        pickle_out.close()

    def load_from_pickle(self, filename):
        pickle_in = open(filename, "rb")
        return pickle.load(pickle_in)

    def parse_data(self):
        try:
            self.links = np.array(self.load_from_pickle(self.links_pickle_name))
            self.movies = np.array(self.load_from_pickle(self.movies_pickle_name))
            self.ratings = np.array(self.load_from_pickle(self.ratings_pickle_name))
            self.tags = np.array(self.load_from_pickle(self.tags_pickle_name))
        except (OSError, IOError) as e:
            self.links = pandas.read_csv(self.links_path).as_matrix()
            self.movies = pandas.read_csv(self.movies_path).as_matrix()
            self.ratings = pandas.read_csv(self.ratings_path).as_matrix()
            self.tags = pandas.read_csv(self.tags_path).as_matrix()

            self.dump_pickle(self.links, self.links_pickle_name)
            self.dump_pickle(self.movies, self.movies_pickle_name)
            self.dump_pickle(self.ratings, self.ratings_pickle_name)
            self.dump_pickle(self.tags, self.tags_pickle_name)
