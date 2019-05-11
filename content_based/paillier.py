from Cryptodome.Util.number import getPrime, inverse, GCD, getRandomRange


class Paillier:

    def __init__(self, pub):
        self.n = pub[0]
        self.n2 = self.n * self.n
        self.g = pub[1]
        self.l = -1
        self.mu = -1

    def set_priv(self, priv):
        self.l = priv[0]
        self.mu = priv[1]

    @staticmethod
    def gen_key(prime_size = 1024):
        p = getPrime(prime_size)
        q = getPrime(prime_size)
        n = p * q
        g = n + 1
        phi = (p - 1) * (q - 1)
        l = phi
        mu = inverse(phi, n)

        return (n, g), (l, mu)

    def L(self, x):
        return (x - 1) // self.n

    def enc(self, m):
        assert m < self.n
        assert m >= 0

        r = getRandomRange(0, self.n)

        assert GCD(r, self.n) == 1

        return pow(self.g, m, self.n2) * pow(r, self.n, self.n2) % self.n2

    def dec(self, c):
        assert self.l != -1
        assert self.mu != -1
        return (self.L(pow(c, self.l, self.n2)) * self.mu) % self.n
