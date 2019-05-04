from Cryptodome import Random
from Cryptodome.Random import random
from Cryptodome.PublicKey import ElGamal
from Cryptodome.Util.number import GCD
from Cryptodome.Util.number import inverse
from Cryptodome.Util import number
import random as rnd
import math
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
        self.p = 1000003#100379 # prime with generator 2
        self.g = 2 # generator of p

        Y = 1 # multiplication of all public keys
        for user in self.user_list:
            user.genElgamalKey(self.p, self.g)
            Y = Y * user.getPubKey() % self.p # retrive public key of each user
        
        # send general(server) public key to each user
        for user in self.user_list:
            user.setServerPubKey(Y)

    def addElgamal(self, c1, c2, p):
        # multiply ciphertext tuple pairwise
        res_a = c1[0]*c2[0] % p
        res_b = c1[1]*c2[1] % p

        return (res_a, res_b)
    
    def boundedDiscreteLog(self, pt):
        h = 0
        while h < self.p - 1:
            if(pow(self.g, h, self.p) == pt):
                return h
            h += 1
        return None
    
    def multiplyRatings(self, round1_m):
        sum_of_ratings = []
        sum_of_flags = []
        
        for i in range(self.m):
            sum_of_flags.append((1,1))
            sum_of_ratings.append((1,1))
        
        for i in range(self.m):
            temp_rating = (1,1)
            temp_flag = (1,1)
            for j in range(len(round1_m)):
                (A,B) = round1_m[j][i]
                temp_rating = self.addElgamal(temp_rating, A, self.p) # Add each encryption
                temp_flag = self.addElgamal(temp_flag, B, self.p) # Add each flag
            sum_of_ratings[i] = temp_rating
            sum_of_flags[i] = temp_flag
        
        return (sum_of_ratings, sum_of_flags)
    
    def calculateAverage(self):
        self.genElgamalKeys()
        n = len(self.user_list)
        round1_m = []
        for i in range(n):
            round1_m.append(self.user_list[i].average_round1_all(self.m))

        sum_of_ratings, sum_of_flags = self.multiplyRatings(round1_m)

        ratings_A = []
        flags_A = []
        for sum in sum_of_ratings:
            ratings_A.append(sum[0])
        for sum in sum_of_flags:
            flags_A.append(sum[0])
        # Round 1 Done
        #print(ratings_A)
        #print(sum_of_ratings)
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
            sum_plain_ratings[i] = self.boundedDiscreteLog(sum_plain_ratings[i])
            base = 1
            for j in range(n):
                base = base * round2_m[j][i][1] % self.p # multiply all A_2 s
            sum_plain_flags[i] = (sum_of_flags[i][1]*inverse(base, self.p)) % self.p # Divide by B_2
            sum_plain_flags[i] = self.boundedDiscreteLog(sum_plain_flags[i])
        
        average_result = []

        for i in range(self.m):
            inter_result = 0
            if(sum_plain_flags[i] == 0):
                inter_result = sum_plain_flags[i]*1.0
            else:
                inter_result = sum_plain_ratings[i]*1.0/sum_plain_flags[i] # calculate the actual average
            print("Rating i", sum_plain_ratings[i])
            print("flags i", sum_plain_flags[i])
            average_result.append(inter_result) 

        self.avg_ratings = average_result # list of m averages

    def multiplySimilarityRatings(self, sim_round1_m):
        pairwise_mults = []
        for i in range(self.m):
            temp_pair = []
            for j in range(self.m):
                temp_pair.append((1,1))
            pairwise_mults.append(temp_pair)
        
        for i in range(self.m):
            for j in range(self.m):
                temp_pair = (1,1)
                for k in range(len(sim_round1_m)):
                    rating_product = sim_round1_m[k][i][j]
                    temp_pair = self.addElgamal(temp_pair, rating_product, self.p)
                pairwise_mults[i][j] = temp_pair
        
        pairwise_m = []
        # unnecessary
        for i in range(self.m):
            temp_zero = []
            for j in range(self.m):
                temp_zero.append(0)
            pairwise_m.append(temp_zero)
        
        # merge this above
        for i in range(self.m):
            for j in range(self.m):
                pairwise_m[i][j] = pairwise_mults[i][j][0]
        return pairwise_m, pairwise_mults # Corresponds to A,B in step 2

    def getSim(self, nom, denom1, denom2):
        nom = float(nom)
        if(nom == 0):
            return 0.0
        else:
            return nom/math.sqrt(denom1*denom2)
    def calculateSimMat(self):
        self.genElgamalKeys()
        n = len(self.user_list)
        sim_round1_m = []
        for i in range(n):
            sim_round1_m.append(self.user_list[i].sim_round1_all(self.m))

        pairwise_m, pairwise_mults = self.multiplySimilarityRatings(sim_round1_m)
        
        round2_m = []

        for i in range(n):
            round2_m.append(self.user_list[i].sim_round2(pairwise_m))
        print(round2_m)
        decrypt_pairwise_m = []
        decrypt_denom = []

        for i in range(self.m):
            temp_zero = []
            for j in range(self.m):
                temp_zero.append(0)
            decrypt_pairwise_m.append(temp_zero)
            decrypt_denom.append(0)    

        for i in range(self.m):
            for j in range(self.m):
                base = 1
                for k in range(n):
                    base = base*round2_m[k][i][j] % self.p
                
                #decrypt_pairwise_m[i][j] = pairwise_mults[i][j][1] * inverse(base, self.p) % self.p
                decrypt_pairwise_m[i][j] = self.boundedDiscreteLog(pairwise_mults[i][j][1] * inverse(base, self.p) % self.p)
            
            decrypt_denom[i] = decrypt_pairwise_m[i][i]
        
        result_matrix = []
        for i in range(self.m):
            sim_vector = []
            for j in range(self.m):
                sim_vector.append(self.getSim(decrypt_pairwise_m[i][j], decrypt_denom[i], decrypt_denom[j]))
            result_matrix.append(sim_vector)
        
        print(result_matrix)
        self.simMat = result_matrix