from Cryptodome import Random
from Cryptodome.Random import random
from Cryptodome.PublicKey import ElGamal
from Cryptodome.Util.number import GCD
from Cryptodome.Util.number import inverse
from Cryptodome.Util import number
import random as rnd

class Server:
    def __init__(self, m):
        self.m = m
        self.simMat = None
        self.user_list = []
    
    def addUser(self, user_to_add):
        self.user_list.append(user_to_add)
    