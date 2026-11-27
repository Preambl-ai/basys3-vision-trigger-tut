# Competition, customer alternatives, and commercial tests

**Reviewed:** November 26, 2026. [Research index](README.md).

## Revised assessment

**The broad idea of neural inference inside instruments is already commercial.** Preambl should investigate a narrow OEM integration problem before treating this as its company direction. The research does not establish a small competitor count, an underserved market, or willingness to pay.

## Direct and adjacent alternatives

| Organization/resource | Public capability | Implication and unresolved question |
| --- | --- | --- |
| Liquid Instruments Moku [S23, S24] | Inline FPGA neural signal processing, uploaded models, and feedback examples; tutorial describes dense feedforward models. | Direct overlap. Is there an OEM interface, form factor, operator, update, or integration need its platform does not meet? No gap established. |
| Photon Force [S25] | Custom firmware for processing high-volume camera data near acquisition. | Direct overlap in camera-side integration; possible expert/partner as well as alternative supplier. |
| Swabian Instruments [S26] | Rule-based hardware filtering of time tags. | Learned selection must improve a concrete task beyond these existing rules. |
| ZEISS [S29] | Guided acquisition and analysis-driven experiment feedback. | Competes with generic smart-microscopy software; a faster core alone is insufficient. |
| Pycro-Manager and EDA [S30, S22] | Open microscope automation and event-driven acquisition. | Existing integration ecosystem and software baseline, not a blank slate. |
| ONE WARE [S27] | Hardware-targeted vision and OEM deployment offering. | Broad model deployment/industrial vision has adjacent competition. |
| ConfigAI [S28] | Vendor-described model-to-FPGA compiler. | A generic compiler business overlaps existing startups and open tools. |
| QICK/QubiC [S14, S15] | Open specialized control and calibration infrastructure. | A quantum-readout entry needs domain access and a distinct contribution. |

Vendor pages establish offered capabilities, not independent performance, current pricing, supported custom integrations, or customer satisfaction. No supplier has been benchmarked or contacted as part of this research. Existing LinkedIn requests do not establish a partnership or sales lead.

## Narrow hypotheses worth asking about

1. **A reusable inference block inside an OEM's existing FPGA.** Proposed deliverable: documented stream interface, quantized model execution, a controlled writable update path, and verification evidence. Risk: OEM engineers or open tools can already do it economically.
2. **A repeatable sensor-transfer workflow.** Proposed deliverable: small device-specific updates plus validation and traceability. Risk: classical calibration or fuller retraining works better, and faster hardware adds little.
3. **A streaming estimator for a particular detector/data format.** Proposed deliverable: fewer raw transfers while preserving defined measurement quality. Risk: exact task already has an effective classical or vendor implementation.

These are commercial hypotheses, not novel-architecture claims. Avoid defining the product as "ROM + adapters": customers buy a solved workflow with support, interfaces, and evidence.

## Potential research conversations

NIREOS is relevant through its hyperspectral product range [S31]. Photon Force and Swabian are relevant because they already address camera or timing-data processing [S25, S26]. Liquid Instruments is particularly useful as a reference offering [S23]. None is classified here as a confirmed buyer.

Ask an engineer to identify the current pipeline and failure cost. Ask a product/engineering owner who controls the interface, qualification, budget, release schedule, and maintenance obligations. Determine whether one integration can be reused across several units or customers.

## What a commercial advantage would have to show

| Advantage hypothesis | Evidence required |
| --- | --- |
| Faster useful response | Same task and quality, complete timing boundary, baseline already measured. |
| Lower cost | Component, engineering, qualification, support, and lifecycle costs for a specific deployment. |
| Easier updates | Measured workflow/time saved and acceptable validation process. |
| Better measurement | Independent reference data, operating-range validation, and acceptable uncertainty. |
| Reusable product | A second deployment with substantially shared code/hardware and a buyer willing to fund it. |

For a custom chip, estimate break-even only after obtaining real fabrication/design quotes, expected volumes, unit savings, and support costs. Fixed engineering cost divided by per-unit savings is a first arithmetic check, not a market forecast. No credible figures are available from this review.

## Reasons to stop or change direction

Stop a candidate if its current processor meets the requirement; acquisition dominates; data/interface access is unavailable; target adaptation loses essential accuracy; integration is one-off consultancy with little reusable value; or a mature supplier already meets the requirement at an acceptable cost.

The defensible opportunity, if found, would be evidence-backed execution on an underserved integration task. Competition is a test to pass, not something this report can wish away.

## Evidence sources

- **S14:** [QICK documentation](https://docs.qick.dev/latest/) - Open instrumentation documentation.
- **S15:** [QubiC project](https://lbl-qubic.gitlab.io/) - Lab project documentation.
- **S22:** [EDA code](https://github.com/LEB-EPFL/EDA) - Author implementation.
- **S23:** [Moku Neural Network](https://liquidinstruments.com/neural-network/) - Commercial vendor description.
- **S24:** [Moku neural-model tutorial](https://next.documentation.liquidinstruments.com/mnn/examples/Simple_sine.html) - Vendor implementation tutorial.
- **S25:** [Photon Force firmware customization](https://www.photon-force.com/services/firmware-customisation/) - Commercial vendor description.
- **S26:** [Swabian conditional filter](https://www.swabianinstruments.com/static/documentation/TimeTagger/InDepthGuides/ConditionalFilter.html) - Vendor technical manual.
- **S27:** [ONE WARE](https://one-ware.com/) - Commercial vendor description.
- **S28:** [ConfigAI](https://www.configai.co/) - Startup vendor description.
- **S29:** [ZEISS Smart Acquisition Toolkit](https://www.zeiss.com/microscopy/en/products/software/zeiss-zen/smart-acquisition-toolkit.html) - Commercial instrument vendor.
- **S30:** [Pycro-Manager](https://pycro-manager.readthedocs.io/en/latest/) - Open software documentation.
- **S31:** [NIREOS HERA](https://nireos.com/hera-hyperspectral-cameras/) - Commercial instrument vendor.
