"""Download and verify inputs for the CIFAR-10 laptop benchmark."""

from __future__ import annotations

import hashlib
import pickle
import shutil
import sys
import tarfile
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

import numpy as np

ASSETS = Path("runs/cifar10-baseline/assets")
MLPERF_REVISION = "4addd0fa08d216e20637637874e084895f289da4"
MODEL_DIRECTORY_URL = (
    f"https://raw.githubusercontent.com/mlcommons/tiny/{MLPERF_REVISION}/"
    "benchmark/training/image_classification/trained_models"
)
MODEL_SHA256 = "b5c0046d6e0328b4956afd6baa29555a29b1f1c65bdd45aaed75b7cd484d9f79"
INT8_MODEL_SHA256 = "3c002613d1b2475eb51dd78dfb85a546c8ae658dee71cf6ade43b022fe205415"
INT8_INPUT_QUANTIZATION = (1.0, -128)
INT8_OUTPUT_QUANTIZATION = (1 / 256, -128)
DATASET_URL = "https://storage.googleapis.com/tensorflow/tf-keras-datasets/cifar-10-python.tar.gz"
DATASET_SHA256 = "6d958be074577803d12ecdefd02955f39262c83c16fe9348329d7fe0b5c001ce"
IMAGE_SHAPE = (32, 32, 3)
TEST_IMAGES = 10_000
CLASS_COUNT = 10


def sha256(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def verified_asset(name: str, url: str, checksum: str) -> Path:
    destination = ASSETS / name
    if destination.is_file() and sha256(destination) == checksum:
        return destination

    destination.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {name}", file=sys.stderr, flush=True)
    temporary = NamedTemporaryFile(dir=destination.parent, delete=False)
    pending = Path(temporary.name)
    try:
        with temporary, urlopen(url, timeout=60) as source:
            shutil.copyfileobj(source, temporary, length=1024 * 1024)
        if sha256(pending) != checksum:
            raise ValueError(f"SHA-256 mismatch for {name}")
        pending.replace(destination)
    finally:
        pending.unlink(missing_ok=True)
    return destination


def load_test_set() -> tuple[np.ndarray, np.ndarray]:
    archive = verified_asset("cifar-10-python.tar.gz", DATASET_URL, DATASET_SHA256)
    # Verify the known archive before unpickling its original test batch.
    with tarfile.open(archive, "r:gz") as release:
        member = release.extractfile("cifar-10-batches-py/test_batch")
        if member is None:
            raise ValueError("CIFAR-10 test batch is missing")
        with member:
            batch = pickle.load(member, encoding="bytes")

    pixels = batch[b"data"]
    labels = np.asarray(batch[b"labels"], dtype=np.int64)
    classes, counts = np.unique(labels, return_counts=True)
    if pixels.shape != (TEST_IMAGES, 3072) or pixels.dtype != np.uint8:
        raise ValueError("Expected 10,000 packed 32 × 32 RGB test images")
    if labels.shape != (TEST_IMAGES,) or not (
        np.array_equal(classes, np.arange(CLASS_COUNT))
        and np.all(counts == TEST_IMAGES // CLASS_COUNT)
    ):
        raise ValueError("Expected exactly 1,000 test labels per CIFAR-10 class")

    # CIFAR-10 stores channel planes. The reference model expects RGB per pixel.
    images = pixels.reshape(TEST_IMAGES, 3, 32, 32).transpose(0, 2, 3, 1)
    return np.ascontiguousarray(images), labels


def open_reference_model(
    *, int8: bool = False, reference_kernels: bool = False
) -> tuple[Interpreter, int, int]:
    from ai_edge_litert.interpreter import Interpreter, OpResolverType

    if int8:
        path = verified_asset(
            "resnet8-int8.tflite", f"{MODEL_DIRECTORY_URL}/pretrainedResnet_quant.tflite", INT8_MODEL_SHA256
        )
    else:
        path = verified_asset(
            "resnet8-float.tflite", f"{MODEL_DIRECTORY_URL}/pretrainedResnet.tflite", MODEL_SHA256
        )
    resolver = OpResolverType.BUILTIN_REF if reference_kernels else OpResolverType.AUTO
    interpreter = Interpreter(model_path=str(path), num_threads=1, experimental_op_resolver_type=resolver)
    interpreter.allocate_tensors()
    inputs = interpreter.get_input_details()
    outputs = interpreter.get_output_details()
    if len(inputs) != 1 or len(outputs) != 1:
        raise ValueError("Expected one model input and one model output")
    model_input, model_output = inputs[0], outputs[0]
    dtype = np.int8 if int8 else np.float32
    if (
        tuple(model_input["shape"]) != (1, *IMAGE_SHAPE)
        or tuple(model_output["shape"]) != (1, CLASS_COUNT)
        or model_input["dtype"] != dtype
        or model_output["dtype"] != dtype
    ):
        raise ValueError(f"Expected a {dtype.__name__} RGB input and ten {dtype.__name__} class scores")
    if int8 and (
        model_input["quantization"] != INT8_INPUT_QUANTIZATION
        or model_output["quantization"] != INT8_OUTPUT_QUANTIZATION
    ):
        raise ValueError("Unexpected input or output quantization for the reference model")
    return interpreter, model_input["index"], model_output["index"]


def load_training_set() -> tuple[np.ndarray, np.ndarray]:
    """Read only the 50,000 official training images, in release order."""
    archive = verified_asset("cifar-10-python.tar.gz", DATASET_URL, DATASET_SHA256)
    batches = []
    targets = []
    with tarfile.open(archive, "r:gz") as release:
        for number in range(1, 6):
            member = release.extractfile(f"cifar-10-batches-py/data_batch_{number}")
            if member is None:
                raise ValueError(f"Missing CIFAR-10 training batch {number}")
            with member:
                batch = pickle.load(member, encoding="bytes")
            batches.append(batch[b"data"])
            targets.extend(batch[b"labels"])
    pixels = np.concatenate(batches)
    labels = np.asarray(targets, dtype=np.int64)
    if pixels.shape != (50_000, 3072) or pixels.dtype != np.uint8:
        raise ValueError("Expected 50,000 packed RGB training images")
    classes, counts = np.unique(labels, return_counts=True)
    if not np.array_equal(classes, np.arange(CLASS_COUNT)) or not np.all(counts == 5_000):
        raise ValueError("Expected 5,000 training labels per class")
    images = pixels.reshape(-1, 3, 32, 32).transpose(0, 2, 3, 1)
    return np.ascontiguousarray(images), labels


def training_indices(labels: np.ndarray, seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Fix a stratified 45,000/5,000 split without touching official test data."""
    if labels.shape != (50_000,):
        raise ValueError("Split expects the official training labels")
    rng = np.random.default_rng(seed)
    train, validation = [], []
    for label in range(CLASS_COUNT):
        indices = rng.permutation(np.flatnonzero(labels == label))
        if len(indices) != 5_000:
            raise ValueError("Split expects exactly 5,000 examples per class")
        validation.extend(indices[:500])
        train.extend(indices[500:])
    return np.sort(train), np.sort(validation)


if __name__ == "__main__":
    open_reference_model()
    load_test_set()
    print("Verified the ResNet-8 model and 10,000 CIFAR-10 test images.")
