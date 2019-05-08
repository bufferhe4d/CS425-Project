from User import *
from Server import *

num_items = 4
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
testServer.predict_rating(0,3)