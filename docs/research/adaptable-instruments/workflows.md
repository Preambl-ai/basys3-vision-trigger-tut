# Where inference could help an instrument

**Reviewed:** November 26, 2026. [Research index](README.md).

## Conclusion

**Research two narrow needs first: adaptable signal classification at an OEM interface, and sensor-specific correction.** Neither is a confirmed business. Learned acquisition control and streaming estimators are technically supported but have substantial existing solutions.

An instrument is a measurement system: sensor, acquisition electronics, processing, software, and sometimes an actuator. Inference helps only if its output improves a measurement or changes a useful action within the available time.

## Evidence from working systems

| Example | Established evidence | Important boundary |
| --- | --- | --- |
| SPAD fluorescence lifetime estimation | A 2024 study couples a 32 x 32 Piccolo sensor to four quantized GRU cores on Kintex-7, reporting up to 4 million photons/s and 10 frames/s. [S10] | Those are instrument-specific operating results, not generic image-classification throughput. |
| Compact lifetime networks | FLAN investigates adder-based estimation, temporal compression, and FPGA implementation. [S11] | Architecture ideas, not a benchmark Preambl has reproduced. |
| Event-driven microscopy | Learned detection changes the acquisition rate while observing biological events. [S12] | The experiment already works through existing control software; faster FPGA inference needs an additional reason. |
| Quantum-state readout | QubiCML v5 describes 40 ns state inference on digitized readout data and experiments on superconducting devices. [S13] | Readout integration and full feedback add time; older 54 ns descriptions concern an earlier version. |

FLIM measures how fluorescence decays after excitation. A SPAD detects individual photons; TCSPC records their timing. This is primarily a parameter-estimation problem. It should not be forced into a CNN image-classification framing.

QICK and QubiC already provide open RFSoC control ecosystems. [S14, S15] Quantum control is a valuable technical reference but a difficult initial market without a specialist laboratory partner.

## Candidate workflows: Preambl hypotheses

| Candidate | Proposed output | Reason it might matter | What would invalidate it? |
| --- | --- | --- | --- |
| OEM signal-quality classification | Good/bad/unknown or event label before host transfer | Immediate capture decisions with task updates | Simple rules or the existing processor already suffice. |
| Sensor-specific correction | Corrected scalar/vector plus quality flag | Reuse a shared model across sensor units | Variation requires replacing most of the model or the reference measurement is unavailable. |
| Learned acquisition trigger | Request faster capture or retain a region | Capture important events under storage/exposure limits | Acquisition/actuation is slower than inference, or missed events cause unacceptable selection bias. |
| Streaming lifetime estimator | Lifetime estimate and quality indication | Reduce timestamp traffic and enable feedback | Classical estimators are accurate and fast enough; hardware already implements the required estimator. |
| Hyperspectral classification | Material/quality score | Relevant to products such as HERA [S31] | Exposure, spectral reconstruction, or a CPU dominates the real constraint. |

These are proposed output contracts, not requests from the named companies. Begin with recorded digital data. Buying a detector or claiming a sensor-ready product is premature.

## Timing determines the opportunity

Define the allowed time from the physical event to the action. Then measure acquisition, buffering, preprocessing, inference, communication, scheduling, and actuator response separately. A short neural core cannot remove delay elsewhere.

The event-driven microscopy paper describes acquisition scheduling and reaction delays, including different temporal scales for different experiments. [S12] This is a useful warning against treating a neural-network timing number as an instrument timing number.

**Illustrative arithmetic, not a measurement:** if a pipeline spends 20 ms acquiring, 2 ms transferring, and 1 ms inferring, reducing inference to 0.01 ms changes 23 ms to 22.01 ms, only about 1.05x faster. A stronger benefit might instead come from avoiding transfer, improving the measurement, or meeting a control deadline.

## Questions to resolve with engineers

Ask for a trace showing the delayed decision; its deadline and acceptable missed-event rate; raw data format and ownership; current classical/CPU/FPGA solution; sensor-to-sensor variation; update frequency; available firmware interface; and who approves integration.

Request a concrete evaluation task before selecting an accelerator. A laboratory collaborator can establish technical value; an OEM buyer must separately establish repeatable demand and a viable product boundary.

## Evidence sources

- **S10:** [RNN coupled to SPAD TCSPC for FLIM](https://pmc.ncbi.nlm.nih.gov/articles/PMC10853568/) - Peer-reviewed experimental instrument.
- **S11:** [FLAN: compact FLIM network](https://pubmed.ncbi.nlm.nih.gov/36863024/) - Primary paper abstract.
- **S12:** [Event-driven acquisition](https://pmc.ncbi.nlm.nih.gov/articles/PMC7613693/) - Peer-reviewed experimental microscopy.
- **S13:** [QubiCML v5](https://arxiv.org/abs/2406.18807v5) - Experimental quantum-readout paper; versioned abstract.
- **S14:** [QICK documentation](https://docs.qick.dev/latest/) - Open instrumentation documentation.
- **S15:** [QubiC project](https://lbl-qubic.gitlab.io/) - Lab project documentation.
- **S31:** [NIREOS HERA](https://nireos.com/hera-hyperspectral-cameras/) - Commercial instrument vendor.
