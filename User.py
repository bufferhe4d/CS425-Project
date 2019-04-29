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
        self.avg_round1 = None
        self.sim_round1 = None
        self.ratings = {}
        self.p = None
        self.g = None
        self.privElgamalKey = None
        self.pubElgamalKey = None
    
    def setRating(self,ratings):
        self.ratings = ratings
    
    def genElgamalKey(self, p, g):
        self.p = p
        self.g = g
        self.privElgamalKey = number.getRandomRange(2, self.p - 1, Random.new().read)
        self.pubElgamalKey = pow(g, self.privElgamalKey, self.p)
