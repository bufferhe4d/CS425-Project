from Cryptodome import Random
from Cryptodome.Random import random
from Cryptodome.PublicKey import ElGamal
from Cryptodome.Util.number import GCD
from Cryptodome.Util.number import inverse
from Cryptodome.Util import number
import random as rnd

class User:
    def __init__(self, id):
        self.id = id
        self.avg_round1_m = None
        self.sim_round1 = None
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
        self.encryptObj = ElGamal.consturct(elgamal_tuple)

    def average_round1_all(self, num_item):
        if self.avg_round1_m != None:
            return self.avg_round1_m
        
        # do the encryption for all items
        result = []
        for j in range(m):
            result.append(self.average_round1(j))
        return result
    
    def average_round1(self, r):
        k1 = number.getRandomRange(2, self.p - 1, Random.new().read)
        k2 = number.getRandomRange(2, self.p - 1, Random.new().read)
        if r in self.ratings:
            flag = 1
            enc_rating = elgEncrypt(self.encryptObj, pow(self.g, self.ratings[r], self.p), k1)
            enc_flag = elgEncrypt(self.encryptObj, pow(self.g, flag, self.p), k1)
        else:
            flag = 0
            enc_rating = elgEncrypt(self.encryptObj, pow(self.g, flag, self.p), k1)
            enc_flag = elgEncrypt(self.encryptObj, pow(self.g, flag, self.p), k1)
        return (enc_rating, enc_flag) # corresponds to M_i = (E(g^r), E(g^f))
