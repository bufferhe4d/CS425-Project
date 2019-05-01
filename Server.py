from Cryptodome import Random
from Cryptodome.Random import random
from Cryptodome.PublicKey import ElGamal
from Cryptodome.Util.number import GCD
from Cryptodome.Util.number import inverse
from Cryptodome.Util import number
import random as rnd
from User import *

class Server:
    def __init__(self, m):
        self.m = m
        self.simMat = None
        self.user_list = []
        self.avg_ratings = None
    
    def addUser(self, user_to_add):
        self.user_list.append(user_to_add)
    
    def genElgamalKeys(self):
        self.p = 100379 # prime with generator 2
        self.g = 2 # generator of p

        Y = 1 # multiplication of all public keys
        for user in self.user_list:
            user.genElgamalKeys(self.p, self.g)
            Y *= user.getPubKey() # retrive public key of each user
        
        # send general(server) public key to each user
        for user in self.user_list:
            user.setServerPubKey(Y)

    def addElgamal(c1, c2, p):
        # multiply ciphertext tuple pairwise
        res_a = c1[0]*c2[0] % p
        res_b = c1[1]*c2[1] % p

        return (res_a, res_b)
    
    def boundedDiscreteLog(pt):
        h = 0
        while h < self.p - 1:
            if(pow(self.g, h, p) == pt):
                return h
            h += 1
        return None
    
    def multiplyRatings(round1_m):
        sum_of_ratings = []
        sum_of_flags = []
        
        for i in range(self.m):
            sum_of_flags.append((1,1))
            sum_of_ratings.append((1,1))
        
        for i in range(self.m):
            rating_base = (1,1)
            flag_base = (1,1)
            for j in range(len(round1_m)):
                (A,B) = round1_m[j][i]
                temp_rating = addElgamal(rating_base, A, self.p) # Add each encryption
                temp_flag = addElgamal(flag_base, B, self.p) # Add each flag
            sum_of_ratings[i] = temp_rating
            sum_of_flags[i] = temp_flag
        
        return (sum_of_ratings, sum_of_flags)
    
    def calculateAverage(self):
        self.genElgamalKeys()
        n = len(self.user_list)
        round1_m = []
        for i in range(n):
            round1_m.append(self.user_list[i].average_round1_all(self.m))

        sum_of_ratings, sum_of_flags = multiplyRatings(round1_m, self.p)

        ratings_A = []
        flags_A = []
        for sum in sum_of_ratings:
            ratings_A.append(sum_of_ratings[0])
        for sum in sum_of_flags:
            flags_A.append(sum_of_flags[0])
        # Round 1 Done

        # Round 2   
        round2_m = []
        for i in range(n):
            round2_m.append(self.user_list[i].average_round2(ratings_A, flags_A))
        
        sum_plain_ratings = []
        sum_plain_flags = []

        for i in range(self.m):
            sum_plain_flags.append(0)
            sum_plain_ratings.append(0)
        
        for i in range(self.m):
            base = 1
            for j in range(n):
                base = base * round2_m[j][i][0] % self.p # multiply all A_1 s
            sum_plain_ratings[i] = (sum_of_ratings[i][1]*inverse(base, self.p)) % self.p # Divide by B_1
            sum_plain_ratings[i] = boundedDiscreteLog(sum_plain_ratings[i])
            base = 1
            for j in range(n):
                base = base * round2_m[j][i][1] % self.p # multiply all A_2 s
            sum_plain_flags[i] = (sum_of_flags[i][1]*inverse(base, self.p)) % self.p # Divide by B_2
            sum_plain_flags[i] = boundedDiscreteLog(sum_plain_flags[i])
        
        average_result = []

        for i in range(self.m):
            inter_result = 0
            if(sum_plain_flags[i] == 0):
                inter_result = sum_plain_flags[i]*1.0
            else:
                inter_result = sum_plain_ratings[i]*1.0/sum_plain_flags[i] # calculate the actual average
            
            average_result.append(inter_result) 

        self.avg_ratings = average_result # list of m averages