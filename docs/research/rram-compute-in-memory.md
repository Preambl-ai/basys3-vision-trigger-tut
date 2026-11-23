# RRAM and compute-in-memory research for Preambl

**Research reviewed:** November 21, 2026

**Documented:** November 22, 2026

**Status:** Literature and vendor-documentation review. No RRAM simulation, hardware measurement, procurement, or vendor application has been performed for this project.

## Recommendation

**Explore RRAM compute-in-memory as a separate research track while continuing the digital FPGA prototype.** Begin with accuracy simulation, then investigate access to research hardware if the results justify it.

RRAM is relevant to Preambl's interest in keeping model weights close to computation. Some RRAM architectures perform neural-network arithmetic inside the memory array. This is a physically different implementation from the current BRAM-and-MAC design, but it is not automatically faster, more accurate, or more energy-efficient at the complete-system level.

The most practical initial role for Preambl would be model preparation, mapping, or hybrid-system engineering using a partner's RRAM technology. Developing a memory device, fabrication process, accelerator circuits, software, and application together is a much larger undertaking.

## 1. What RRAM is

RRAM, also called ReRAM, means **resistive random-access memory**. It stores information by programming a device's electrical resistance. The state can persist after power is removed, making it nonvolatile memory.

Digital implementations distinguish resistance ranges corresponding to bits. Some implementations support multiple resistance levels. RRAM may be embedded within a larger chip or supplied as a separate memory component; it is not inherently on the same chip as the processor. [Weebit bitcell explanation][bitcell]

### Storage and computing are different products

| Implementation | How it works | Relevance to Preambl |
| --- | --- | --- |
| Current FPGA approach | Weights reside in on-chip memory; separate arithmetic circuits execute the model. | Existing digital development path. |
| Conventional RRAM storage | A processor reads stored data and calculates elsewhere. | Persistent storage, without an automatic inference speedup. |
| RRAM compute-in-memory | A specially designed array performs operations through its electrical behavior. | Potential acceleration research direction. |

For example, RAMXEED's MB85AS8MT is an SPI-connected RRAM storage device. Its documented interface is memory access, not access to an analog matrix-computing array. Buying an ordinary RRAM component would not provide an AI accelerator. [Datasheet][ramxeed-datasheet]

## 2. How an RRAM array can execute model operations

A common neural-network operation multiplies inputs by weights and adds the results. In an analog RRAM computing array:

1. Weights are encoded using conductance, the inverse of resistance.
2. Inputs are encoded using voltages.
3. Resulting currents implement products, and combined currents implement sums.
4. Peripheral electronics measure or digitize the outputs for subsequent processing.

This enables parallel matrix operations while weights remain in place. Negative weights and higher precision may require extra devices or computation. Input conversion, output conversion, buffering, and other model operations remain part of the architecture. [NeuRRAM paper][neurram]

```mermaid
flowchart LR
    A[Digital inputs] --> B[Input encoding]
    B --> C[RRAM array: stored weights and matrix operations]
    C --> D[Output measurement and conversion]
    D --> E[Digital processing and decision]
```

The potential benefit is reduced weight movement and high parallelism. Whether that translates into better inference depends on the full implementation and workload.

## 3. Relationship to Taalas

Taalas publicly emphasizes model-specific silicon and merging storage with computation. Its public architectural description does not establish that RRAM is its underlying technology. This review does not attribute RRAM to Taalas. [Taalas explanation][taalas]

The shared question is how to remove data movement and general-purpose overhead from inference. RRAM is one possible approach; specialized digital circuits and other on-chip memory architectures are alternatives. Choosing a memory technology alone does not establish an advantage or novelty.

## 4. Evidence and organizations already working on it

| Example | Published evidence | What it establishes |
| --- | --- | --- |
| NeuRRAM, Nature 2022 | A 48-core chip with approximately three million RRAM cells; hardware-measured inference across several tasks. | RRAM computation has physical demonstrations beyond simulation. |
| TetraMem | Its published timeline describes evaluation chips and production-sample milestones for analog inference hardware. | Commercial development activity; current availability requires direct confirmation. |
| Weebit Nano | Embedded RRAM technology and an FPGA-supported compute-in-memory research platform. | A possible research-hardware access route. |
| RAMXEED | SPI RRAM memory products. | Conventional RRAM storage availability, distinct from computing arrays. |

Sources: [NeuRRAM][neurram], [TetraMem timeline][tetramem], [Weebit research-program announcement][matrix-announcement], [RAMXEED product list][ramxeed].

NeuRRAM's experimental board also uses an FPGA for intermediate buffers and partial-sum accumulation. This illustrates a hybrid architecture: the RRAM chip and FPGA have different responsibilities. It does not mean that an FPGA's existing memory becomes RRAM. [Paper][neurram]

Vendor announcements establish what suppliers describe or offer. They are not independent evidence that Preambl's model would achieve the same benefits.

## 5. Why implementation is difficult

| Challenge | Consequence for a prototype |
| --- | --- |
| Programming variation and read noise | Encoded values and computed outputs can differ from the intended mathematical values. |
| Stability over time and operating conditions | Accuracy needs validation under relevant conditions, with any correction overhead included. |
| Input and output conversion | Supporting circuits consume energy, time, and area. |
| Finite array size | Larger layers require tiling across arrays or multiple executions. |
| Remaining digital operations | Activations, residual paths, buffers, control, and interfaces still need implementation. |

Conversion overhead is itself an active research problem. Published work investigates adaptive analog-to-digital conversion to address limitations of conventional conversion circuitry. [Research paper][adc]

