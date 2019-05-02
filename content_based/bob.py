from .paillier import Paillier


class Bob:
    k = 10
    maxsim = 2**k

    def __init__(self, sm, delta=0.1):
        self.sm = sm
        self.delta = delta

    def recommend(self, ps, pub):
        c = Paillier(pub)
        I = []
        # possibly make this faster
        for j in len(self.sm):
            satisfy = True
            for _, i in ps:
                if self.sm[i][j] <= self.maxsim * self.delta:
                    satisfy = False
                    break
            if satisfy:
                I.append(j)

        vs = []
        for i in range(len(I)):
            a = 0
            for _, j in range(ps):
                a += self.sm[i][j]
            vs.append(a)

        lut = []
        for i in
        ws = []




