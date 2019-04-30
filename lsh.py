from copy import copy
from itertools import combinations
import numpy as np
import pandas as pd
import os.path
from scipy import spatial
import sklearn.preprocessing as pp
from scipy import sparse


class LSH:
    def __init__(self, data, orig_data):
        self.data = data
        self.orig_data = orig_data
        self.buckets = None
        self.vectors = None
        self.num_vector = None
        self.sparsedata = None
        self.div_num = 1
        self.sim_mat = self.getSimilarity()
        print("similirez")
        self.aver_mov = self.getAverage()

    def gen_orthagonal(self, k):
        x = np.random.rand(len(k))
        x -= x.dot(k)*k
        x /= np.linalg.norm(x)

        return x

    def gen_rand_vecs(self, n):
        print("New")
        k = np.random.rand(n)

        rand_vecs = []
        rand_vecs.append(k)
        for i in range(9723):
            rand_vecs.append(self.gen_orthagonal(k))
        return rand_vecs

    def train(self, num_vector):
        dim = self.data.shape[1]
        self.num_vector = num_vector
        random_vectors = []
        """ for i in range(self.div_num):
            random_vectors.append(  np.random.randn(int(dim/self.div_num), num_vector) ) """
        random_vectors.append(self.gen_rand_vecs(num_vector))
        print(len(random_vectors[0]))
        
        bin_to_decimal = 1 << np.arange(num_vector - 1, -1, -1)

        table =[]
        bin_index_bits = []
        bin_index_arr = []
        datasplitted =  np.hsplit( data, self.div_num )
        for i in range(self.div_num):
            table.append({})
            bin_index_bits.append( ( datasplitted[i].dot( random_vectors[i]) >= 0) )
            # Encode bin index bits into integers
            bin_index_arr.append( bin_index_bits[i].dot(bin_to_decimal))
            for data_point, bin_index in enumerate(bin_index_arr[i]):
                if bin_index not in table[i]:
                   table[i][bin_index] = []
                table[i][bin_index].append(data_point)
        self.buckets = table
        self.vectors = random_vectors

    def query(self, movieId):
        similars = []
        bin_to_decimal = 1 << np.arange(self.num_vector - 1, -1, -1)
        datasplitted =  np.hsplit( self.data, self.div_num )
        for i in range(self.div_num):
            bit_arr = datasplitted[i][movieId].dot(self.vectors[i]) >= 0
            bin_index = bit_arr.dot(bin_to_decimal)
            k = self.buckets[i][bin_index]
            for item in k:
                if item not in similars:
                    similars.append(item)

        return similars

    def predict_rating(self, userId, movieId):
        sim_total = 0
        sum_total = 0
        similars = self.query(userId)
        print("Similar user count: ", len(similars))
        for i in range(len(similars)):
            print(orig_data[similars[i]][movieId])
            cur_sim = 1 - spatial.distance.cosine(data[userId], data[similars[i]])
            if orig_data[similars[i]][movieId] != 0 and userId != similars[i]:
                sum_total += cur_sim*orig_data[similars[i]][movieId]
                sim_total += cur_sim
            
        
        if sim_total == 0:
            return 0
        else:
            return sum_total/sim_total
    def getSimilarity(self):
        similarity = []
        self.sparsedata = sparse.csc_matrix(data.astype(np.dtype('double')))
        sparsenorm = pp.normalize( self.sparsedata , axis=0)
        """INEFFIECNT WAY
        dim = self.data.shape[1]
        for i in range(dim):
           temp = []
           print(i)
           for j in range(dim):
               temp.append(1-spatial.distance.cosine(data[:,i],data[:,j]))
           similarity.append(temp)"""
        return sparsenorm.T * sparsenorm

    def getAverage(self):
        dim = self.data.shape[1]
        sum= np.zeros( dim)
        rated= np.zeros( dim)
        for user in orig_data:
            for i in range(dim):
                if user[i] is not 0:
                    sum[i] += user[i]
                    rated[i] += 1
        average = np.zeros( dim)
        for i in range(dim):
            if rated[i] is not 0:
                average[i] = sum[i] / rated[i]
        return average

    def getPrediction( self, userId, movieId):
        dim = self.data.shape[1]
        Rk = self.aver_mov[movieId]
        total = 0
        w_total = 0
        row = self.sparsedata.getrow(userId)
        col = self.sim_mat.getcol(movieId)
        for j in col.nonzero()[1]:
            print(total)
            print(w_total)
            total += col[0,j]
            w_total += col[0,j]*(self.orig_data[userId,j]-self.aver_mov[j])
        return Rk + w_total/total

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

df_rating_matrix = df_ratings.pivot(index='userId', columns='movieId', values='rating').fillna(0)
orig_data = df_rating_matrix.values
df_rating_matrix = df_rating_matrix.sub(df_rating_matrix.mean(axis=1), axis=0)
data = df_rating_matrix.values

model = LSH(data, orig_data)
print(data)
print(data[0][0])
print(data.shape)
model.train(5)

count = 0
""" for i in model.buckets:
    print("Table :")
    print(type(i))
    for j in i:
        count += 1
        print("-----------------------------------------------------------------bucket" +str(j))
        for value in i[j]:
            print( df_movies['title'][value] ) """

print("Count:", count)

print("Original Rating: ", orig_data[0][2])
#print(model.predict_rating(0,2))
print(model.getPrediction(0,2))

