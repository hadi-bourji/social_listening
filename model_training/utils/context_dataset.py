from torch.utils.data import Dataset
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import os

class CONTEXT_DATA(Dataset):
        
    def __init__(self, data_path: str = "./data/input.txt"):
        if os.path.isfile(data_path):
            with open(data_path, 'r', encoding='utf-8') as f:
                self.sentences = [line.strip() for line in f if line.strip()]
        else:
            raise Exception(f"data_path {data_path} is not a valid file path")
        
        labels_path = data_path.replace("input", "labels")
        if os.path.isfile(labels_path):
            with open(labels_path, 'r', encoding='utf-8') as f:
                self.labels = [int(line.strip()) for line in f if line.strip()]
        else:
            raise Exception(f"data_path {labels_path} is not a valid file path")
        
        self.vectorizer = CountVectorizer()
        self.X = self.vectorizer.fit_transform(self.sentences).toarray()
        self.input_dim = self.X.shape[1]

    
    def __getitem__(self, idx):
        return self.X[idx], self.labels[idx]
    

    def __len__(self):
        return len(self.sentences)