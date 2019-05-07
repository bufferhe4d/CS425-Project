from .paillier import Paillier


class Bob:
    k = 5
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
            vs.append((a, i))

        lut = dict()
        for p, _ in ps:
            t = p
            a = []
            for i in range(self.maxsim):
                a.append(t)
                t = (t * p) % c.n2
            lut[p] = a

        ws = []
        for i in I:
            w = 1
            for p, j in ps:
                w *= lut[p][self.sm[i][j] - 1]
                w = w % c.n2
            ws.append((w, i))

        return ws, vs
