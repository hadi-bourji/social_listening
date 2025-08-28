import torch
import pickle
from train import TextClassifier
from utils.context_dataset import CONTEXT_DATA
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

def filter(sentences):

    device = "cuda" if torch.cuda.is_available() else "cpu"

    #pull in dataset object to get size of vocabulary/features to build model input layer and load parameters
    dataset = CONTEXT_DATA("./data/input.txt")
    model = TextClassifier(input_dim=dataset.input_dim, hidden_dim=128)
    model.load_state_dict(torch.load("model_checkpoints/classifier__ep100_bs1_hn_128_lr1e-04_wd5e-04_08-28_13_dataset5.pth", map_location=device))
    model.eval().to(device)

    #load in vectorizer from training since it has the vocabulary words in order 
    with open("vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)

    X = vectorizer.transform(sentences).toarray()
    X_tensor = torch.tensor(X, dtype=torch.float32).to(device)

    with torch.no_grad():
        outputs = model(X_tensor)
        predictions = (outputs > 0.5).long().cpu().numpy()
    # print(outputs)  ##good for testing since it shows how confident the model is in its prediction     
    # print(predictions)   

    for sent, pred in zip(sentences, predictions):
        label = "Relevant" if pred == 1 else "Irrelevant"
        print(f"{label}: {sent}")

sentences = ["Chemical plant explosion results in millions in damage.", "Wildfire causes damage across multiple counties.", 
             "Students evacuate after gas leak.", "St. Louis County police rule out crime in house explosion, say it's 'likely' gas incident", 
             "The coffee spill in the office ruined several documents.", "A cooking gas cylinder was replaced in the restaurant without incident.",
             "The school science fair featured experiments with dry ice and colored smoke."]
filter(sentences)