A relatively static model can be programmed in advance. If the mapping instead requires frequent weight rewriting during inference, programming adds cost. Endurance and programming characteristics depend on the particular device and must be checked in its specifications.

### Connection to pruning and quantization

Pruning, quantization, and distillation remain relevant, but the optimization objective changes:

- Scattered zero weights may still occupy a fixed array. Physical area or latency savings require a mapping that exploits the zeros.
- Structured reductions can make the array mapping smaller or require fewer executions.
- Precision choices affect accuracy, device count, conversions, and digital accumulation.
- Hardware-aware model preparation must account for physical errors as well as mathematical quantization.

These are engineering questions to test, not measured Preambl results. See the earlier [model-compression research](model-compression.md).

## 6. What is possible with the Basys 3?

The Basys 3 has FPGA block RAM and external serial flash, not an RRAM computing array. A bitstream can configure existing circuits; it cannot add a new fabricated memory technology. [Digilent reference manual][basys]

An FPGA could nevertheless control an external RRAM device, prepare inputs, collect outputs, and implement the digital portions of a hybrid system. Compatibility depends on the external platform's interfaces, voltages, throughput, and supplied controller design.

Digital emulation can also test numerical behavior, but it cannot demonstrate the speed or energy consumption of a physical RRAM array. Adding conventional external RRAM storage would leave the FPGA's arithmetic work in place and would not by itself resolve the scheduling constraints in the [current fit study](../resnet8-fpga-fit.md).

## 7. A possible hardware route: Weebit Matrix IMC

Weebit announced its Matrix IMC Research Program on **November 4, 2026**. It describes a **32 × 32 RRAM crossbar array**, a direct-access evaluation package, and a quick-start package containing an FPGA subsystem and sample code. Applications are open to qualified industry and academic researchers. [Announcement][matrix-announcement]

This is a small experimental building block: 1,024 cells, with effective weight capacity depending on sign and precision representation. It should not be assumed to hold or accelerate the complete Preambl CNN automatically.

The current platform page specifies **research and prototyping only, with no commercial use rights**. A product would require a separate commercial arrangement. Pricing, acceptance, delivery timing, licensing details, and Basys 3 compatibility have not been confirmed. [Platform details][matrix]

No application or supplier contact has been submitted for Preambl as part of this review.

## 8. Potential contributions for Preambl

| Direction | Evidence needed before treating it as an advantage |
| --- | --- |
| Models tolerant of RRAM behavior | Better retained accuracy under measured variation, including correction overhead. |
| Model-to-array mapping | Better capacity utilization, fewer conversions or transfers, or lower total implementation cost. |
| Hybrid RRAM and digital module | Better complete-system performance or energy at comparable accuracy on a useful workload. |

All three areas have prior work. They are research hypotheses, not claims of novelty, patentability, customer demand, or commercial readiness.

## 9. Proposed evaluation

**Status: proposed; not executed.**

1. Preserve the digital model and hardware implementation as references, clearly separating estimates from board measurements.
2. Simulate a small model or representative layer using an RRAM-style array. Vary array size, precision, programming error, read noise, and conversion settings.
3. Identify which assumptions determine accuracy and how many array executions, transfers, and accumulations the mapping needs.
4. If promising, investigate research-hardware access and validate a small physical operation or layer before attempting a complete model.
5. Compare complete systems at comparable accuracy: include conversion, digital processing, transfers, programming, latency, energy, and hardware cost. Separate one-time preparation from per-inference work.

### Simulation starting point

Sandia's open-source CrossSim supports analog-array accuracy studies, including programming errors, noise, conductance drift, conversion precision, and array parasitics. Its documentation explicitly states that it **does not model accelerator energy, area, or speed**. Those claims require separate analysis and measurements; simulation runtime is not accelerator inference latency. [CrossSim documentation][crosssim]

### Decision rule

Continue toward hardware only if the model retains useful accuracy under realistic assumptions and the complete-system analysis identifies an advantage worth measuring. Reassess if the benefit disappears after accounting for conversions, tiling, transfers, or digital processing.

The immediate recommendation is a bounded research experiment, while continuing the digital FPGA prototype. There is no evidence yet that RRAM is the best implementation for Preambl's workload.

## Sources and scope notes

Sources are linked beside the relevant claims. Supplier pages and availability can change after the review date. No headline vendor speedup is adopted as a prediction for Preambl. This review is not a comprehensive prior-art or patent search.

[bitcell]: https://www.weebit-nano.com/technology/reram-bitcell/
[ramxeed-datasheet]: https://www.ramxeed.com/assets/images/products/datasheet/ReRAM/MB85AS8MT-DS2v2-E.pdf
[neurram]: https://www.nature.com/articles/s41586-022-04992-8
[taalas]: https://taalas.com/the-path-to-ubiquitous-ai/
[tetramem]: https://tetramem.com/about-tetramem/
[matrix-announcement]: https://www.weebit-nano.com/news/press-releases/weebit-nano-launches-weebit-matrix-in-memory-compute-research-program/
[ramxeed]: https://www.ramxeed.com/products/reram/reram-products.html
[adc]: https://www.nature.com/articles/s41467-025-65233-w
[basys]: https://digilent.com/reference/_media/reference/programmable-logic/basys-3/basys3_rm.pdf
[matrix]: https://www.weebit-nano.com/products/embedded-reram-ip/matrix-imc-in-memory-compute-reram-rram/
[crosssim]: https://github.com/sandialabs/cross-sim
