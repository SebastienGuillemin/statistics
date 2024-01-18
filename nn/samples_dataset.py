import numpy as np
from torch.utils.data import Dataset
import torch
import pandas as pd 


class SamplesDataset(Dataset):
    def __init__(self, tuples=[], columns_names=[]):
        self.columns_names = columns_names
        self.pairs = []
        self.labels = []

        for tuple in tuples:
            self.pairs.append(np.asarray(tuple[0] + tuple[1]))
            self.labels.append(tuple[2])

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        X = torch.tensor(self.pairs[index], dtype=torch.float32)
        y = torch.tensor(self.labels[index], dtype=torch.float32)
        return X, y
    
    def get_columns_names(self):
        return self.columns_names
    
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
    
    def export_as_csv(self, path):
        X_as_array = np.asarray(self.pairs)
        y_as_array = np.asarray([self.labels]).T
        concat = np.concatenate((X_as_array, y_as_array), axis=1)
        
        df_columns_names = self.columns_names + ['label']
        
        df = pd.DataFrame(concat, columns=df_columns_names)
        df.to_csv(path, index=False)
        
    def load_csv(self, path):
        df = pd.read_csv(path)
        df_columns_count = len(df.columns)
        
        labels_df = df.iloc[:, df_columns_count - 1]
        self.labels = labels_df.values.tolist()
        
        pairs_df = df.drop(df.columns[df_columns_count - 1], axis=1)
        self.pairs = pairs_df.to_numpy()       
        