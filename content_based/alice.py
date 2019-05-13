from content_based.paillier import Paillier


class Alice:
    def __init__(self):
        pub, priv = Paillier.gen_key()
        self.c = Paillier(pub)
        self.c.set_priv(priv)

    def encrypt_ratings(self, ratings):
        p = []
        for r, i in ratings:
            p.append((self.c.enc(r), i))
        return p

    def get_pub(self):
        return self.c.n, self.c.g

    def calc_recommendations(self, w, v):
        assert len(w) == len(v)
        r = []
        for i in range(len(w)):
            r.append((self.c.dec(w[i][0]) / v[i][0], w[i][1]))

        return r

    def calc_prediction(self, w, v):
        return self.c.dec(w) / v