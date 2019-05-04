from Cryptodome import Random
from Cryptodome.Random import random
from Cryptodome.PublicKey import ElGamal
from Cryptodome.Util.number import GCD
from Cryptodome.Util.number import inverse
from Cryptodome.Util import number
import random as rnd

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
    
    def sim_round1_all(self, num_item):
        # send each similarity pair as a list
        all_pairs = []
        for i in range(num_item):
            sim_pair = []
            for j in range(num_item):
                sim_pair.append(self.sim_round1(i,j))
            all_pairs.append(sim_pair)
        
        return all_pairs

    def sim_round1(self, i, j):
        k = number.getRandomRange(2, self.p - 1, Random.new().read)
        if (i in self.ratings) and (j in self.ratings):
            # multiply two ratings
            mult_rating = elgEncrypt(self.encryptObj, pow(self.g, self.ratings[i]*self.ratings[j], self.p), k)
        else:
            # send 0
            mult_rating = elgEncrypt(self.encryptObj, pow(self.g, 0, self.p), k)
        
        return mult_rating
    
    def sim_round2(self, pairwise_m):
        num_item = len(pairwise_m)

        round2_m = []
        for i in range(num_item):
            temp_row = []
            for j in range(num_item):
                inter_result = pow(pairwise_m[i][j], self.privElgamalKey, self.p)
                temp_row.append(inter_result)
            round2_m.append(temp_row)
        return round2_m

    