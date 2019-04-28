from copy import copy
from itertools import combinations
import numpy as np
import pandas as pd
import os.path


class LSH:
    def __init__(self, data):
        self.data = data

    def train(self, num_vector):
        dim = self.data.shape[1]

        random_vectors = np.random.randn(dim, num_vector)
        bin_to_decimal = 1 << np.arange(num_vector - 1, -1, -1)

        table = {}
        
        # multiply data with random vectors
        bin_index_bits = (self.data.dot(random_vectors) >= 0)

        # Encode bin index bits into integers
        bin_index_arr = bin_index_bits.dot(bin_to_decimal)

        for data_point, bin_index in enumerate(bin_index_arr):
            if bin_index not in table:
                table[bin_index] = []

            table[bin_index].append(data_point)

        return table


# configure file path
data_path = '../../ml-latest-small'
movies_filename = 'movies.csv'
ratings_filename = 'ratings.csv'
# read data
df_movies = pd.read_csv(
    os.path.join(data_path, movies_filename),
    usecols=['movieId', 'title'],
    dtype={'movieId': 'int32', 'title': 'str'})

df_ratings = pd.read_csv(
    os.path.join(data_path, ratings_filename),
    usecols=['userId', 'movieId', 'rating'],
    dtype={'userId': 'int32', 'movieId': 'int32', 'rating': 'float32'})

print(df_ratings.head(5))

df_rating_matrix = df_ratings.pivot(index='movieId', columns='userId', values='rating').fillna(0)

data = df_rating_matrix.values

model = LSH(data)

table = model.train(10)

print(table)

