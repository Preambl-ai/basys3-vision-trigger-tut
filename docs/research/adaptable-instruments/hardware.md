# Hardware approaches and toolchains

**Reviewed:** November 26, 2026. [Research index](README.md).

## Recommendation

Use a conventional quantized reference first. Compare fixed and writable implementations of the **same small computation** before claiming specialization helps. Keep adaptation training on a computer initially.

## Implementation choices

| Approach | Potential advantage | Main trade-off |
| --- | --- | --- |
| MCU/CPU with DSP or linear model | Simple integration and updates | Must measure deadline, jitter, and energy. |
| Existing NPU/edge accelerator | Mature neural execution | Operator, interface, and memory constraints may limit a workload. |
| FPGA with BRAM-backed MACs | Predictable scheduling and direct stream integration | Capacity, bandwidth, development effort, and buffering. |
| Constant-weight arithmetic | Synthesis can simplify fixed operations | More parallel logic and routing can offset savings. |
| LUT-network inference | Boolean mapping can give very short pipelines | Fan-in and quantization restrict the model. |
| Custom ROM ASIC | Dense fixed storage and specialized computation | Fabrication cost, physical design, and model-lifetime risk. |

MemryX documents weight, feature-map, and compute constraints; Mythic describes commercial analog inference hardware. [S39, S40] Both are alternatives to compare when appropriate, not evidence their technology matches an instrument interface.

## Fixed logic is established research

LogicNets maps suitable sparse quantized networks into truth-table circuits, with fan-in-dependent cost. [S04] FixyFPGA uses fixed-weight scalers and compression to reduce hardware needs. [S38] DeepFreeze is an existing fixed-network generation project with research-code limitations. [S37] None guarantees that the current ResNet-8 or compact CNN fits fully unrolled on Basys 3.

FixyNN and YOLoC establish prior art for separating shared computation from a changeable back end or residual path. [S02, S03] ROMA adds custom memory and layout ideas to a language-model architecture. [S01] See the existing [ROMA review](../roma-fixed-model-adapters.md) for its design-projection limitations.

## Existing tools to evaluate

| Resource | Useful starting point | Check before relying on it |
| --- | --- | --- |
| hls4ml [S05] | Convert supported quantized models to spatial HLS designs | Pin model frontend, backend, compiler, precision, reuse, and stream settings; verify supported layers. |
| hls4ml external weights [S06] | Expose weights through BRAM interfaces | User supplies loader/update protocol; page flags feature redesign. External means outside the generated core, not necessarily off-chip DRAM. |
| FINN [S07] | Quantized dataflow and selectable parameter-memory modes | Supported combinations depend on layer/backend; dynamic updates require explicit implementation checks. |
| Handwritten RTL | A tiny writable classifier with an explicit interface | Requires arithmetic equivalence, overflow, timing, and protocol verification. |

These tools already cover part of any proposed generic model-to-FPGA compiler. A Preambl product would need additional instrument-specific value.

## Basys 3 boundaries

The board has 1,800 Kbits BRAM (approximately 225 KiB) and 90 DSP slices. [S09] Its GPIO and serial interfaces do not turn it into a high-speed camera receiver or RFSoC acquisition system. A future sensor interface might require another board, ADC, receiver, or OEM FPGA integration; choose it from requirements rather than a shopping list.

An inferred FPGA ROM uses already-manufactured BRAM/LUT resources. It does not provide ROMA's custom mask-ROM density. [S08] Compare actual post-route LUT, flip-flop, BRAM, DSP, and timing results. Weights alone are insufficient: activation storage, memory ports, accumulators, queues, and control also matter.

**Sizing example only:** a 128-input, 32-hidden, 6-output dense network contains 4,288 matrix weights and 38 biases. INT8 matrix weights occupy 4,288 bytes; biases may use wider accumulators. A single ideal MAC executing every cycle at 100 MHz would spend 42.88 microseconds on the matrix products, before loading, activations, and control. This is a lower-bound arithmetic illustration, not measured latency or a fit claim.

## Fair comparisons

Compare equal input data, quantization, quality targets, timing boundaries, and batch/streaming conditions. Report clock and initiation interval separately from latency. A deeply pipelined design can accept a new input before the previous prediction exits; a serialized design may not.

Use the existing [FPGA fit report](../../resnet8-fpga-fit.md) as project evidence. It concerns dot products and memories, not a complete deployed CNN. A new approach must earn an advantage against that baseline and the simpler classical model.

## Evidence sources

- **S01:** [ROMA v2](https://arxiv.org/abs/2503.12988v2) - Architecture paper; synthesis/estimated power.
- **S02:** [FixyNN](https://arxiv.org/abs/1902.11128) - Research evaluation.
- **S03:** [YOLoC](https://arxiv.org/abs/2206.00379) - Architecture research.
- **S04:** [LogicNets](https://arxiv.org/abs/2004.03021) - FPGA circuit research.
- **S05:** [hls4ml FAQ](https://fastmachinelearning.org/hls4ml/intro/faq.html) - Official tool documentation.
- **S06:** [hls4ml external BRAM weights](https://fastmachinelearning.org/hls4ml/advanced/bramfactor.html) - Official tool documentation.
- **S07:** [FINN memory modes](https://finn.readthedocs.io/en/latest/reference/mem-modes.html) - Official tool documentation.
- **S08:** [AMD ROM_STYLE](https://docs.amd.com/r/2022.2-English/ug901-vivado-synthesis/ROM_STYLE) - Vendor implementation documentation.
- **S09:** [Basys 3 reference manual](https://digilent.com/reference/_media/reference/programmable-logic/basys-3/basys3_rm.pdf) - Board documentation.
- **S37:** [DeepFreeze](https://github.com/ARM-software/DeepFreeze) - Research implementation.
- **S38:** [FixyFPGA](https://developer.arm.com/community/arm-research/b/articles/posts/fixyfpga-fully-parallel-fully-pipelined-fpga-accelerator-for-sparse-cnns) - Author technical explanation.
- **S39:** [MemryX FAQ](https://developer.memryx.com/support/faq.html) - Commercial technical documentation.
- **S40:** [Mythic M1](https://www.mythic.ai/m-1) - Commercial vendor description.
