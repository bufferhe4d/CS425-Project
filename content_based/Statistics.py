from DataParser import DataParser


class Statistics:

    def __init__(self, tag_data):
        self.tag_data = tag_data
        self.tag_occurrence = dict()
        self.top_tags = list()

    def get_top_tags(self):
        for i in self.tag_data:
            tag = i[2].lower().replace(" ", "")
            if tag in self.tag_occurrence:
                self.tag_occurrence[tag] += 1
            else:
                self.tag_occurrence[tag] = 1

        # Add the tags whose occurrence is >= 5 and do no add "in netflix queue"
        self.top_tags = sorted(self.tag_occurrence.items(), key=lambda kv: kv[1])
        self.remove_unused_tags()
        return self.top_tags

    def get_num_top_tags(self):
        return len(self.top_tags)

    def remove_unused_tags(self):
        end = 0
        for i, tag in enumerate(self.top_tags):
            if tag[1] < 5:
                end += 1
            else:
                del self.top_tags[0:end]
                return


def main():
    data = DataParser()
    data.parse_data()
    stats = Statistics(data.tags)
    stats.get_top_tags()


if __name__ == '__main__':
    main()
