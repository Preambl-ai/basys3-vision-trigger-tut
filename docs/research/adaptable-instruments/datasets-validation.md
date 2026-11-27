# Datasets, baselines, and reproducible evaluation

**Reviewed:** November 26, 2026. [Research index](README.md).

## First benchmark recommendation

**Use paired spectroscopy data to test transfer and chronological sensor data to test drift, while keeping the existing vision benchmark.** These inexpensive software experiments can reject an unsuitable frozen-model idea before more FPGA development. They do not substitute for a partner's real instrument task.

## Data and code starting points

| Resource | Contents established by source | Appropriate use and limitation |
| --- | --- | --- |
| Eigenvector corn [S18] | 80 physical corn samples, three NIR spectrometers, 700 channels, four reference properties | Paired instrument-transfer regression; small sample size limits conclusions. |
| Other Eigenvector sets [S18] | Catalog includes pharmaceutical spectroscopy and process-fault data | Additional discovery resources; inspect each dataset's actual metadata and permissions. |
| UCI gas drift [S19] | 13,910 measurements from 16 sensors, six gases; temporal batches and CC BY 4.0 | Chronological drift classification; precomputed features, not fast raw-sensor timing. |
| EDA Zenodo deposit [S20] | Version 0.1.0 archive includes microscopy recordings and training files; listed total 14.1 GB | Event-recognition/replay work after checking metadata, labels, license, and publication-version differences. |
| RnnFlim [S21] | Author code linked from the FLIM paper | Investigate timestamp simulation, training, and firmware reproduction requirements; not run here. |
| EDA implementation [S22] | Author microscopy-control code | Existing software baseline and integration reference; not a Basys 3 design. |

Only resource descriptions were reviewed. No new archive was downloaded, converted, trained on, or redistributed by this documentation work. Public availability is not blanket permission to republish files; check actual license and attribution before adding data to the repository.

## Leakage-resistant splits

For corn, assign physical sample IDs to partitions **before** expanding them into measurements from different instruments. Keep every measurement of a held-out specimen out of training and adaptation. Use a source-training set, target-adaptation set with an explicit budget, validation set for model selection, and untouched target test specimens. Eighty samples call for careful uncertainty reporting and sensitivity analysis, not a large neural architecture by default.

For gas drift, predeclare chronological training, adaptation, validation, and test periods. Fit scaling and feature selection only on allowed training data. Track available classes and concentration distributions by period. Randomly mixing future and past measurements answers a different question from adaptation to future drift.

For microscopy, split by experiment, biological sample, or recording rather than adjacent frames. Track event identity across overlapping windows. An apparently large frame count can contain few independent events. A model trained on synthetic timestamps must also be evaluated on real measurements and optical conditions outside its training generator.

## Comparison matrix

Run the applicable classical method, a full-precision neural reference, its quantized version, frozen-plus-head adaptation, and a fuller fine-tuning reference. Add intermediate adapters only if a simpler update fails. Give methods comparable training information and disclose any pretrained knowledge.

For each target domain, plot or tabulate performance against adaptation-label budget and update size. Do not select the best adapter with test labels. Report repeated seeds where training randomness matters and confidence intervals appropriate to the independent unit of sampling.

## Quality and performance measurements

| Measurement | Record |
| --- | --- |
| Classification | Balanced accuracy or macro-F1 where appropriate, per-class confusion, event-level recall, false triggers per unit time, and rejection coverage. |
| Regression | Physical units, RMSE/MAE, bias, residuals across range/device/conditions, and comparison with reference repeatability. |
| Timing | Observation/window length, core latency, stream initiation interval, complete response, p50/p95/p99 where variable, worst observed case, and deadline misses. |
| Update | Bytes, transfer time, activation time, whether acquisition paused, and rollback behavior. |
| Hardware | Part/speed grade, actual clock, post-route utilization/timing, and full pipeline included. |
| Energy | Measured board/input power with idle and active conditions; distinguish estimates and specify host/sensor inclusion. |

An observed maximum is not a mathematical worst-case bound. Measurement accuracy and operating conditions may dominate a small neural error difference.

## Honest replay

Replay can test a classifier and a streaming interface. It cannot recreate physical exposure, ADC noise, a host-camera driver, or actuator response unless those are explicitly modeled or measured. If a host sends extracted features, report feature-to-result timing and measure extraction separately. Do not label it sensor-to-action latency.

Publish a manifest with dataset version/source, file hashes, split IDs, preprocessing, permitted uses, seeds, model and quantization settings, software/tool versions, and timing scripts. Add golden inputs/outputs for hardware equivalence and avoid embedding restricted or partner-confidential recordings in public commits.

## Evidence sources

- **S18:** [Eigenvector datasets](https://eigenvector.com/resources/data-sets/) - Dataset custodian.
- **S19:** [UCI Gas Sensor Array Drift](https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset) - Dataset custodian.
- **S20:** [EDA data archive](https://zenodo.org/records/5548355) - Author data deposit.
- **S21:** [RnnFlim code](https://github.com/Yang-J-LIN/RnnFlim) - Author implementation.
- **S22:** [EDA code](https://github.com/LEB-EPFL/EDA) - Author implementation.
