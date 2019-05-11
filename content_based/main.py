from content_based.DataParser import DataParser
from content_based.FeatureMatrixGenerator import FeatureMatrixGenerator
from content_based.Statistics import Statistics
from content_based.MinHash import minHash
from content_based.lsh import LSH
from content_based.alice import Alice
from content_based.bob import Bob
import numpy as np


def reformat_rating_matrix(ratings_, fgm_):
    for i, (rating, mov_id) in enumerate(ratings_):
        ratings_[i][0] = int(float(ratings_[i][0])*2)
        ratings_[i][1] = np.where(fgm_.mov_id_matrix == int(mov_id))[0][0]

    return ratings_


if __name__ == '__main__':
    data = DataParser()
    data.parse_data()
    stats = Statistics(data.tags, data.staff)
    fgm = FeatureMatrixGenerator(data, stats.get_top_tags(), stats.get_top_staff())
    fgm.populate_matrix()

    sig = minHash(fgm.item_feature_matrix)
    lsh = LSH(sig, 2, 12)

    alice = Alice()
    bob = Bob(lsh)

    ratings = reformat_rating_matrix(data.ratings, fgm)[:5]
    enc_ratings = alice.encrypt_ratings(ratings)

    ws, vs = bob.recommend(enc_ratings, alice.get_pub())
    rec = alice.calc_recommendations(ws, vs)
    print("done")

