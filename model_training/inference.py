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
    model.load_state_dict(torch.load("model_checkpoints/classifier__ep30_bs1_hn_128_lr1e-04_wd5e-04_08-29_10_dataset7.pth", map_location=device))
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
        label = "Relevant article" if pred == 1 else "Not a relevant article"
        print(f"{label}: {sent}\n")


if __name__ == "__main__":
    sentences = ["Chemical plant explosion results in millions in damage.", 
             "Wildfire causes damage across multiple counties.", 
             "Students evacuate after gas leak.", "St. Louis County police rule out crime in house explosion, say it's 'likely' gas incident", 
             "The coffee spill in the office ruined several documents.", "A cooking gas cylinder was replaced in the restaurant without incident.",
             "The school science fair featured experiments with dry ice and colored smoke.",
             "780,000 pressure washers are under recall after some consumers report explosions and impact injuries",
             "TRINTY COUNTY SHERIFF: 3 dead due to gas leak in Trinity County, bodies recovered",
             "-A hazardous materials incident shut down both directions of I-70 and Highway 40 early Wednesday morning, triggering a chain reaction of semi-trucks diverting onto unsuitable side roads.",
             "Man who died in Sacramento home explosion is identified",
             "-New EPA data shows PFAS, or forever chemicals, in 200 more drinking water systems nationwide, including Durham and Fayetteville, as NC utilities work to remove them.",
             "Fort McHenry channel closing to recover hatch from coal ship that exploded",
             "-In recent years, Maines work to combat PFAS has been marked by learning, listening, collaborating and acting decisively.",
             "-Interstate 70 was closed in both directions west of Denver while crews responded to a hydrochloric acid leak Wednesday morning.",
             "Gas leak prompts evacuation at Fort Lupton community college",
             "St. Louis County police rule out crime in house explosion, say it's 'likely' gas incident",
             "Without hesitation, a nurse at the hospital who was not assigned to respond to the mass casualty event sat with the young girl throughout the procedure even though safety protocols stipulate that medical staff should clear the room to prevent radiation exposure.",
             "'Take meaningful action:' Parents of students killed in Minneapolis church shooting share emotional pleas",
             "Road worker returns home after losing leg in work zone crash that killed colleague",
             "The county previously confirmed to KCRA 3 that the site where the deadly fireworks explosion occurred was not properly zoned to store fireworks.",
             "Colorado sues Aurora mobile home park for failing to notify residents about contaminated water",
             "He said the roadway was closed overnight due to a fuel leak and traffic was diverted onto Ives Dairy Road.",
             "Longtime Broward teacher accused of sexually assaulting student South Florida news reporter turns himself into Miami police following Rolex theft, pawning After months in ICE detention, federal judge squashes dream of family reunion in Coral Springs New Florida Buc-ee’s location could be in the works Mother of slain 14-year-old boy says murder suspect ‘kept threatening him’ before stabbing in Broward From mold in the tomato paste to roaches and rodents, multiple restaurants ordered shut!",
             "New EPA data shows PFAS, or forever chemicals, in 200 more drinking water systems nationwide, including Durham and Fayetteville, as NC utilities work to remove them.",
             "In recent years, Maine’s work to combat PFAS has been marked by learning, listening, collaborating and acting decisively.",
             "Mold. Mold. Mold.’ Former Cedar Point workers describe dorm conditions, park pushes back",
             "Former employees allege years of mold complaints in Cedar Point dorms, while health officials and the park say inspections show no current issues."

             
             ]
    filter(sentences)