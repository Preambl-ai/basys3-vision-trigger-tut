# ROMA and adaptable fixed-model hardware

**Research reviewed and documented:** November 25, 2026

**Status:** Literature and vendor-documentation review. No ROMA reproduction, adapter training, new FPGA implementation, ASIC fabrication, or customer validation has been performed for this research.

## Recommendation

**Test a small fixed feature extractor with an updateable classifier before considering custom ROM circuitry.** This is a relevant extension of Preambl's FPGA work. It could combine efficient inference with inexpensive task customization, but the underlying architectural idea already has substantial prior art.

The most promising business hypotheses remain embedded decisions inside scientific instruments and sensor-specific correction. A general-purpose image accelerator would face established alternatives. Neither this paper nor a fast demonstration establishes customer demand or commercial differentiation.

## 1. Paper reviewed

[ROMA: a Read-Only-Memory-based Accelerator for QLoRA-based On-Device LLM, version 2][roma], by Wenqiang Wang, Yijia Zhang, Zikai Zhang, Guanting Huo, Hao Liang, Shijie Cao, and Ningyi Xu. First submitted March 17, 2025; version 2 dated March 2, 2026.

This review examined all seven pages of the supplied version, including the architecture, physical-design proposal, evaluation methodology, and figures. Page references below use PDF page numbers.

### Main idea

ROMA separates the model into parts with different requirements:

| Part | Storage and implementation | Purpose |
| --- | --- | --- |
| Quantized base weights | Fixed ROM near low-precision compute | Keep the large, reusable model on-chip. |
| LoRA adapters | Writable SRAM and higher-precision compute | Customize behavior while keeping the base model frozen. |
| Attention KV cache | Writable SRAM | Store changing attention state during language generation. |
| Intermediate results | SRAM | Buffer the data produced during computation. |

LoRA adds small trainable matrices to a frozen model. Conceptually, a layer computes `W*x + B*(A*x)`: `W` stays fixed, while the much smaller `A` and `B` can change. QLoRA combines low-bit base weights with adapter-based fine-tuning. ROMA accelerates inference for this arrangement; it does not demonstrate an on-chip training system.

The architectural lesson is to specialize the expensive shared computation while retaining enough programmable capacity for useful changes. A conventional image classifier usually does not need the language model's KV cache.

### B-ROM and fused cells

ROMA's B-ROM groups decoded addresses and shares pre-generated combinations, encoding constant information in circuit connections. Its fused-cell proposal overlaps the physical footprints of wiring-heavy ROM and transistor-heavy computation to improve utilization of metal and transistor layers. These are custom digital CMOS design techniques, not RRAM or analog computation. See Sections III-C and III-D, PDF page 4.

The approximate fourfold reduction discussed in the paper concerns storage-array transistor count under its assumptions. It does **not** mean a fourfold reduction in complete-chip area. Figure 12 instead reports an L-Unit area change from 36.7 to 22.5 thousand square micrometers between standard ROM plus computation and the fused design, approximately 39% lower.

## 2. What the results establish

**The reported hardware results are design-level projections, not measured performance from a manufactured ROMA chip.** Section IV-A describes Verilog synthesis using Synopsys Design Compiler with a TSMC 7 nm library and power estimation using PrimeTime PX. The paper does not report fabricated-silicon measurements or a full-chip post-route timing-closure demonstration.

| Reported item | Paper result | Evidence location and qualification |
| --- | --- | --- |
| Clock | 500 MHz | Table I, page 4; design target/evaluation configuration. |
| Memory | 1.86 GB B-ROM plus 304 MB SRAM | Table I; 288 MB for adapters/cache and 16 MB for intermediate data described on page 2. |
| Area and power | 503.7 mm2 and 33.1 W | Table I; reported design area and estimated power. |
| Llama 3.2 3B, 4-bit, rank-16 adapters | 31,800 tokens/s with zero cached tokens; 24,600 at 1K; 14,600 at 4K | Figure 7, page 5; speed depends on cache length. |
| Llama 3 8B, 2-bit, rank-16 adapters | 24,100 tokens/s with zero cached tokens; 19,000 at 1K; 11,600 at 4K | Figure 7; not equivalent to the 3B configuration. |
| Comparison against RTX 4090 | Reported average 70.5x inference-speed advantage | Figure 9 and accompanying text, pages 5-6; specific model, workload, software, and projected accelerator. |

