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
import pickle

def elgEncrypt(encryptInfo, m, K):
        c1 = int(pow(encryptInfo.g,K,encryptInfo.p))
        c2 = m*int(pow(encryptInfo.y,K,encryptInfo.p )) % int(encryptInfo.p)
        return (c1, c2)
class User:
    def __init__(self, id):
        self.id = id
        self.avg_round1_m = None
        #self.sim_round1 = None
        self.ratings = {}
        self.p = None
        self.g = None
        self.privElgamalKey = None
        self.pubElgamalKey = None
        self.encryptObj = None
    
    def boundedDiscreteLog(self, pt):
        h = 0
        while h < self.p - 1:
            #print("HEre: ", h)
            if(pow(self.g, h, self.p) == pt):
                return h
            h += 1
        return None

    def setRating(self,ratings):
        self.ratings = ratings
    
    def genElgamalKey(self, p, g):
        # generate elgamal keys according to parameters
        self.p = p
        self.g = g
        self.privElgamalKey = number.getRandomRange(2, self.p - 1, Random.new().read)
        self.pubElgamalKey = pow(g, self.privElgamalKey, self.p)

    def getPubKey(self):
        return self.pubElgamalKey
    
    def setServerPubKey(self, Y):
        elgamal_tuple = (self.p, self.g, Y)
        # consturct elgamal object from the server public key
        self.encryptObj = ElGamal.construct(elgamal_tuple)

    def average_round1_all(self, num_item):
        if self.avg_round1_m != None:
            return self.avg_round1_m
        
        # do the encryption for all items
        result = []
        for j in range(num_item):
            result.append(self.average_round1(j))
        return result
    
    def average_round1(self, r):
        k1 = number.getRandomRange(2, self.p - 1, Random.new().read)
        k2 = number.getRandomRange(2, self.p - 1, Random.new().read)
        if r in self.ratings:
            flag = 1
            enc_rating = elgEncrypt(self.encryptObj, pow(self.g, self.ratings[r], self.p), k1)
            enc_flag = elgEncrypt(self.encryptObj, pow(self.g, flag, self.p), k2)
        else:
            flag = 0
            enc_rating = elgEncrypt(self.encryptObj, pow(self.g, flag, self.p), k1)
            enc_flag = elgEncrypt(self.encryptObj, pow(self.g, flag, self.p), k2)
        return (enc_rating, enc_flag) # corresponds to M_i^(1) = (E(g^r), E(g^f))

    def average_round2(self, ratings_A, flags_A):
        num_item = len(ratings_A)

        round2_m = []
        for i in range(num_item):
            decrypted_rating = pow(ratings_A[i], self.privElgamalKey, self.p)
            decrypted_flag = pow(flags_A[i], self.privElgamalKey, self.p)
            round2_m.append((decrypted_rating, decrypted_flag))

        return round2_m # Corresponds to M_i^(3) = (A_1^x, A_2^x)
    
    def sim_round1_all(self, num_item, avg_ratings):
        # send each similarity pair as a list
        all_pairs = []
        progress = 0
        for i in range(num_item):
            sim_pair = []
            for j in range(num_item):
                sim_pair.append(self.sim_round1(i,j, avg_ratings))
                #print("i: ", i, " j: ", j, "Done!")
                #progress+=1
            #print("Round1 Progress: %", 100*float(progress)/(num_item**2))
            all_pairs.append(sim_pair)
        
        return all_pairs

    def sim_round1(self, i, j, avg_ratings):
        k = number.getRandomRange(2, self.p - 1, Random.new().read)
        if (i in self.ratings) and (j in self.ratings):
            # multiply two ratings
            #print(self.ratings[i]*self.ratings[j])
            """  term1 = pow(self.g, int(self.ratings[i]*self.ratings[j]*10), self.p)
            term2 = pow(self.g, int(avg_ratings[i]*avg_ratings[j]*10), self.p)
            div1 = pow(self.g, int(self.ratings[i]*avg_ratings[j]*10), self.p)
            div2 = pow(self.g, int(avg_ratings[i]*self.ratings[j]*10), self.p)
            div1 = inverse(div1, self.p)
            div2 = inverse(div2, self.p)
            #pearson coeff test
            mult_rating = elgEncrypt(self.encryptObj, pow(self.g, term1*term2*div1*div2, self.p), k) """
            mult_rating = elgEncrypt(self.encryptObj, pow(self.g, (self.ratings[i])*(self.ratings[j]), self.p), k)
        else:
            # send 0
            mult_rating = elgEncrypt(self.encryptObj, pow(self.g, 0, self.p), k)
        
        return mult_rating
    
    def sim_round2(self, pairwise_m):
        num_item = len(pairwise_m)
        progress = 0
        round2_m = []
        for i in range(num_item):
            temp_row = []
            for j in range(num_item):
                inter_result = pow(pairwise_m[i][j], self.privElgamalKey, self.p)
                temp_row.append(inter_result)
                #progress +=1
            #print("Round2 Progress: %", 100*float(progress)/(num_item**2))
            round2_m.append(temp_row)
        return round2_m

    def sendRatings(self, num_item):
        enc_obj = ElGamal.construct((self.p, self.g, self.pubElgamalKey))
        encrypted_ratings = {}
        for i in range(num_item):
            k = number.getRandomRange(2, self.p - 1, Random.new().read)
            if i in self.ratings:
                encrypted_ratings[i] = elgEncrypt(enc_obj, pow(self.g, self.ratings[i]*100, self.p), k)
            else:
                temp = 1
                sum_rat = 0
                rat_cnt = 0
                for r in self.ratings:
                    sum_rat += self.ratings[r]
                    rat_cnt += 1
                if rat_cnt == 0:
                    user_avg = 0
                else:
                    user_avg = sum_rat/rat_cnt
                encrypted_ratings[i] = elgEncrypt(enc_obj, pow(self.g, int(user_avg*100), self.p), k)
        
        return encrypted_ratings

    def sendPlainRatings(self):
        return self.ratings

    def calculate_prediction(self, encrypted_nom, encrypted_denom):
        plain_nom = encrypted_nom[1]*inverse(pow(encrypted_nom[0], self.privElgamalKey, self.p), self.p)
        plain_denom = encrypted_denom[1]*inverse(pow(encrypted_denom[0], self.privElgamalKey, self.p), self.p)
        
        #print(self.boundedDiscreteLog(plain_nom % self.p))
        #print(self.boundedDiscreteLog(plain_denom % self.p))
        nom = self.boundedDiscreteLog(plain_nom % self.p)
        denom = self.boundedDiscreteLog(plain_denom % self.p)
        print("Nom", nom)
        print("Denom", denom)
        if denom == 0:
            prediction = 0
        else:
            prediction = nom/denom
        return prediction
        #print(prediction/100)