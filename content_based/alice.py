from .paillier import Paillier


class Alice:
    def __init__(self, ratings):
        self.ratings = ratings
        pub, priv = Paillier.gen_key()
        self.c = Paillier(pub)
        self.c.set_priv(priv)

    def encrypt_ratings(self):
        p = []
        for r, i in self.ratings:
            p.append((self.c.enc(r), i))
        return p

    def get_pub(self):
        return self.c.n, self.c.g

    def calc_recommendations(self, w, v, idx):
        assert len(w) == len(v)
        r = []
        for i in range(len(w)):
            r.append(self.c.dec(w[i]) / v[i], idx[i])

        return r