The figures distinguish prompt processing from token decoding. Peak decoding throughput is not time to first output or complete application response time. It also does not predict CNN image throughput: CNN weight reuse, feature-map traffic, image acquisition, and interface costs differ from single-stream LLM decoding.

### Important unanswered questions

1. **Model quality:** No substantial perplexity, language-task accuracy, or adapter-quality evaluation establishes what the 2-bit and 4-bit models retain.
2. **Physical implementation:** Fabricated measurements and full-chip routing, timing, thermal, and power evidence would strengthen the projections. Synthesis estimates do not resolve all of these issues.
3. **Benchmark reproducibility:** The CPU/GPU comparison needs independently reproducible model formats, adapter configurations, software versions, timing boundaries, and workloads. It should not become a general claim that ROMA beats every GPU workload by 70.5x.
4. **Power accounting:** Table II lists CPU/GPU power figures, but does not establish matched, measured workload energy for complete systems. Do not derive a verified energy advantage by dividing those figures into throughput.
5. **Context accounting:** Figure 9 describes generating 4K output tokens with varying prompt lengths, while the design discussion describes a roughly 4K cache. How longer combined prompt/output sequences are handled needs clarification.
6. **Model lifetime:** The expectation that base-model updates will occur over years is an assumption. Adapters cannot guarantee that an unsuitable or obsolete frozen base remains competitive.
7. **Deployment access:** This review did not identify a public ROMA implementation repository or independently measured ROMA hardware. This is a search limitation, not proof that neither exists.

These limitations justify further evaluation rather than dismissal or acceptance of the headline results.

## 3. Closely related prior work and competition

| Work or company | Relevant overlap | Meaning for Preambl |
| --- | --- | --- |
| [FixyNN, 2019][fixynn] | Fixed vision feature extractor with a programmable task-specific back end; evaluated transfer across six datasets. | A direct precedent for a fixed vision backbone with configurable behavior. |
| [FixyFPGA, 2021][fixyfpga] | Sparse CNN weights encoded as fixed hardware scalers, with fully on-chip pipelining. | Fixed-weight logic on FPGA is feasible, with substantial resource/accuracy trade-offs. |
| [YOLoC, DAC 2022][yoloc] | ROM computing plus an assisting SRAM residual branch for adaptable object detection. | A close vision precedent for fixed weights plus writable corrections. |
| [Taalas][taalas] | Publicly describes hardwired Llama inference and low-rank-adapter customization. | Adapter support alone would not distinguish Preambl from Taalas. |
| [LogicNets][logicnets] | Quantized sparse networks converted into FPGA truth-table circuits. | An established alternative to conventional memory-backed multiply-accumulate execution. |
| [MemryX][memryx] | Commercial embedded inference with on-chip weight and feature-map resource constraints. | A customer alternative, although its architecture differs from ROMA. |
| [Mythic M1][mythic] | Vendor describes on-chip weights and analog matrix computation. | Another commercial alternative for embedded vision; vendor claims need workload-specific verification. |

FixyNN reports nearly 2x energy efficiency versus an equal-area programmable accelerator across its six-dataset transfer evaluation with less than 1% accuracy loss. That supports the concept in those experiments, not universal transferability. FixyFPGA explicitly identifies FPGA resource consumption and accuracy losses from aggressive compression as constraints.

Arm's [DeepFreeze repository][deepfreeze] provides relevant hardware-generation research, but its documented limitations mean it should be evaluated before adoption. [hls4ml][hls4ml] is another baseline for FPGA model deployment and latency/resource trade-offs. [TinyTL][tinytl] is related work on adapting frozen networks efficiently; it does not validate ROMA's chip implementation.

