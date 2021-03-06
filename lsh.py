from copy import copy
from itertools import combinations
import numpy as np
import pandas as pd
import os.path
from scipy import spatial
import sklearn.preprocessing as pp
from scipy import sparse
import pickle
import time

class LSH:
    def __init__(self, data, orig_data, sim_mat_load = False):
        self.data = data
        self.orig_data = orig_data
        self.m = len(orig_data[0])
        self.buckets = None
        self.vectors = None
        self.num_vector = None
        self.sparsedata = None
        self.div_num = 1
        self.sparsedata = sparse.csc_matrix(orig_data)
        begin = time.process_time()
        if not sim_mat_load:
            self.sim_mat = self.getSimilarity()
        else:
            self.sim_mat = self.loadSimMat()
        end = time.process_time()
        
        print("simmat propro", end - begin )
        #print("similirez")
        begin = time.process_time()
        self.aver_mov = self.getAverage()
        end = time.process_time()
        print("aver propro", end - begin )

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
        for i in range(self.m - 1):
            rand_vecs.append(self.gen_orthagonal(k))
        return rand_vecs

    def train(self, num_vector):
        dim = self.data.shape[1]
        self.num_vector = num_vector
        random_vectors = []
        """ for i in range(self.div_num):
            random_vectors.append(  np.random.randn(int(dim/self.div_num), num_vector) ) """
        random_vectors.append(self.gen_rand_vecs(num_vector))
        #print(len(random_vectors[0]))

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
        #print("Similar user count: ", len(similars))
        for i in range(len(similars)):
            #print(orig_data[similars[i]][movieId])
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

        sparsenorm = pp.normalize( self.sparsedata , axis=0)
        """INEFFIECNT WAY
        dim = self.data.shape[1]
        for i in range(dim):
           temp = []
           print(i)
           for j in range(dim):
               temp.append(1-spatial.distance.cosine(data[:,i],data[:,j]))
           similarity.append(temp)"""
        result = sparsenorm.T * sparsenorm
        f = open('sim_mat.pickle', 'wb')
        pickle.dump(result, f)
        f.close()
        return result

    def loadSimMat(self):
        f = open('sim_mat.pickle', 'rb')
        result = pickle.load(f)
        f.close()
        return result

    def getAverage(self):
        """ dim = self.data.shape[1]
        sum= np.zeros( dim)
        rated= np.zeros( dim)
        for user in orig_data:
            for i in range(dim):
                if user[i] != 0:
                    sum[i] += user[i]
                    rated[i] += 1
        average = np.zeros( dim)
        for i in range(dim):
            if rated[i] != 0:
                average[i] = sum[i] / rated[i]
<<<<<<< Updated upstream
        return average """
        return np.true_divide(orig_data.T.sum(1), (orig_data.T!=0).sum(1))

    def getPrediction( self, userId, movieId):
        dim = self.data.shape[1]
        Rk = self.aver_mov[movieId]
        total = 0
        w_total = 0
        row = self.sparsedata.getrow(userId)
        k = 1
        #cow = sorted(range(len(row[1])), key=lambda i: row[1][i])[-1*k:] #best k
        col = self.sim_mat.getcol(movieId)
        cnt = 0
        for j in row.nonzero()[1]:
 #           print("j:", j)
            if j != movieId:
                total += col[j,0]
                w_total += col[j,0]*(self.orig_data[userId,j]-self.aver_mov[j])
        if total is 0:
            return 0
        #print("Rk", Rk)
        #print("wtotal", w_total)
        #print("total", total)
        if Rk+ w_total/total > 5:
            return 5
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
    dtype={'userId': 'int32', 'movieId': 'int32', 'rating': 'double'})

#print(df_ratings.head(5))

df_rating_matrix = df_ratings.pivot(index='userId', columns='movieId', values='rating').fillna(0)
orig_data = df_rating_matrix.values
df_rating_matrix = df_rating_matrix.sub(df_rating_matrix.mean(axis=1), axis=0)
data = df_rating_matrix.values

item_count = 500
data = data[:,:item_count]
data = orig_data[:,:item_count]

#data = [[3,5,0,4],[0,1,5,0], [2,3,2,4]]
#data = np.array(data)
#orig_data = data

#print("Avg", np.true_divide(data.T.sum(1), (data.T!=0).sum(1)))
model = LSH(data, orig_data)
#print(data)
#print(data[0][0])
#print(data.shape)
#model.train(5)

count = 0
""" for i in model.buckets:
    print("Table :")
    print(type(i))
    for j in i:
        count += 1
        print("-----------------------------------------------------------------bucket" +str(j))
        for value in i[j]:
            print( df_movies['title'][value] ) """

#print("Count:", count)

#print("Original Rating: ", orig_data[0][0])
#print(model.predict_rating(0,2))
#print(model.getPrediction(0,0))
#print("Original Rating: ", orig_data[0][1])
#print(model.getPrediction(0,1))
#print("Original Rating: ", orig_data[0][2])
#print(model.getPrediction(0,2))
#print("Original Rating: ", orig_data[0][3])
#print(model.getPrediction(0,3))
#print(model.getPrediction(1,50))

test_file = open("test_data500-3000-2.pickle", "rb")
test_data = pickle.load(test_file)
#pickle.dump(test_data, test_file)
test_file.close()
count = 0

#print(data.shape)
for index, rating in test_data.items():
    data[index[0]][index[1]] = 0

def rmse(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2).mean())

ratings = np.array([])
predictions = np.array([])
cnt = 0

begin = time.process_time()
for index, rating in test_data.items():
    #print("index:", index)
    cnt+=1
    predicted = model.getPrediction(int(index[0]), index[1])
    ratings = np.append(ratings, rating)
    predictions = np.append(predictions, predicted)
    #print("preditced:", cnt, " prediction: ", predicted, " original: ", rating)
    #if cnt == 5:
        #print("Error:", rmse(predictions, ratings))
     #   cnt = 0
     
end = time.process_time()
print("simmat propro", (end - begin)/3000 )
print("Error:", rmse(predictions, ratings))

