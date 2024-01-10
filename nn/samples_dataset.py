import numpy as np
from torch.utils.data import Dataset
import torch
import random


class SamplesDataset(Dataset):
    def __init__(self, tuples=[]):
        self.pairs = []
        self.labels = []

        for tuple in tuples:
            self.pairs.append(np.asarray(tuple[0] + tuple[1]))
            self.labels.append(tuple[2])

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        X, y = torch.tensor(self.pairs[index], dtype=torch.float32), torch.tensor(self.labels[index], dtype=torch.float32)
        return X, y
    
    def add_examples(self, examples, labels):
        if len(examples) != len(labels):
            raise Exception(f'The number of examples {len(examples)} must be the same as the number of labels {len(labels)}.')
        
        for i in range(len(examples)):
            self.pairs.append(np.asarray(examples[i]))
            self.labels.append(labels[i])

    def get_positive_examples_number(self):
        return self.labels.count(1)

    def get_negative_examples_number(self):
        return self.labels.count(0)
    
    def get_row_dataset(self):
        return self.pairs, self.labels
    
    def shuffle(self):
        temp = list(zip(self.pairs, self.labels))
        random.shuffle(temp)
        
        new_pairs,  new_labels = zip(*temp)
        self.pairs = list(new_pairs)
        self.labels = list(new_labels)