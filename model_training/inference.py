import torch
import pickle
from train import TextClassifier
from utils.context_dataset import CONTEXT_DATA

device = "cuda" if torch.cuda.is_available() else "cpu"

dataset = CONTEXT_DATA("./data/input.txt")

model = TextClassifier(input_dim=dataset.input_dim, hidden_dim=128)
model.load_state_dict(torch.load("model_checkpoints/classifier__ep100_bs1_hn_128_lr1e-04_wd5e-04_08-28_12_dataset4.pth", map_location=device))
model.eval().to(device)

with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

sentences = ["Chemical plant explosion results in millions in damage.", "Wildfire causes damage across multiple counties.", 
             "Students evacuate after gas leak."]
X = vectorizer.transform(sentences).toarray()
X_tensor = torch.tensor(X, dtype=torch.float32).to(device)

with torch.no_grad():
    outputs = model(X_tensor)
    predictions = (outputs > 0.5).long()

print(outputs)     
print(predictions)   
