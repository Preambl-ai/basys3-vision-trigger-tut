"""Small RGB classifier with ordinary convolutions and quantization boundaries."""

import torch
from torch import nn

ARCHITECTURE = "compact-cifar10-8-16-32-v1"


class CompactCNN(nn.Module):
    """Six 3x3 convolutions, three pools, global average, and ten logits.

    Inputs are NCHW RGB float32 in [0, 1]. No pretrained weights are used.
    Batch normalization is folded into convolutions before INT8 conversion.
    """

    def __init__(self):
        super().__init__()
        self.quant = torch.ao.quantization.QuantStub()
        stages = []
        previous = 3
        for channels in (8, 16, 32):
            for _ in range(2):
                stages.append(nn.Sequential(
                    nn.Conv2d(previous, channels, 3, padding=1, bias=False),
                    nn.BatchNorm2d(channels),
                    nn.ReLU(),
                ))
                previous = channels
            stages.append(nn.MaxPool2d(2))
        self.features = nn.Sequential(*stages)
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.classifier = nn.Linear(32, 10)
        self.dequant = torch.ao.quantization.DeQuantStub()

    def forward(self, images):
        x = self.features(self.quant(images))
        return self.dequant(self.classifier(self.pool(x).flatten(1)))

    def fuse(self):
        if self.training:
            raise ValueError("Fusion requires evaluation mode")
        for layer in self.features:
            if isinstance(layer, nn.Sequential):
                torch.ao.quantization.fuse_modules(layer, ["0", "1", "2"], inplace=True)


def resource_counts(model: nn.Module) -> dict:
    """Count dense products and kernel storage before fusion/quantization."""
    layers, hooks = [], []

    def record(module, inputs, output):
        weights = module.weight.numel()
        positions = output.shape[2] * output.shape[3] if isinstance(module, nn.Conv2d) else 1
        layers.append({"kind": type(module).__name__, "output_shape": list(output.shape),
                       "kernel_parameters": weights, "dense_macs": weights * positions})

    for layer in model.modules():
        if isinstance(layer, (nn.Conv2d, nn.Linear)):
            hooks.append(layer.register_forward_hook(record))
    try:
        with torch.inference_mode():
            model(torch.zeros(1, 3, 32, 32))
    finally:
        for hook in hooks:
            hook.remove()
    kernels = sum(layer["kernel_parameters"] for layer in layers)
    return {"trainable_parameters": sum(p.numel() for p in model.parameters()),
            "kernel_parameters": kernels, "kernel_weight_bytes": kernels * 4,
            "int8_kernel_weight_bytes": kernels,
            "dense_macs_per_image": sum(layer["dense_macs"] for layer in layers),
            "layers": layers}
