# What should remain updateable?

**Reviewed:** November 26, 2026. [Research index](README.md).

## Conclusion

Start with supervised, offline updates to the smallest component that works. Test a writable output head before adding intermediate adapters. Keep full fine-tuning as a reference: a frozen representation may simply be unsuitable.

Three meanings of calibration must stay separate: correcting the physical instrument, transferring a predictive model between instruments, and calibrating a classifier's confidence. Success at one does not establish the others.

## Adaptation ladder: proposed comparison

| Change | Why test it? | Main failure mode |
| --- | --- | --- |
| Input offset/gain and normalization | Cheap response to limited signal variation | Cannot fix missing information, nonlinear drift, or changed physics. |
| Output threshold/bias | Small update footprint | Does not repair a poor underlying representation. |
| Linear classifier/regressor | Reuse shared features for a changed task | New classes or devices may need different features. |
| Small residual or low-rank adapter | Modify intermediate behavior while preserving most weights | Extra arithmetic, scaling, memory, and possible placement bottlenecks. |
| Selected-layer/full fine-tuning | Accuracy reference and fallback | More update data and potentially a new hardware build. |

LoRA freezes a base matrix and learns a low-rank correction. [S32] For a matrix of shape `m x n`, rank `r` uses `r*(m+n)` adapter parameters rather than `m*n`, excluding bias/scales. For example, a 64 x 64 matrix and rank 4 need 512 adapter parameters rather than 4,096 full-matrix parameters. These are parameter counts, not guaranteed speedups.

In software, a low-rank update may be merged into the base matrix. With physically fixed base arithmetic or mask ROM, changing the base is unavailable during ordinary operation: an unmerged correction needs a writable path and additional execution. Include that cost in the comparison.

TinyTL studies frozen weights and small trainable components for memory-efficient learning. [S33] Its lesson is useful, but training-memory benefits do not automatically become smaller inference circuits. For a CNN, head-only training, affine changes, or a small residual block may be simpler than applying language-model LoRA everywhere.

## Calibration transfer is a real research problem

Deep calibration transfer studies adapting neural models across benchtop and handheld infrared instruments. [S16] Adaptive ANN work evaluates another transfer approach on accessible spectroscopy datasets. [S17] These support investigating cross-device transfer, not guaranteed reduction in reference measurements or successful FPGA deployment.

"Standard-free" in this literature concerns avoiding a particular common transfer-standard procedure. It must not be described as "needs no target data or ground truth." Record exactly which target measurements, labels, standards, and reference assays each experiment uses.

For spectroscopy, compare PLS regression, simple bias/slope correction, and direct/piecewise standardization where applicable before a neural method. For a detector stream, compare thresholding, filtering, matched filters, or the accepted estimator. These are proposed mandatory baselines, not a statement that every method applies to every instrument.

## Drift and continual learning

Distinguish sensor drift, changed concentration ranges, changed classes, changed optics, and changed sample preparation. An update that works for one type may fail for another. Keep a source-domain regression set to detect whether improving the new device damages earlier behavior.

Tent demonstrates test-time adaptation using entropy and normalization updates on benchmark tasks. [S34] It is a research comparator, not a reason to enable unattended weight changes in an instrument. Begin with labeled offline adaptation, review, versioning, and rollback. Test imbalanced streams, unexpected inputs, and prolonged operation before considering online training.

## Confidence and scientific correctness

Neural probabilities can be miscalibrated; temperature scaling is an established validation-based technique. [S35] A high confidence score is not proof of physical correctness or a reliable detector of unfamiliar conditions. Use accepted-domain checks, rejection/unknown outputs, reference measurements, and appropriate error analysis.

For regression, evaluate bias, RMSE, residual structure, and error across operating ranges. For classification, measure per-class errors and missed important events. Decide the acceptable loss with the domain owner before choosing an adapter size.

## Experiment record

Record base/model hash, frozen layers, changed parameters, training/validation/test identities, adaptation-label count, quantization/scales, source/target performance, update bytes, hardware cycles, and build versions. Publish negative transfer and failed configurations as well as the best result. No such adaptation experiment has been run in this research update.

## Evidence sources

- **S16:** [Deep calibration transfer](https://sapientia.ualg.pt/server/api/core/bitstreams/97879f02-7363-4c0d-9a35-02eb1a533e2c/content) - Peer-reviewed primary paper.
- **S17:** [Adaptive ANN calibration transfer](https://www.sciencedirect.com/science/article/pii/S016974392200185X) - Primary paper abstract.
- **S32:** [LoRA](https://arxiv.org/abs/2106.09685) - Primary adaptation research.
- **S33:** [TinyTL](https://arxiv.org/abs/2007.11622) - Primary adaptation research.
- **S34:** [Tent](https://arxiv.org/abs/2006.10726) - Primary adaptation research.
- **S35:** [Neural confidence calibration](https://arxiv.org/abs/1706.04599) - Primary uncertainty research.
