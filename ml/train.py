"""Train the pilot CNN and evaluate it on a separate camera recording."""

from pathlib import Path

import cv2
import torch
from torch import Tensor, nn

from model import EventCNN

DATASET = Path("data/processed/eraser-pilot")
CHECKPOINT = Path("runs/eraser-pilot/model.pt")
LABELS = ("normal", "out-of-position")


def load_split(split: str) -> tuple[Tensor, Tensor, list[Path]]:
    images = []
    labels = []
    paths = []
    for label, name in enumerate(LABELS):
        folder = DATASET / split / name
        files = sorted(folder.glob("*.png"))
        if not files:
            raise ValueError(f"No labeled PNGs found in {folder}")
        for path in files:
            image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
            if image is None or image.shape != (32, 32) or image.dtype.name != "uint8":
                raise ValueError(f"Expected an 8-bit grayscale 32x32 PNG: {path}")
            images.append(torch.from_numpy(image))
            labels.append(label)
            paths.append(path)
    crops = torch.stack(images).unsqueeze(1).float().div(255)
    return crops, torch.tensor(labels, dtype=torch.float32).unsqueeze(1), paths


def main() -> None:
    torch.manual_seed(42)
    torch.set_num_threads(1)
    train_crops, train_labels, _ = load_split("train")
    test_crops, test_labels, test_paths = load_split("test")

    model = EventCNN()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    positives = train_labels.sum()
    # Give normal and out-of-position crops equal weight in the training loss.
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=(train_labels.numel() - positives) / positives)
    model.train()
    print(f"Training on {len(train_crops)} images")
    for _ in range(500):
        optimizer.zero_grad()
        loss = loss_fn(model(train_crops), train_labels)
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.inference_mode():
        predictions = (model(test_crops) >= 0).flatten().tolist()
    expected = test_labels.flatten().long().tolist()
    for path, actual, predicted in zip(test_paths, expected, predictions):
        print(f"{path.stem}: expected {LABELS[actual]}, predicted {LABELS[predicted]}")
    correct = sum(actual == predicted for actual, predicted in zip(expected, predictions))
    print(f"Separate test recording: {correct}/{len(expected)} correct")

    CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model_state_dict": model.state_dict(), "labels": LABELS}, CHECKPOINT)
    print(f"Saved checkpoint to {CHECKPOINT}")


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        raise SystemExit(str(error)) from error
