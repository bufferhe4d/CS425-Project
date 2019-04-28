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

        random_vectors = []
        for i in range(10):
            random_vectors.append(  np.random.randn(dim/10, num_vector) )
        bin_to_decimal = 1 << np.arange(num_vector - 1, -1, -1)

        table =[]
        bin_index_bits = []
        bin_index_arr = []
        datasplitted =  np.hsplit( data, 10 )
        for i in range(10):
            table.append({})
            bin_index_bits.append( ( datasplitted[i].dot( random_vectors[i]) >= 0) )
            # Encode bin index bits into integers
            bin_index_arr.append( bin_index_bits[i].dot(bin_to_decimal))
            for data_point, bin_index in enumerate(bin_index_arr[i]):
                if bin_index not in table[i]:
                   table[i][bin_index] = []
                table[i][bin_index].append(data_point)
        return table


# configure file path
data_path = 'ml-latest-small'
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
df_rating_matrix = df_rating_matrix.sub(df_rating_matrix.mean(axis=1), axis=0)
data = df_rating_matrix.values

model = LSH(data)
print(data)

table = model.train(10)

count = 0
for i in table:
    print("Table :")
    print(type(i))
    for j in i:
        count += 1
        print("-----------------------------------------------------------------bucket" +str(j))
        for value in i[j]:
            print( df_movies['title'][value] )

print("Count:", count)

