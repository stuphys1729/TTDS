import re

class RegexpTokenizer():

    def __init__(self, regexp):

        self.pattern = regexp

    def tokenize(self, text):
        return re.findall(self.pattern, text)
