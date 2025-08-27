import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from utils.context_dataset import CONTEXT_DATA
from torch.optim import AdamW
from torch.utils.tensorboard import SummaryWriter
from sklearn.model_selection import train_test_split
from tqdm import tqdm
from datetime import datetime


class TextClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1))
    
    def forward(self, x):
        return torch.sigmoid(self.fc(x))


def train(num_epochs, batch_size, device, hidden_nodes, lr, weight_decay, model_name):

    dataset = CONTEXT_DATA("./data/input.txt")

    train_idx, val_idx = train_test_split(list(range(len(dataset))), test_size=0.2, random_state=1)
    train_data = torch.utils.data.Subset(dataset, train_idx)
    val_data   = torch.utils.data.Subset(dataset, val_idx)

    train_loader = DataLoader(train_data, batch_size, shuffle=True)
    val_loader   = DataLoader(val_data, batch_size, shuffle=False)


    today = datetime.today()
    date_str = today.strftime("%m-%d_%H")
    exp_name = f"{model_name}__ep{num_epochs}_bs{batch_size}_lr{lr:.0e}_wd{weight_decay:.0e}_{date_str}"

    model = TextClassifier(dataset.input_dim, hidden_nodes)
    model.train().to(device)

    loss_fn = nn.BCELoss()
    optimizer = AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)

    writer = SummaryWriter(log_dir=f"./logs/{exp_name}")
    writer.add_text("Hyperparameters", f"num_epochs: {num_epochs}, "
                                            f"batch_size: {batch_size}")

    for epoch in tqdm(range(num_epochs), desc="Training Epochs", unit="epoch"):
        
        running_train_loss = 0.0
        running_val_loss = 0.0

        for batch in tqdm(train_loader, desc="Training Batches", unit="batch", total = len(train_loader)):
            sentence, labels = batch
            sentence = sentence.to(device).float()
            labels = labels.to(device).float().unsqueeze(1)
            
            outputs = model(sentence)
            loss = loss_fn(outputs, labels.float())

            running_train_loss += loss.item()

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        for batch in tqdm(val_loader, desc="Validation Batches", unit="batch", total = len(val_loader)):
            sentence, labels = batch
            sentence = sentence.to(device).float()
            labels = labels.to(device).float().unsqueeze(1)
            
            outputs = model(sentence)
            loss = loss_fn(outputs, labels.float())

            running_val_loss += loss.item()


            
        train_loss = running_train_loss / len(train_loader)
        val_loss = running_val_loss / len(val_loader)
            
        writer.add_scalar("Total Loss/Train", train_loss, epoch)
        writer.add_scalar("Total Loss/Val", val_loss, epoch)

    # save written table
    torch.save(model.state_dict(), f"model_checkpoints/{exp_name}.pth")


    writer.close()

if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    train(
        num_epochs=100,
        batch_size=1,
        device=device,
        hidden_nodes=64,
        lr=0.0001,
        weight_decay=0.0005,
        model_name="classifier"
    )