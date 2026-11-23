"""Train a compact CIFAR-10 candidate; select checkpoints using validation only."""

import argparse
import json
import platform
import random
from pathlib import Path
from time import perf_counter

import numpy as np
import torch
import torch.nn.functional as F

from cifar10_inputs import DATASET_SHA256, load_training_set, training_indices
from compact_model import ARCHITECTURE, CompactCNN, resource_counts


def augment(images):
    """Independent four-pixel reflection crops and horizontal flips per image."""
    padded = F.pad(images, (4, 4, 4, 4), mode="reflect")
    count = len(images)
    offsets = torch.randint(0, 9, (count, 2))
    rows = offsets[:, 0, None, None] + torch.arange(32)[None, :, None]
    cols = offsets[:, 1, None, None] + torch.arange(32)[None, None, :]
    crops = padded.permute(0, 2, 3, 1)[torch.arange(count)[:, None, None], rows, cols]
    crops = crops.permute(0, 3, 1, 2).contiguous()
    return torch.where(torch.rand(count, 1, 1, 1) < 0.5, crops.flip(3), crops)


def accuracy(model, images, labels, batch_size=256):
    model.eval()
    correct = 0
    with torch.inference_mode():
        for start in range(0, len(labels), batch_size):
            scores = model(images[start:start + batch_size].float().div(255))
            correct += int((scores.argmax(1) == labels[start:start + batch_size]).sum())
    return 100 * correct / len(labels)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("runs/compact-cifar10/seed-42"))
    args = parser.parse_args()
    if min(args.epochs, args.batch_size, args.threads) < 1:
        parser.error("epochs, batch size, and threads must be positive")
    if args.output.exists() and any(args.output.iterdir()):
        parser.error("output directory must be empty; choose a new run directory")
    args.output.mkdir(parents=True, exist_ok=True)
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    raw, targets = load_training_set()
    train, validation = training_indices(targets, args.seed)
    np.savez_compressed(args.output / "split.npz", train=train, validation=validation,
                        dataset_sha256=DATASET_SHA256)
    images = torch.from_numpy(raw.transpose(0, 3, 1, 2).copy())
    labels = torch.from_numpy(targets)
    train_images, train_labels = images[train], labels[train]
    val_images, val_labels = images[validation], labels[validation]
    model = CompactCNN()
    resources = resource_counts(model.eval())
    config = {**vars(args), "output": str(args.output), "architecture": ARCHITECTURE,
              "dataset_sha256": DATASET_SHA256, "training_images": len(train),
              "validation_images": len(validation), "test_images_used_in_training": 0,
              "preprocessing": "RGB NCHW float32 / 255; train-only reflection crop and flip",
              "optimizer": "AdamW lr=0.003 weight_decay=0.0005; cosine to 0.00003",
              "checkpoint_selection": "highest validation accuracy; earliest epoch wins ties",
              "torch": torch.__version__, "numpy": np.__version__,
              "python": platform.python_version(), "platform": platform.platform(),
              "resources": resources}
    (args.output / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.003, weight_decay=0.0005)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, args.epochs, eta_min=0.00003)
    history, best = [], -1.0
    started = perf_counter()
    for epoch in range(1, args.epochs + 1):
        epoch_start = perf_counter()
        model.train()
        order = torch.randperm(len(train))
        loss_sum, correct = 0.0, 0
        for indices in order.split(args.batch_size):
            batch = augment(train_images[indices].float().div(255))
            expected = train_labels[indices]
            optimizer.zero_grad(set_to_none=True)
            scores = model(batch)
            loss = F.cross_entropy(scores, expected)
            if not torch.isfinite(loss):
                raise ValueError("Non-finite training loss")
            loss.backward()
            optimizer.step()
            loss_sum += float(loss.detach()) * len(indices)
            correct += int((scores.detach().argmax(1) == expected).sum())
        val = accuracy(model, val_images, val_labels)
        row = {"epoch": epoch, "train_loss": loss_sum / len(train),
               "train_accuracy_percent": 100 * correct / len(train),
               "validation_accuracy_percent": val,
               "learning_rate": optimizer.param_groups[0]["lr"],
               "seconds": perf_counter() - epoch_start}
        history.append(row)
        if val > best:
            best = val
            torch.save({"state_dict": model.state_dict(), "architecture": ARCHITECTURE,
                        "seed": args.seed, "epoch": epoch, "validation_accuracy_percent": val,
                        "dataset_sha256": DATASET_SHA256}, args.output / "best.pt")
        scheduler.step()
        (args.output / "history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
        print(f"Epoch {epoch}/{args.epochs}: loss={row['train_loss']:.4f}, "
              f"validation={val:.2f}%, best={best:.2f}%, {row['seconds']:.1f}s", flush=True)
    (args.output / "summary.json").write_text(json.dumps({"best_validation_percent": best,
        "total_seconds": perf_counter() - started, "epochs": args.epochs,
        "official_test_evaluated": False}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
