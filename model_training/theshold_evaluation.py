import torch
import numpy as np
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt
from utils.context_dataset import CONTEXT_DATA
from torch.utils.data import DataLoader, Subset
from sklearn.model_selection import train_test_split
from train import TextClassifier

device = "cuda" if torch.cuda.is_available() else "cpu"

# --- Load Dataset (same split as training) ---
dataset = CONTEXT_DATA("./data/input.txt")
train_idx, val_idx = train_test_split(list(range(len(dataset))), test_size=0.2, random_state=1)
val_data = Subset(dataset, val_idx)
val_loader = DataLoader(val_data, batch_size=32, shuffle=False)

# --- Load Model ---
model = TextClassifier(dataset.input_dim, hidden_dim=128)
model.load_state_dict(torch.load("model_checkpoints/classifier__ep30_bs1_hn_128_lr1e-04_wd5e-04_08-29_10_dataset7.pth"))
model.to(device)
model.eval()

# --- Collect Predictions ---
all_labels, all_probs = [], []
with torch.no_grad():
    for sentences, labels in val_loader:
        sentences = sentences.to(device).float()
        outputs = model(sentences).cpu().numpy().flatten()
        all_probs.extend(outputs)
        all_labels.extend(labels.numpy())

# --- ROC & AUC ---
fpr, tpr, thresholds = roc_curve(all_labels, all_probs)
roc_auc = auc(fpr, tpr)
print(f"AUC: {roc_auc:.3f}")

# --- Plot ROC ---
plt.figure()
plt.plot(fpr, tpr, label=f"ROC Curve (AUC={roc_auc:.2f})")
plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")
plt.legend()
plt.show()

# --- Threshold Analysis ---
tpr_list = []
fpr_list = []
thresholds_to_test = [.1, .2, .3, .4, .5, .6, .7, .8, .9]
for th in thresholds_to_test:
    preds = (np.array(all_probs) >= th).astype(int)
    tp = ((preds == 1) & (np.array(all_labels) == 1)).sum()
    fn = ((preds == 0) & (np.array(all_labels) == 1)).sum()
    fp = ((preds == 1) & (np.array(all_labels) == 0)).sum()
    tn = ((preds == 0) & (np.array(all_labels) == 0)).sum()
    tpr_val = tp / (tp + fn) if (tp + fn) > 0 else 0
    fpr_val = fp / (fp + tn) if (fp + tn) > 0 else 0
    tpr_list.append(tpr_val)
    fpr_list.append(fpr_val)
    print(f"Threshold {th:.2f} -> TPR: {tpr_val:.3f}, FPR: {fpr_val:.3f}")
J = np.array(tpr_list) - np.array(fpr_list)
ix = np.argmax(J)
best_thresh = thresholds_to_test[ix]

print(f"\nBest threshold by Youden's J: {best_thresh:.2f} (TPR={tpr_list[ix]:.3f}, FPR={fpr_list[ix]:.3f})")