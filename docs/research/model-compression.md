# Model compression research for Preambl

**Reviewed:** November 19, 2026

**Status:** Research and proposed experiments. No new compression experiment or FPGA inference result is claimed here.

## Recommendation

**Test structured pruning and quantization alongside a directly trained smaller CNN. Optimize the model and its FPGA implementation together.**

Qismet provides relevant ideas for searching for smaller networks. Its published results do **not** establish that quantum search is better than strong classical alternatives. Quantum optimization should remain a separate research experiment until it demonstrates a practical advantage.

The possible commercial value for Preambl is delivering an accurate, deployable model that meets a customer's speed, memory, energy, or device-cost constraint. General model compression is already a well-developed field; using it alone does not establish a distinctive product.

## Scope and evidence

This review inspected Qismet's experiment code, protocols, result tables, and timing records, alongside the papers and tools linked below. It also checked this repository's existing laptop benchmark and FPGA fit reports.

- Qismet training and IBM jobs were **not independently rerun**. Its numerical results are repository-reported evidence.
- Preambl's existing results are documented separately and retain their original limitations.
- Business opportunities below are hypotheses requiring customer validation.
- This is a technical review, not a comprehensive novelty or patent search.

The Qismet review is pinned to [commit `25e7a11`](https://github.com/Syinaric/Qismet/tree/25e7a112ca98d6e385fd70974fd4b84c75eea8d7), so future repository changes do not silently change the evidence.

## 1. The concepts in plain language

| Concept | What it does | Possible benefit |
| --- | --- | --- |
| Pruning | Removes selected weights, neurons, channels, or blocks. | Less storage or computation, if the implementation exploits the removal. |
| Quantization | Uses fewer bits to represent weights and activations. | Smaller memory footprint and potentially cheaper arithmetic. |
| Distillation | Trains a smaller model to imitate a larger model's outputs. | May help recover accuracy in a compact model. |
| Search | Chooses among model configurations and implementation settings. | Can reduce manual engineering and find better trade-offs. |

Qismet mainly investigates search. Search happens while preparing the model; inference happens when the finished model classifies an image. Faster search does not automatically mean faster inference.

## 2. What Qismet does

Its workflow is:

1. Train a sample of candidate subnetworks.
2. Fit a predictor of the candidates' validation loss.
3. Search that predictor for promising candidates.
4. Train and evaluate the selected candidates.

The quantum computer participates in candidate generation. Neural-network training and image inference remain classical computations. The flagship task is Fashion-MNIST clothing classification with a fully connected network, not general photographic classification with a CNN. [Qismet overview][q-overview]

### Reported flagship results

The 100-qubit experiment reduces a 400-hidden-neuron network to 200 hidden neurons. Its selected smaller networks score about **84.0–84.4% test accuracy**, versus **82.4–83.2%** for the full networks across three seeds.

The primary comparison uses best validation loss after training selected candidates:

| Comparison | Reported result | Interpretation |
| --- | --- | --- |
| Quantum search vs random sampling | Wins under the predefined rule. | Better than this random baseline in the experiment. |
| Quantum search vs matched simulated annealing | Mean best loss rounds to 0.5014 for both; no quantum win. | No demonstrated superiority over this classical method. |
| Quantum search vs longer simulated annealing | Classical search wins in all three seeds; mean loss 0.4976 vs 0.5014. | Stronger classical search remains important. |

Simulated annealing is an optimization algorithm that runs on an ordinary computer. These comparisons use a fixed candidate budget, except the longer classical reference. Equal candidate counts do not establish equal elapsed time or cost. [Flagship results][q-results], [protocol][q-protocol]

### What the headline claims do and do not establish

**The 56× speedup is against exhaustive retraining.** Practical pruning systems need not train every possible subnetwork. The smaller experiment's own report attributes its speedup to the predictor-based method, and records a faster total pipeline for its CPU-search version than its quantum-search version. [Timing report][q-timing]

**Billed quantum time is different from turnaround time.** One published job lists three seconds of billed quantum time and approximately 9 hours 40 minutes from submission to result retrieval. This includes waiting and is one recorded job, not a universal queue-time estimate. [Job record][q-job]

**A large search space does not demonstrate classical intractability.** The protocol acknowledges that the chosen interaction graph is nearly a tree and easy for classical solvers. Quantum sampling does not return all possible networks at once. [Protocol][q-protocol]

**The predictor is a limitation.** Reported held-out R² values are 0.03–0.14. This indicates limited explanatory power on the audit samples; optimizing the predictor cannot guarantee the best real network. [Results][q-results]

**The training setup matters.** The implementation slices subsets from the original random initialization and trains them. It does not simply shrink a finished pretrained model while preserving its learned weights. An important additional baseline is directly training an ordinary 200-neuron network with a comparable overall tuning budget. [Implementation][q-code]

Research has previously found that directly training compact architectures can match or outperform structured-pruning pipelines in some settings. That is a reason to include the baseline, not to assume it always wins. [Rethinking the Value of Network Pruning][rethinking]

**Assessment:** Qismet supports further investigation of candidate selection and compact networks. It does not yet validate a general commercial compression service or a quantum advantage.

## 3. Why compression matters for the current Preambl prototype

| Existing evidence | Result | Limitation |
| --- | --- | --- |
| Optimized INT8 laptop ResNet-8 | 86.97% accuracy; approximately 0.22 ms median inference. | CPU runtime measurement, not FPGA performance. |
| 64-lane FPGA datapath and memories | 44.5 of 50 block RAM tiles; 89% utilization. | Partial out-of-context hardware build. |
| 64-lane dot-product schedule | About 4.95 ms per image at 100 MHz. | Estimate assuming continuous issues; excludes the remaining classifier operations and I/O. |

Sources: [CIFAR-10 baseline](../cifar10-baseline.md) and [ResNet-8 FPGA fit report](../resnet8-fpga-fit.md).

The present design therefore has real computation and memory constraints. The complete FPGA classifier has not yet been demonstrated by these results.

The fit report also shows that increasing from 32 to 64 MAC lanes reduces the dot-product estimate only from **5.52 ms to 4.95 ms**. This suggests that the current scheduling and lane utilization need attention alongside model size. This is an engineering inference from the documented design.

### A useful computation budget

The exported model requires about 12.5 million dense multiply-accumulates (MACs), including padding taps. Under the assumption of one MAC per DSP per cycle:

```text
90 DSPs × 100 million cycles/second = 9 billion MACs/second
12.5 million MACs / 9 billion = approximately 1.39 ms
9 billion MACs/second × 0.22 ms = approximately 1.98 million MACs
```

Thus, approaching the current laptop latency under those assumptions requires fewer than roughly two million MACs, before overhead. Different arithmetic packing, clock rates, or architectures change the calculation. This is a theoretical budget, not a measured result or a universal FPGA limit.

## 4. Which pruning approach fits an FPGA?

| Approach | What changes | Practical consideration |
| --- | --- | --- |
| Unstructured | Individual scattered weights become zero. | A dense execution loop can still read and multiply every zero. Sparse execution or compiler elimination is needed to exploit them. |
| Structured | Whole neurons, channels, or blocks are removed. | Produces smaller dense computations; a strong first experiment. |
| Hardware-aware | Pruning groups match the hardware's resources and schedule. | Targets actual DSPs, memory blocks, bandwidth, and execution cycles. |

Fixed-weight circuitry can allow synthesis to remove zero multiplications. Shared arithmetic may benefit less from scattered zeros. The outcome depends on how weights and operations are implemented. [hls4ml architecture paper][hls-architecture]

Channel widths must also suit the execution lanes. Removing channels can leave lanes idle unless the scheduler and data layout are adapted. Fewer parameters, fewer operations, lower latency, and lower energy are related but distinct measurements.

## 5. Prior work and existing alternatives

### Research closest to this direction

| Work | Contribution relevant to Preambl |
| --- | --- |
| [Network Slimming, 2017][slimming] | Channel pruning to produce compact CNNs. |
| [AMC, 2018][amc] | Automated compression with measured device acceleration. |
| [APQ, 2020][apq] | Joint architecture, pruning, and quantization search using an accuracy predictor. |
| [FPGA Resource-aware Structured Pruning, 2023][fpga-pruning] | Optimizes resource-aligned weight groups; reports 55–92% DSP savings and up to 81% BRAM savings on its evaluated tasks. |
| [Iterative Combinatorial Brain Surgeon, 2024][icbs] | Combinatorial pruning with block-wise optimization that could potentially use quantum hardware. |

The reported savings are specific to those studies. They are not predictions of what Preambl will achieve. Broad concepts such as pruning for FPGAs or searching a learned accuracy predictor already have substantial prior art.

### Tools and companies to benchmark against

| Alternative | Relevant capability | Relationship to Preambl |
| --- | --- | --- |
| [hls4ml][hls-optimization] | FPGA conversion and hardware-aware pruning objectives, including DSP and memory use. | Close technical baseline; possible implementation foundation. |
| [AMD FINN][finn] | Specialized FPGA inference for supported quantized networks. | FPGA compiler baseline; arbitrary models are not automatically supported. |
| [NVIDIA Model Optimizer][nvidia] | Pruning and optimization workflows. | Overlapping compression capabilities, primarily a different deployment ecosystem. |
| [Torch-Pruning][torch-pruning] | Structural pruning with dependency handling across layers. | Useful open-source pruning baseline. |
| [Edge Impulse EON][eon] | Embedded inference compilation and memory optimization. | Overlapping customer benefit; not the same FPGA approach. |
| [ST Edge AI tools][st] | Optimization, quantization, validation, and deployment on ST devices. | Alternative route for customers whose problem can be solved on those devices. |

These alternatives show that the field is established. They do not prove that every customer's deployment problem is solved. Preambl would need a specific, measured advantage.

## 6. Possible customer value

The strongest initial customer hypothesis is an embedded-product team that already has a model but cannot meet a device constraint.

| Customer problem | Useful outcome to demonstrate |
| --- | --- |
| Model needs an unaffordable processor or too much memory. | Preserve acceptable accuracy on a cheaper device. |
| Product exceeds battery or thermal limits. | Reduce measured energy per decision under the real workload. |
| System misses a response deadline. | Meet the deadline consistently, including input/output transfers. |
| FPGA deployment requires extensive manual work. | Reduce engineering time while producing verified implementations. |

Possible products include cameras, sensors, inspection systems, and other embedded devices. These are candidate markets, not validated customers or demonstrated demand.

A future workflow could accept a supported model, representative data, a target device, and constraints; then return a deployable implementation with an accuracy and performance report. Start with one model family and one hardware target.

Pruning does not require an FPGA. The customer benefit should determine whether an FPGA, MCU, NPU, or another device is the appropriate target. Customer interviews and pilot deployments are needed before committing to a commercial market.

## 7. Proposed next experiment

**Status: proposed; not executed by this research review.**

### Compare these candidates

| Candidate | Purpose |
| --- | --- |
| Existing INT8 ResNet-8 | Preserve the reference accuracy and performance measurements. |
| Directly trained smaller CNN, quantized | Test whether a simpler model is sufficient without pruning. |
| Structurally pruned ResNet-8, fine-tuned and quantized | Test the value of pruning an existing architecture. |
| Best compact candidate with distillation, if needed | Test whether teacher outputs help recover lost accuracy. |

Begin with classical pruning and search. A later Qismet-inspired predictor/search experiment should have to beat these baselines at a comparable total optimization budget.

### Evaluation rules

1. Keep the existing CIFAR-10 train/validation/test separation. Use validation data for tuning and freeze selections before final test evaluation. Obtain representative calibration/training data as required.
2. Agree the accuracy requirement before experiments. A proposed rule is at most one percentage point below the corresponding original-model accuracy, while also meeting the existing 85% minimum target.
3. Report the exact model, precision, preprocessing, tool versions, training/fine-tuning budget, and seeds. Repeat promising results across seeds.
4. Validate integer arithmetic against a reference for each candidate. Do not reuse ResNet-8 reference outputs as expected outputs for a different model.
5. Measure the compact candidates on the optimized CPU too. Compare at matched quality requirements; the CPU also benefits from compression.
6. Report FPGA resources, timing closure, actual cycles, and achieved clock. Distinguish synthesis estimates from measurements on a complete board implementation.
7. Report batch-one core inference latency separately from end-to-end transfer latency and throughput. Include latency percentiles for repeated measurements.
8. Measure power or energy if claiming an energy benefit. Parameter counts and resource reductions alone do not establish it.
9. Record total optimization time and compute usage. Include training samples, fine-tuning, compilation, quantum queue time if applicable, and failed attempts.

### Decision criteria

- **Continue:** a compact candidate meets the accuracy requirement and demonstrates a useful, repeatable deployment benefit over strong alternatives.
- **Use simpler methods when they win:** if direct training or ordinary pruning matches the search method, adopt the simpler approach.
- **Reassess hardware when needed:** if the Basys 3 cannot meet the required trade-off, use the result to guide architecture or device choices.
- **Keep quantum research conditional:** require a clear improvement in quality, total time, or cost over strong classical solvers before making it central to the product.

The next milestone is an honest before/after implementation result. A startup case additionally requires evidence that a customer values the improvement enough to adopt or pay for it.

## Sources

Qismet links below are pinned to the reviewed revision. External tool documentation may evolve.

[q-overview]: https://github.com/Syinaric/Qismet/blob/25e7a112ca98d6e385fd70974fd4b84c75eea8d7/README.md
[q-results]: https://github.com/Syinaric/Qismet/blob/25e7a112ca98d6e385fd70974fd4b84c75eea8d7/outputs/hw100_v6/RESULTS.md
[q-protocol]: https://github.com/Syinaric/Qismet/blob/25e7a112ca98d6e385fd70974fd4b84c75eea8d7/outputs/hw100_v6/PREREGISTRATION.md
[q-timing]: https://github.com/Syinaric/Qismet/blob/25e7a112ca98d6e385fd70974fd4b84c75eea8d7/outputs/scale16_v5/speed_race/raw_report.md
[q-job]: https://github.com/Syinaric/Qismet/blob/25e7a112ca98d6e385fd70974fd4b84c75eea8d7/outputs/hw100_v6/seed_11/hardware.json
[q-code]: https://github.com/Syinaric/Qismet/blob/25e7a112ca98d6e385fd70974fd4b84c75eea8d7/outputs/hw100_v6/hw100.py
[rethinking]: https://arxiv.org/abs/1810.05270
[hls-architecture]: https://people.ece.uw.edu/hauck/publications/hls4ml_TRETS.pdf
[slimming]: https://openaccess.thecvf.com/content_iccv_2017/html/Liu_Learning_Efficient_Convolutional_ICCV_2017_paper.html
[amc]: https://openaccess.thecvf.com/content_ECCV_2018/html/Yihui_He_AMC_Automated_Model_ECCV_2018_paper.html
[apq]: https://arxiv.org/abs/2006.08509
[fpga-pruning]: https://arxiv.org/abs/2308.05170
[icbs]: https://arxiv.org/abs/2411.17796
[hls-optimization]: https://github.com/fastmachinelearning/hls4ml/blob/main/docs/advanced/model_optimization.rst
[finn]: https://finn.readthedocs.io/en/latest/faq.html
[nvidia]: https://github.com/NVIDIA/Model-Optimizer/blob/main/examples/pruning/README.md
[torch-pruning]: https://github.com/VainF/Torch-Pruning
[eon]: https://www.edgeimpulse.com/blog/introducing-eon-compiler-ram-optimized/
[st]: https://www.st.com/content/st_com/en/st-edge-ai-suite/tools.html
