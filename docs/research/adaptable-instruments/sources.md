# Evidence register

Reviewed November 26, 2026. Summaries identify narrow support and limits; they are not claims that Preambl reproduced a result. Version labels identify the particular result or documentation consulted.

## S01 - ROMA v2

- **Original:** [ROMA v2](https://arxiv.org/abs/2503.12988v2)
- **Evidence:** Architecture paper; synthesis/estimated power; 2026-03-02, v2.
- **Supports:** Fixed base weights with writable adapters; custom ROM layout.
- **Limit:** No fabricated ROMA result established; see existing detailed repository review.

## S02 - FixyNN

- **Original:** [FixyNN](https://arxiv.org/abs/1902.11128)
- **Evidence:** Research evaluation; 2019.
- **Supports:** Fixed vision features with a programmable back end.
- **Limit:** Transfer results cover selected datasets, not arbitrary new tasks.

## S03 - YOLoC

- **Original:** [YOLoC](https://arxiv.org/abs/2206.00379)
- **Evidence:** Architecture research; 2022, DAC.
- **Supports:** ROM computation plus an SRAM residual branch.
- **Limit:** Different physical implementation from the Basys 3.

## S04 - LogicNets

- **Original:** [LogicNets](https://arxiv.org/abs/2004.03021)
- **Evidence:** FPGA circuit research; 2020.
- **Supports:** Sparse quantized networks mapped to truth-table circuits.
- **Limit:** Fan-in growth restricts useful topologies; headline latency is task-specific.

## S05 - hls4ml FAQ

- **Original:** [hls4ml FAQ](https://fastmachinelearning.org/hls4ml/intro/faq.html)
- **Evidence:** Official tool documentation; 1.3.1 page reviewed.
- **Supports:** Neural-model conversion and spatial parallelism.
- **Limit:** Layer support and FPGA fit require actual tool evaluation.

## S06 - hls4ml external BRAM weights

- **Original:** [hls4ml external BRAM weights](https://fastmachinelearning.org/hls4ml/advanced/bramfactor.html)
- **Evidence:** Official tool documentation; 1.3.0 page reviewed.
- **Supports:** Exposed BRAM ports can support a user-built weight loader.
- **Limit:** Documentation flags reimplementation; not a ready-made atomic update system.

## S07 - FINN memory modes

- **Original:** [FINN memory modes](https://finn.readthedocs.io/en/latest/reference/mem-modes.html)
- **Evidence:** Official tool documentation; Live page reviewed.
- **Supports:** Parameter storage modes depend on layer/backend.
- **Limit:** External storage does not itself guarantee runtime updates for every layer.

## S08 - AMD ROM_STYLE

- **Original:** [AMD ROM_STYLE](https://docs.amd.com/r/2022.2-English/ug901-vivado-synthesis/ROM_STYLE)
- **Evidence:** Vendor implementation documentation; UG901, 2022.2.
- **Supports:** FPGA ROM can map into BRAM or LUT resources.
- **Limit:** Does not create dense custom mask ROM.

## S09 - Basys 3 reference manual

- **Original:** [Basys 3 reference manual](https://digilent.com/reference/_media/reference/programmable-logic/basys-3/basys3_rm.pdf)
- **Evidence:** Board documentation; Published manual.
- **Supports:** 1,800 Kbits BRAM and 90 DSP slices.
- **Limit:** Available resources do not imply a full model or sensor interface fits.

## S10 - RNN coupled to SPAD TCSPC for FLIM

- **Original:** [RNN coupled to SPAD TCSPC for FLIM](https://pmc.ncbi.nlm.nih.gov/articles/PMC10853568/)
- **Evidence:** Peer-reviewed experimental instrument; 2024; Scientific Reports 14, 3286.
- **Supports:** Timestamp-to-lifetime processing demonstrated on a Kintex-7 microscope system.
- **Limit:** Specific sensor, estimator, and optical conditions; no Preambl results.

## S11 - FLAN: compact FLIM network

- **Original:** [FLAN: compact FLIM network](https://pubmed.ncbi.nlm.nih.gov/36863024/)
- **Evidence:** Primary paper abstract; 2023.
- **Supports:** Adder-based lifetime estimation with FPGA implementation.
- **Limit:** Abstract review supports approach, not a fully reproduced performance comparison.

## S12 - Event-driven acquisition

- **Original:** [Event-driven acquisition](https://pmc.ncbi.nlm.nih.gov/articles/PMC7613693/)
- **Evidence:** Peer-reviewed experimental microscopy; 2022; Nature Methods.
- **Supports:** Learned event recognition changes acquisition rate during experiments.
- **Limit:** Actuation and scheduling matter; this is not an FPGA speed demonstration.

## S13 - QubiCML v5

- **Original:** [QubiCML v5](https://arxiv.org/abs/2406.18807v5)
- **Evidence:** Experimental quantum-readout paper; versioned abstract; 2026-09-13, v5.
- **Supports:** Current abstract reports 40 ns FPGA state inference.
- **Limit:** Core inference differs from readout and complete feedback; older summary reports 54 ns.

## S14 - QICK documentation

- **Original:** [QICK documentation](https://docs.qick.dev/latest/)
- **Evidence:** Open instrumentation documentation; Live documentation.
- **Supports:** RFSoC firmware, software, and real-time control ecosystem.
- **Limit:** Requires supported RFSoC hardware and RF engineering.

## S15 - QubiC project

- **Original:** [QubiC project](https://lbl-qubic.gitlab.io/)
- **Evidence:** Lab project documentation; QubiC 2.0.
- **Supports:** Existing open FPGA control, gateware, and calibration infrastructure.
- **Limit:** Existing ecosystem, not an unoccupied startup market.

## S16 - Deep calibration transfer

- **Original:** [Deep calibration transfer](https://sapientia.ualg.pt/server/api/core/bitstreams/97879f02-7363-4c0d-9a35-02eb1a533e2c/content)
- **Evidence:** Peer-reviewed primary paper; 2021; Infrared Physics and Technology 117, 103863.
- **Supports:** Transfer learning across benchtop and handheld infrared instruments.
- **Limit:** Standard-free does not imply no target data, reference values, or validation.

## S17 - Adaptive ANN calibration transfer

- **Original:** [Adaptive ANN calibration transfer](https://www.sciencedirect.com/science/article/pii/S016974392200185X)
- **Evidence:** Primary paper abstract; 2022; Chemometrics 230, 104674.
- **Supports:** Evaluates adaptation against calibration-transfer alternatives.
- **Limit:** Abstract review; not hardware deployment or universal superiority.

## S18 - Eigenvector datasets

- **Original:** [Eigenvector datasets](https://eigenvector.com/resources/data-sets/)
- **Evidence:** Dataset custodian; Live catalog.
- **Supports:** Paired corn spectra and additional spectroscopy/fault datasets.
- **Limit:** Public download does not establish unrestricted redistribution rights.

## S19 - UCI Gas Sensor Array Drift

- **Original:** [UCI Gas Sensor Array Drift](https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset)
- **Evidence:** Dataset custodian; 2012 donation; DOI 10.24432/C5RP6W.
- **Supports:** Sensor measurements organized for drift research; CC BY 4.0.
- **Limit:** Not raw fast acquisition or a real-time FPGA benchmark.

## S20 - EDA data archive

- **Original:** [EDA data archive](https://zenodo.org/records/5548355)
- **Evidence:** Author data deposit; 0.1.0, 2021-10-04.
- **Supports:** Microscopy recordings and training archive.
- **Limit:** Record predates the final publication; license and split need inspection before reuse.

## S21 - RnnFlim code

- **Original:** [RnnFlim code](https://github.com/Yang-J-LIN/RnnFlim)
- **Evidence:** Author implementation; Live repository.
- **Supports:** Starting point associated with the FLIM paper.
- **Limit:** No reproduction performed; inspect dependencies and license before reuse.

## S22 - EDA code

- **Original:** [EDA code](https://github.com/LEB-EPFL/EDA)
- **Evidence:** Author implementation; Live repository.
- **Supports:** Existing event-driven microscope-control implementation.
- **Limit:** Hardware compatibility and deployment timing remain setup-specific.

## S23 - Moku Neural Network

- **Original:** [Moku Neural Network](https://liquidinstruments.com/neural-network/)
- **Evidence:** Commercial vendor description; Live product page.
- **Supports:** Already offers inline neural signal processing and feedback.
- **Limit:** Vendor capability statement; no independent Preambl comparison.

## S24 - Moku neural-model tutorial

- **Original:** [Moku neural-model tutorial](https://next.documentation.liquidinstruments.com/mnn/examples/Simple_sine.html)
- **Evidence:** Vendor implementation tutorial; Live documentation.
- **Supports:** Documents feedforward network export, scaling, and clipping.
- **Limit:** Support is platform/version-specific; not evidence of arbitrary model support.

## S25 - Photon Force firmware customization

- **Original:** [Photon Force firmware customization](https://www.photon-force.com/services/firmware-customisation/)
- **Evidence:** Commercial vendor description; Live service page.
- **Supports:** In-camera processing addresses raw-data transfer constraints.
- **Limit:** Direct overlap; does not establish a need to buy Preambl.

## S26 - Swabian conditional filter

- **Original:** [Swabian conditional filter](https://www.swabianinstruments.com/static/documentation/TimeTagger/InDepthGuides/ConditionalFilter.html)
- **Evidence:** Vendor technical manual; 2.22.6.0 documentation.
- **Supports:** Hardware rules reduce irrelevant time tags before transfer.
- **Limit:** A learned method must improve on appropriate existing rules.

## S27 - ONE WARE

- **Original:** [ONE WARE](https://one-ware.com/)
- **Evidence:** Commercial vendor description; Live product page.
- **Supports:** Hardware-targeted vision and OEM deployment offering.
- **Limit:** Marketing/testimonials are not independent benchmarks.

## S28 - ConfigAI

- **Original:** [ConfigAI](https://www.configai.co/)
- **Evidence:** Startup vendor description; Live product page.
- **Supports:** Automated ML-to-FPGA mapping and code generation offering.
- **Limit:** Compilation-time and compatibility claims not independently tested.

## S29 - ZEISS Smart Acquisition Toolkit

- **Original:** [ZEISS Smart Acquisition Toolkit](https://www.zeiss.com/microscopy/en/products/software/zeiss-zen/smart-acquisition-toolkit.html)
- **Evidence:** Commercial instrument vendor; Live product page.
- **Supports:** Guided acquisition and image-analysis feedback already exist.
- **Limit:** Platform-specific capability; not proof all OEM needs are solved.

## S30 - Pycro-Manager

- **Original:** [Pycro-Manager](https://pycro-manager.readthedocs.io/en/latest/)
- **Evidence:** Open software documentation; Live documentation.
- **Supports:** Microscope automation, image processing, and control components.
- **Limit:** Python orchestration is not a hard real-time timing guarantee.

## S31 - NIREOS HERA

- **Original:** [NIREOS HERA](https://nireos.com/hera-hyperspectral-cameras/)
- **Evidence:** Commercial instrument vendor; Live product page.
- **Supports:** Relevant hyperspectral instrument category for discovery.
- **Limit:** No documented Preambl purchase interest or measured bottleneck.

## S32 - LoRA

- **Original:** [LoRA](https://arxiv.org/abs/2106.09685)
- **Evidence:** Primary adaptation research; 2021.
- **Supports:** Low-rank trainable updates around frozen weights.
- **Limit:** Language-model results do not prove sensor transfer; unmerged adapters add work.

## S33 - TinyTL

- **Original:** [TinyTL](https://arxiv.org/abs/2007.11622)
- **Evidence:** Primary adaptation research; 2020.
- **Supports:** Frozen weights with small trainable components for efficient learning.
- **Limit:** Training memory differs from inference memory and circuit area.

## S34 - Tent

- **Original:** [Tent](https://arxiv.org/abs/2006.10726)
- **Evidence:** Primary adaptation research; 2020 submission.
- **Supports:** Test-time entropy optimization and normalization updates.
- **Limit:** Benchmark success is not a guarantee of stable online instrument adaptation.

## S35 - Neural confidence calibration

- **Original:** [Neural confidence calibration](https://arxiv.org/abs/1706.04599)
- **Evidence:** Primary uncertainty research; 2017.
- **Supports:** Confidence can be miscalibrated; studies temperature scaling.
- **Limit:** Calibrated confidence is not universal out-of-distribution detection.

## S36 - AMD AXI stream handshake

- **Original:** [AMD AXI stream handshake](https://docs.amd.com/r/en-US/pg080-axi-fifo-mm-s/Port-Descriptions)
- **Evidence:** Vendor interface documentation; PG080, 4.3.
- **Supports:** Transfer occurs when valid and ready are both asserted.
- **Limit:** Application must still handle a sensor that cannot pause.

## S37 - DeepFreeze

- **Original:** [DeepFreeze](https://github.com/ARM-software/DeepFreeze)
- **Evidence:** Research implementation; Live repository.
- **Supports:** Fixed-network hardware-generation precedent.
- **Limit:** Research code has documented limitations; no adoption or reproduction here.

## S38 - FixyFPGA

- **Original:** [FixyFPGA](https://developer.arm.com/community/arm-research/b/articles/posts/fixyfpga-fully-parallel-fully-pipelined-fpga-accelerator-for-sparse-cnns)
- **Evidence:** Author technical explanation; 2021.
- **Supports:** Sparse fixed-weight CNN hardware; pruning/quantization constraints.
- **Limit:** Benefits are design-specific and do not guarantee Basys 3 fit.

## S39 - MemryX FAQ

- **Original:** [MemryX FAQ](https://developer.memryx.com/support/faq.html)
- **Evidence:** Commercial technical documentation; Live documentation.
- **Supports:** Model mapping depends on more than parameter capacity.
- **Limit:** Different architecture; benchmark the actual workload before comparing.

## S40 - Mythic M1

- **Original:** [Mythic M1](https://www.mythic.ai/m-1)
- **Evidence:** Commercial vendor description; Live product page.
- **Supports:** On-chip weights and analog inference are existing alternatives.
- **Limit:** Vendor speed/power claims not independently validated here.
