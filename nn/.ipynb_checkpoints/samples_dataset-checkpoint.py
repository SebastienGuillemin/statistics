import numpy as np
from torch.utils.data import Dataset


class SamplesDataset(Dataset):
    def __init__(self, tuples):
        self.pairs = []
        self.labels = []

        for tuple in tuples:
            self.pairs.append(tuple[0] + tuple[1])
            self.labels.append(tuple[2])

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        X, y = np.asarray(self.pairs[index]), np.array(self.labels[index])
        print(X, y)
        print(type(X))
        print(type(y))
        return X, y

    def get_positive_examples_number(self):
        return self.labels.count(1)

    def get_negative_examples_number(self):
        return self.labels.count(0)