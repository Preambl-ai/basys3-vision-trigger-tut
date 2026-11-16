"""Small image classifier for the Basys 3 vision-trigger prototype."""

from torch import Tensor, nn


class EventCNN(nn.Module):
    """Score 32x32 grayscale crops normalized to [0, 1]."""

    def __init__(self) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 4, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2),
            nn.Conv2d(4, 8, kernel_size=3, padding=1),
            nn.ReLU(),
            # Keep a 2x2 grid so the score can depend on where the object is.
            nn.AvgPool2d(kernel_size=8),
        )
        self.classifier = nn.Sequential(nn.Flatten(), nn.Linear(8 * 2 * 2, 1))

    def forward(self, crops: Tensor) -> Tensor:
        """Return one raw score per crop, as a tensor of shape [batch, 1]."""
        return self.classifier(self.features(crops))
