import numpy as np
from DataParser import DataParser
from Statistics import Statistics
from pandas import DataFrame


class FeatureMatrixGenerator:

    def __init__(self, data, top_tags, top_staff):
        self.raw_data = data
        self.top_tags = top_tags
        self.top_staff = top_staff
        self.item_feature_matrix = np.array([])
        self.genres = ["Action", "Adventure", "Animation", "Children's", "Comedy", "Crime", "Documentary", "Drama",
                       "Fantasy", "Film-Noir", "Horror", "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller", "War",
                       "Western"]
        self.shape_matrix()

    def add_tag_cols(self):
        self.item_feature_matrix = np.hstack(self.item_feature_matrix, np.zeros((self.item_feature_matrix.shape[0], 1)))

    def generate_feature_matrix(self):
        self.add_tag_cols()

    def shape_matrix(self):
        # add 1 col representing the movie id
        # add 184 cols representing top-tags (asc. order) - not used for now
        # add 1 col representing the director
        # add 1 col representing the leading actor
        # 18 cols representing each genre in dataset
        # 9742 is the number of movies
        self.item_feature_matrix = np.zeros((9742, 1519), dtype="int")

    def populate_matrix(self):
        for i, movie in enumerate(self.raw_data.movies):
            m_id = movie[0]

            # insert movie id
            self.item_feature_matrix[i][0] = m_id

            # populate tag cols
            # m_tags = self.get_tags_by_movie(m_id)
            # for tag in m_tags:
            #     tag_idx = np.where(self.top_tags == tag)[0][0] + 1
            #     self.item_feature_matrix[i][tag_idx] = 1

            # populate actor cols - top 1499 staff
            m_actors = self.get_actors_by_movie(m_id)
            for actor in m_actors:
                actor_idx = [i[0] for i in self.top_staff].index(actor) + 1
                self.item_feature_matrix[i][actor_idx] = 1

            # populate director and actor cols - 1 dir, 1 actor approach
            # director, actor = self.get_director_and_actor(m_id)
            # self.item_feature_matrix[i][1] = director
            # self.item_feature_matrix[i][2] = actor

            # populate genres
            m_genres = self.get_genres_by_movie_id(m_id)
            for j, genre in enumerate(self.genres):
                if genre in m_genres:
                    self.item_feature_matrix[i][1500 + j] = 1

            print("movie " + str(i) + " done")

        print("matrix generation done")

    def get_genres_by_movie_id(self, m_id):
        df = DataFrame(self.raw_data.movies)
        m_info = np.array(df.loc[df[0] == m_id])

        return m_info[0][-1].split("|")

    def get_director_and_actor(self, m_id):
        director, actor = '', ''

        # find imdb id of the movie
        df = DataFrame(self.raw_data.links)
        imdb_id = np.array(df.loc[df[0] == m_id])[0][1]

        df = DataFrame(self.raw_data.staff)
        m_info = np.array(df.loc[df[0] == "tt" + imdb_id])

        # ToDo: returning only 1 director and 1 actor, could be better?
        for info in m_info:
            if info[2] == "director":
                director = info[1]
            elif info[2] == "actor":
                actor = info[1]

        return '1' + director[2:], '1' + actor[2:]

    def get_actors_by_movie(self, m_id):
        res = []

        df_links = DataFrame(self.raw_data.links)
        imdb_id = 'tt' + np.array(df_links.loc[df_links[0] == m_id])[0][1]

        df_staff = DataFrame(self.raw_data.staff)
        actors_by_mov = np.array(df_staff.loc[df_staff[0] == imdb_id])

        for actor in actors_by_mov:
            tmp = actor[1].lower().replace(" ", "")
            if tmp in [i[0] for i in self.top_staff]:
                res.append(tmp)

        return res

    def get_tags_by_movie(self, m_id):
        res = []

        df = DataFrame(self.raw_data.tags)
        tags_by_mov = np.array(df.loc[df[1] == m_id])

        for tag in tags_by_mov:
            tmp = tag[2].lower().replace(" ", "")
            if tmp in self.top_tags:
                res.append(tmp)

        return res


if __name__ == '__main__':
    data = DataParser()
    data.parse_data()
    stats = Statistics(data.tags, data.staff)
    fgm = FeatureMatrixGenerator(data, stats.get_top_tags(), stats.get_top_staff())
    fgm.populate_matrix()
