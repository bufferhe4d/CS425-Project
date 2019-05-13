from .paillier import Paillier


class Bob:
    k = 5
    maxsim = 2 ** k

    def __init__(self, lsh):
        self.lsh = lsh

    def recommend(self, ps, pub):
        c = Paillier(pub)
        I = self.lsh.I
        """
        # possibly make this faster
        for j in len(self.sm):
            satisfy = True
            for _, i in ps:
                if self.sm[i][j] <= self.maxsim * self.delta:
                    satisfy = False
                    break
            if satisfy:
                I.append(j)
        """
        for _, i in ps:
            I &= self.lsh.find_sim(i)

        vs = []
        for i in I:
            a = 0
            for _, j in ps:
                s = int(self.lsh.sim(i, j) * self.maxsim)
                if s < 1:
                    continue
                a += s
            if a == 0:
                I.remove(i)
                continue
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
                s = int(self.lsh.sim(i, j) * self.maxsim)
                if s < 1:
                    continue
                w *= lut[p][s - 1]
                w = w % c.n2
            ws.append((w, i))

        return ws, vs

    def predict(self, ps, pub, item):
        c = Paillier(pub)
        v = 0
        for _, j in ps:
            s = int(self.lsh.sim(item, j) * self.maxsim)
            if s < 1:
                continue
            v += s
        w = 1
        for p, j in ps:
            s = int(self.lsh.sim(item, j) * self.maxsim)
            if s < 1:
                continue
            w *= pow(p, s, c.n2)

        return w, v