The general architecture is established. Differentiation could still come from a better workload-specific implementation, adaptation method, sensor interface, calibration workflow, or deployment process. This review does not establish patent novelty or freedom to operate.

## 4. What Basys 3 can test

The [Basys 3 reference manual][basys] lists 1,800 Kbits of block RAM, approximately 225 KiB, and 90 DSP slices. ROMA's proposed memory capacity and custom physical layout cannot be reproduced on this board.

| Candidate implementation | What it tests | What it does not establish |
| --- | --- | --- |
| Base weights in BRAM, used read-only | Straightforward fixed-model execution and a reference for comparisons. | Dense manufactured-ROM area or energy benefits. |
| Constants mapped to LUTs or constant arithmetic | Whether specialization improves the selected FPGA model's resources, latency, or energy. | Automatic superiority over BRAM or ASIC scalability. |
| Fixed feature extractor with writable classifier/adapters | Useful customization without rebuilding the complete FPGA bitstream. | ROMA-scale LLM inference or universal adaptation. |

AMD documents that [`ROM_STYLE`][rom-style] maps constant arrays to existing memory resources such as block RAM or LUT-based ROM. Declaring ROM in RTL does not manufacture new memory cells or metal layers. FPGA configuration remains reprogrammable; a manufactured mask ROM would be fixed.

For intuition, 100,000 weights at 4 bits require about 50,000 bytes before metadata. This arithmetic is **not** a fit result: activations, line buffers, accumulators, adapters, parallel memory ports, and arithmetic resources also consume capacity.

Start with a writable output classifier, which is simpler than LoRA throughout the network. If that fails under meaningful domain changes, evaluate intermediate residual adapters. Train updates on a computer initially. Adapter training on the FPGA is a separate problem, and merging updates into permanently fixed base weights would remove the intended update flexibility.

## 5. Application and business hypotheses

The following are proposals inferred from the architecture and existing product workflows, not established customer requirements.

| Priority | Application | Possible before/after improvement | Required validation |
| --- | --- | --- | --- |
| 1 | Embedded decisions inside scientific instruments | Move a classification, quality check, or capture decision from a host computer into the instrument; retain task customization. | Show that interpretation or transfer actually limits the workflow and that OEM integration is worthwhile. |
| 2 | Sensor calibration and correction | Share a fixed processing model while loading small device- or installation-specific corrections. | Demonstrate that small updates handle real sensor variation, drift, and operating conditions. |
| 3 | Inspection across related products | Reuse a feature extractor while switching the classifier or adapters for a different product. | Compare accuracy with full fine-tuning and existing processors; broad inspection is competitive. |
| 4 | Selective capture of high-rate data | Identify useful events near the sensor, reducing transfer and storage. | Measure missed-event risk and beat existing rules on an appropriate workload. |

[NIREOS HERA][nireos] demonstrates a relevant scientific/industrial hyperspectral product category. It does not establish demand for Preambl. Exposure, acquisition, or reconstruction may dominate total time even if classification becomes much faster.

