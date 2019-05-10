from Cryptodome import Random
from Cryptodome.Random import random
from Cryptodome.PublicKey import ElGamal
from Cryptodome.Util.number import GCD
from Cryptodome.Util.number import inverse
from Cryptodome.Util import number
""" from Crypto import Random
from Crypto.Random import random
from Crypto.PublicKey import ElGamal
from Crypto.Util.number import GCD
from Crypto.Util.number import inverse
from Crypto.Util import number """
import random as rnd
import math
from User import *

class Server:
    def __init__(self, m):
        self.m = m
        self.simMat = None
        self.user_list = []
        self.avg_ratings = None
    
    def setServerSimMat(self, simMat):
        self.simMat = simMat

    def addUser(self, user_to_add):
        self.user_list.append(user_to_add)
    
    def genElgamalKeys(self):
        self.p = 2494536251 #number.getPrime(32) # prime with generator 2
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
            #print("HEre: ", h)
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
            #print("Rating i", sum_plain_ratings[i])
            #print("flags i", sum_plain_flags[i])
            #average_result.append(inter_result) open if not stored as a multiple of 2
            average_result.append(inter_result/2)


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
            sim_round1_m.append(self.user_list[i].sim_round1_all(self.m, self.avg_ratings))
            print("Round 1 User: ", i)

        pairwise_m, pairwise_mults = self.multiplySimilarityRatings(sim_round1_m)
        
        round2_m = []

        for i in range(n):
            round2_m.append(self.user_list[i].sim_round2(pairwise_m))
            print("Round 2 User: ", i)
        #print(round2_m)
        decrypt_pairwise_m = []
        decrypt_denom = []

        print("Round2 Done")
        for i in range(self.m):
            temp_zero = []
            for j in range(self.m):
                temp_zero.append(0)
            decrypt_pairwise_m.append(temp_zero)
            decrypt_denom.append(0)    

        progress = 0
        for i in range(self.m):
            for j in range(self.m):
                base = 1
                for k in range(n):
                    base = base*round2_m[k][i][j] % self.p
                    progress += 1

                
                #decrypt_pairwise_m[i][j] = pairwise_mults[i][j][1] * inverse(base, self.p) % self.p
                decrypt_pairwise_m[i][j] = self.boundedDiscreteLog(pairwise_mults[i][j][1] * inverse(base, self.p) % self.p)
                #print("Decrypt i: ", i, " j: ", j, " Done!")
            print("Progress: %", 100*float(progress)/(self.m*self.m*n))
            decrypt_denom[i] = decrypt_pairwise_m[i][i]

        
        result_matrix = []
        for i in range(self.m):
            sim_vector = []
            for j in range(self.m):
                sim_vector.append(int(self.getSim(decrypt_pairwise_m[i][j], decrypt_denom[i], decrypt_denom[j])*100))
            result_matrix.append(sim_vector)
        
        #print(result_matrix)
        self.simMat = result_matrix

    def inv_pair(self, ct):
        return (inverse(ct[0], self.p), inverse(ct[1], self.p))

    def predict_rating(self, i, k):
        # predict rating of user i, item k denoted P_i,k
        enc_obj = ElGamal.construct((self.p, self.g, self.user_list[i].getPubKey()))
        
        encrypted_ratings = self.user_list[i].sendRatings(self.m)
        sum_of_sims = 0
        l = 10 #modified
        top_l = sorted(range(len(self.simMat[k])), key=lambda i: self.simMat[k][i])[-1*l:] #modified
        #print(top_l)
        #print(self.simMat[k])
        for j in range(self.m):
            if k != j:
                sum_of_sims += self.simMat[k][j]
        R_k = self.avg_ratings[k]*200
        
        #print(R_k)
        #print(sum_of_sims)
        #print(R_k*sum_of_sims)
        a = number.getRandomRange(2, self.p - 1, Random.new().read)
        first_term = elgEncrypt(enc_obj, pow(self.g, int(R_k*sum_of_sims), self.p), a)

        result = (1,1)
        result = self.addElgamal(result, first_term, self.p)
        for j in range(self.m):
            if k != j:
                a = number.getRandomRange(2, self.p - 1, Random.new().read)
                R_j = self.avg_ratings[j]*200
                denom = elgEncrypt(enc_obj, pow(self.g, int(R_j), self.p), a)
                denom_inv = self.inv_pair(denom)
                inter_result = self.addElgamal(encrypted_ratings[j], denom_inv, self.p)
                #inter_result = encrypted_ratings[j]
                inter_result = (inter_result[0]**self.simMat[k][j], inter_result[1]**self.simMat[k][j])
                result = self.addElgamal(result, inter_result, self.p)

        a = number.getRandomRange(2, self.p - 1, Random.new().read)
        encrypted_denom = elgEncrypt(enc_obj, pow(self.g, sum_of_sims, self.p), a)
        
        # send results to user obtain rating
        predicted_rating = self.user_list[i].calculate_prediction(result, encrypted_denom)
        
        result = predicted_rating/200
        #result = self.avg_ratings[k]# only the average
        if result > 5:
            result = 5
        return result
        #print("Rating: ", predicted_rating/100)
            
    def predict_plain_rating(self, i, k):
        l = 20 #modified
        top_l = sorted(range(len(self.simMat[k])), key=lambda j: self.simMat[k][j])[-1*l:] #modified
        sum_of_sims = 0
        ratings = self.user_list[i].sendPlainRatings()
        for a in range(self.m):
            if k != a: # and a in ratings:
                sum_of_sims += self.simMat[k][a]
        R_k = self.avg_ratings[k]*200
        first_term = int(R_k*sum_of_sims)
        result = 0
        
        sum_rat = 0
        rat_cnt = 0
        for r in ratings:
            sum_rat += ratings[r]
            rat_cnt += 1
        if rat_cnt == 0:
            user_avg = 0
        else:
            user_avg = sum_rat/rat_cnt
        
        user_avg = user_avg*200
        #print("user_avg: ", user_avg)
        for a in range(self.m):
            if a in ratings:
                R_a = self.avg_ratings[a]*200
                result = result + int(ratings[a] - R_a)*self.simMat[k][a]
            else:
                R_a = self.avg_ratings[a]*200
                
                result = result + int(user_avg - R_a)*self.simMat[k][a]

        if sum_of_sims == 0:
            return 0

        print("Nom:", result)
        print("Denom:", sum_of_sims)
        result = (first_term + result)/sum_of_sims

        result = result/200
        if result > 5:
            result = 5

        return result