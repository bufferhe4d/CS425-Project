from User import *
from Server import *
import pandas as pd
import os.path
import time
from scipy import sparse
import numpy as np
from random import randint
""" num_items = 4
testServer = Server(num_items)

user1_rating = [3, 5, 0, 4]
user2_rating = [0, 1, 5, 0]
user3_rating = [2, 3, 2, 4]

ratings = []
ratings.append(user1_rating)
ratings.append(user2_rating)
ratings.append(user3_rating)
for i in range(len(ratings)):
    user_to_add = User(str(i))
    user_to_add.setRating({v: k for v , k in enumerate(ratings[i]) if k != 0})
    print({v: k for v , k in enumerate(ratings[i]) if k != 0})
    testServer.addUser(user_to_add)


testServer.calculateAverage()
print("Item Column Averages:")
print(testServer.avg_ratings)

testServer.calculateSimMat()

print("Predictions:")
testServer.predict_rating(0,0)
testServer.predict_rating(0,1)
testServer.predict_rating(0,2)
testServer.predict_rating(0,3) """


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

df_movie_features = df_ratings.pivot(index='userId', columns='movieId', values='rating').fillna(0)

data = df_movie_features.values
#df_new = df_movie_features.sub(df_movie_features.mean(axis=0), axis=1)

item_count = 500
data = data[:,:item_count]
#data = data[:10]
print(data)
print(len(data[0]))
print("Type:", type(data))
print(data.shape)

""" test_size = 3000
data = sparse.csc_matrix(data)
print(data[0][0])
x_i, x_j = data.nonzero()
print("num of Non-zero:", len(x_i))
test_data = {}
data = np.asarray(data.todense())
print("Data before loop", data)
#print(data[5,1])
visited_ind = {}
count = 0
while count < test_size:
    ind = np.random.randint(len(x_i))
    if ind not in visited_ind:
        visited_ind[ind] = 1
        rating = data[x_i[ind], x_j[ind]]
        test_data[(x_i[ind], x_j[ind])] = rating 
        data[x_i[ind], x_j[ind]] = 0
        count +=1   """

#data = sparse.csc_matrix(data)
#print(test_data)
print("Type:", type(data))
item_count = len(data[0]) 

test_file = open("test_data500-3000-2.pickle", "rb")
test_data = pickle.load(test_file)
#pickle.dump(test_data, test_file)
test_file.close()
count = 0

for index, rating in test_data.items():
    data[index[0]][index[1]] = 0




testServer = Server(item_count)

user_list = []
for i in range(len(data)):
    user_ratings = map(float, data[i].tolist())
    user_list.append(user_ratings)
    user_to_add = User(str(i))
    
    user_to_add.setRating({v: int(k*2) for v , k in enumerate(user_ratings) if k != 0})
    testServer.addUser(user_to_add)

print("Users added")

begin = time.process_time()
testServer.calculateAverage()
print("Item Column Averages:")
print(testServer.avg_ratings)
end = time.process_time()
print("Average seconds:", end - begin)


begin = time.process_time()
#testServer.calculateSimMat()
#sim_file = open("testsim_mat1000.pickle", "wb")
#pickle.dump(testServer.simMat, sim_file)
sim_file = open("testsim_mat1000.pickle", "rb")
testServer.setServerSimMat(pickle.load(sim_file))
print("Similarity Matrix Done")
end = time.process_time()
print("Similarity seconds:", end - begin)

#print("Index 0", testServer.simMat[77])
#print("Index 1", testServer.simMat[46])

def rmse(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2).mean())

ratings = np.array([])
predictions = np.array([])
cnt = 0
print(testServer.p)
for index, rating in test_data.items():
    #print("index:", index)
    cnt+=1
    predicted = testServer.predict_rating(index[0], index[1])
    ratings = np.append(ratings, rating)
    predictions = np.append(predictions, predicted)
    print("preditced:", cnt, " prediction: ", predicted, " original: ", rating)
    if cnt == 5:
        print("Error:", rmse(predictions, ratings))
        cnt = 0
    



print("Error:", rmse(predictions, ratings))