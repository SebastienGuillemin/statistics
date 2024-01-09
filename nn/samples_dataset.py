from torch.utils.data import Dataset

class SamplesDataset(Dataset):
    def __init__(self, tuples):
        self.pairs = []
        self.labels = []

        for tuple in tuples:
            self.pairs.append((tuple[0], tuple[1]))
            self.labels.append(tuple[2])

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        return self.pairs[index], self.labels[index]