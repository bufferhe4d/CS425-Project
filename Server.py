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
            
        