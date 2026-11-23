"""Regression checks for data isolation, model export, and result reporting."""

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import torch

from cifar10_inputs import training_indices
from compact_model import CompactCNN, resource_counts
from compare_models import read_result
from train_compact import augment
from benchmark_compact import quantize_model


class CompactTests(unittest.TestCase):
    def test_split_is_complete_disjoint_stratified_and_repeatable(self):
        labels = np.tile(np.arange(10), 5_000)
        train, val = training_indices(labels)
        again, _ = training_indices(labels)
        self.assertTrue(np.array_equal(train, again))
        self.assertEqual(np.intersect1d(train, val).size, 0)
        self.assertTrue(np.array_equal(np.sort(np.concatenate([train, val])), np.arange(50_000)))
        self.assertTrue(np.all(np.bincount(labels[val]) == 500))
        self.assertTrue(np.all(np.bincount(labels[train]) == 4_500))

    def test_fusion_preserves_logits(self):
        torch.manual_seed(42)
        model = CompactCNN().eval()
        image = torch.rand(3, 3, 32, 32)
        with torch.inference_mode():
            before = model(image)
            model.fuse()
            after = model(image)
        torch.testing.assert_close(before, after, atol=1e-6, rtol=1e-5)
        self.assertEqual(tuple(after.shape), (3, 10))

    def test_augmentation_preserves_constant_image_identity(self):
        images = torch.stack([torch.full((3, 32, 32), i / 10) for i in range(10)])
        torch.testing.assert_close(augment(images), images)

    def test_resource_count_matches_layer_geometry(self):
        result = resource_counts(CompactCNN().eval())
        weights = 8*3*9 + 8*8*9 + 16*8*9 + 16*16*9 + 32*16*9 + 32*32*9 + 32*10
        macs = (8*3*9 + 8*8*9)*32*32 + (16*8*9 + 16*16*9)*16*16
        macs += (32*16*9 + 32*32*9)*8*8 + 32*10
        self.assertEqual(result["kernel_parameters"], weights)
        self.assertEqual(result["dense_macs_per_image"], macs)

    def test_int8_export_roundtrip(self):
        torch.manual_seed(42)
        model = quantize_model(CompactCNN().eval(), torch.rand(10, 3, 32, 32))
        inputs = torch.rand(3, 3, 32, 32)
        with tempfile.TemporaryDirectory() as directory, torch.inference_mode():
            path = str(Path(directory) / "model.ts")
            torch.jit.trace(model, inputs[:1]).save(path)
            loaded = torch.jit.load(path).eval()
            torch.testing.assert_close(model(inputs), loaded(inputs), rtol=0, atol=0)

    def test_report_rejects_partial_or_inconsistent_results(self):
        reference = Path("docs/benchmarks/resnet8-int8.json")
        result = json.loads(reference.read_text(encoding="utf-8-sig"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            for field, value in (("test_images", 100), ("top1_correct", 9000), ("cpu_threads", 4)):
                invalid = {**result, field: value}
                path.write_text(json.dumps(invalid), encoding="utf-8")
                with self.assertRaises(ValueError):
                    read_result(path)


if __name__ == "__main__":
    torch.set_num_threads(1)
    unittest.main()
