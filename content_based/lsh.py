from xxhash import xxh64_intdigest as hash


class LSH:
    def __init__(self, mm, r, b):
        self.mm = mm
        self.n = len(mm)
        self.m = len(mm[0])
        self.r = r
        self.b = b
        self.k = 3 * self.n
        self.bs = [[set() for j in range(self.k)] for i in range(self.b)]
        self.I = set()
        for i, l in enumerate(mm):
            self.I.add(i)
            for j in range(self.b):
                le = self.m // self.b
                band = l[le * j: le * (j + 1)]
                self.bs[j][hash(str(band)) % self.k].add(i)

    def find_sim(self, i):
        r = set()
        sig = self.mm[i]
        for j in range(self.b):
            le = self.m // self.b
            band = sig[le * j: le * (j + 1)]
            r |= self.bs[j][hash(str(band)) % self.k]

        return r

    def sim(self, i, j):
        assert len(self.mm[i]) == len(self.mm[j])
        l = len(self.mm[i])
        r = 0
        for k in range(l):
            if self.mm[i][k] == self.mm[j][k]:
                r += 1

        return r / l
