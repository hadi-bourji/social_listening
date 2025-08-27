import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from utils.context_dataset import CONTEXT_DATA
from torch.optim import AdamW
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm


class TextClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1))
    
    def forward(self, x):
        return torch.sigmoid(self.fc(x))


def train(num_epochs = 10, validate = False, batch_size = 1, logging = True, device="cpu", hidden_nodes = 64, lr = 0.001, weight_decay = 0.0005, model_name = "classifier"):

    dataset = CONTEXT_DATA("./data/input.txt", "train")
    dataloader = DataLoader(dataset, batch_size, shuffle=True)
    exp_name = f"{model_name}__ep{num_epochs}_bs{batch_size}_lr{lr:.0e}_wd{weight_decay:.0e}"
    
    model = TextClassifier(dataset.input_dim, hidden_nodes)
    model.train().to(device)

    loss_fn = nn.BCELoss()
    optimizer = AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)

    if logging:
        writer = SummaryWriter(log_dir=f"./logs/{exp_name}")
        writer.add_text("Hyperparameters", f"num_epochs: {num_epochs}, "
                                            f"batch_size: {batch_size}")

    for epoch in tqdm(range(num_epochs), desc="Training Epochs", unit="epoch"):
        
        running_train_loss = 0.0

        for batch in tqdm(dataloader, desc="Training Batches", unit="batch", total = len(dataloader)):
            sentence, labels = batch
            sentence = sentence.to(device).float()
            labels = labels.to(device).float().unsqueeze(1)
            
            # with torch.autocast(device_type=device, dtype = torch.float16):
            outputs = model(sentence)
            loss = loss_fn(outputs, labels.float())

            running_train_loss += loss.item()

            # Backward pass and optimization
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
        train_loss = running_train_loss / len(dataloader)
            
        if logging:
            writer.add_scalar("Total Loss/Train", train_loss, epoch)

    # save written table
    torch.save(model.state_dict(), f"model_checkpoints/{exp_name}.pth")

    if logging:
        writer.close()

if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    train(
        num_epochs=100,
        validate=False,
        batch_size=1,
        logging=True,
        device=device,
        hidden_nodes=64,
        lr=0.0001,
        weight_decay=0.0005,
        model_name="classifier"
    )