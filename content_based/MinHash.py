import random
from gmpy2 import next_prime


def minHash(ifm, k=24):
    le = len(ifm)
    p = next_prime(le)
    a = [random.randrange(p) for i in range(k)]
    b = [random.randrange(p) for i in range(k)]
    mm = []
    for l in ifm:
        h = [len(l)] * k
        for i in range(len(l)):
            if l[i] == 1:
                for j in range(k):
                    h[j] = min(h[j], (a[j] * i + b[j]) % p)
        mm.append(h)
    return mm