[Swabian Instruments' conditional filter][swabian] already removes irrelevant time tags in hardware before transfer. A learned selector must add value beyond such existing rules, while preserving scientifically important data. Learned decisions that discard data require explicit false-negative and fidelity evaluation.

A small, fast model is insufficient as a business proposition when a cheap existing processor already meets the requirement. The candidate product could eventually be an OEM module, licensed hardware design, or deployment software; customer evidence should determine which.

## 6. Proposed experiment and decision criteria

This is a proposed experiment, not an executed milestone or a replacement for the current benchmark plan.

1. **Software feasibility:** Compare full fine-tuning, a frozen feature extractor with a trainable classifier, and, if needed, small intermediate adapters. Separate training, validation, and held-out testing.
2. **Adaptability:** Test at least two meaningfully different classification tasks and changes in lighting, background, or camera conditions. Identify when the frozen representation fails.
3. **Hardware comparison:** Compare BRAM-backed and fixed-weight implementations of the same small model at matched precision, accuracy, and workload. Include a straightforward existing FPGA toolflow as a baseline where practical.
4. **Update demonstration:** Switch the writable classifier or adapter without regenerating the FPGA bitstream; verify the expected new behavior and correctness against software.
5. **System measurement:** Report accuracy, false negatives where relevant, core latency, complete input-to-result latency, throughput, LUT/BRAM/DSP use, and measured board power. Label estimates separately and account for host/interface overhead.
6. **Customer relevance:** Ask instrument engineers for an actual timing/power constraint, representative data, update frequency, acceptable accuracy trade-off, and an integration path.

Continue toward a product only if specialization provides a meaningful measured advantage, the required adaptation remains accurate, and an identifiable customer benefits. If a head-only update fails, test adapters before committing to permanently fixed hardware. If neither works, retain more programmability or reject the approach for that workload.

## 7. Relationship to existing project evidence

The repository already records the CPU [ResNet-8 baseline](../cifar10-baseline.md), the [compact-model accuracy shortfall](../compact-cifar10.md), and [FPGA dot-product fit estimates](../resnet8-fpga-fit.md). Those results do not establish a complete CNN running on the board, nor any ROMA-like adapter implementation.

This research complements [model compression](model-compression.md) and [RRAM compute-in-memory](rram-compute-in-memory.md). Compression may enable fixed hardware to fit; RRAM is a physically different implementation route. Neither is a prerequisite for the proposed digital FPGA experiment.

## Sources

Primary papers, author explanations, official documentation, and vendor pages reviewed for the November 25, 2026 assessment. Vendor performance statements are not independent validation.

- [ROMA v2: paper and version history][roma] - architecture, synthesis methodology, and reported results.
- [FixyNN paper][fixynn] - fixed vision feature extractor and task-specific back end.
- [Arm: FixyFPGA][fixyfpga] - FPGA specialization, sparsity, and implementation constraints.
- [YOLoC paper][yoloc] - ROM-CiM with an SRAM residual branch.
- [Taalas technical overview][taalas] - model specialization and adapter customization.
- [LogicNets paper][logicnets] - neural networks mapped to truth-table circuits.
- [AMD ROM_STYLE documentation][rom-style] - inferred FPGA ROM resources.
- [Digilent Basys 3 manual][basys] - board resources.
- [Arm DeepFreeze][deepfreeze] - existing research implementation and limitations.
- [hls4ml concepts][hls4ml] - FPGA deployment and resource/latency controls.
- [TinyTL paper][tinytl] - related frozen-network adaptation research.
- [MemryX FAQ][memryx] - commercial alternative and mapping constraints.
- [Mythic M1][mythic] - vendor-described embedded analog inference product.
- [NIREOS HERA][nireos] - relevant instrument product category.
- [Swabian conditional filtering][swabian] - existing hardware data-reduction capability.

[roma]: https://arxiv.org/abs/2503.12988v2
[fixynn]: https://arxiv.org/abs/1902.11128
[fixyfpga]: https://developer.arm.com/community/arm-research/b/articles/posts/fixyfpga-fully-parallel-fully-pipelined-fpga-accelerator-for-sparse-cnns
[yoloc]: https://arxiv.org/abs/2206.00379
[taalas]: https://taalas.com/the-path-to-ubiquitous-ai/
[logicnets]: https://arxiv.org/abs/2004.03021
[rom-style]: https://docs.amd.com/r/2022.2-English/ug901-vivado-synthesis/ROM_STYLE
[basys]: https://digilent.com/reference/_media/reference/programmable-logic/basys-3/basys3_rm.pdf
[deepfreeze]: https://github.com/ARM-software/DeepFreeze
[hls4ml]: https://github.com/fastmachinelearning/hls4ml/blob/main/docs/api/concepts.rst
[tinytl]: https://arxiv.org/abs/2007.11622
[memryx]: https://developer.memryx.com/support/faq.html
[mythic]: https://www.mythic.ai/m-1
[nireos]: https://nireos.com/hera-hyperspectral-cameras/
[swabian]: https://www.swabianinstruments.com/static/documentation/TimeTagger/InDepthGuides/ConditionalFilter.html
