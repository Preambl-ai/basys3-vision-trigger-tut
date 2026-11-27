# Adaptable inference for scientific instruments

**Reviewed:** November 26, 2026. **Status:** Research and proposed experiments, not new measured Preambl performance.

## Read this first

There is evidence that near-sensor inference can be useful, and there are already products and open systems doing it. The strongest current hypothesis is a narrow OEM integration or sensor-transfer problem. A generic fast FPGA classifier, compiler, or smart microscope is not an established market gap.

The earlier broad recommendation is provisional. Direct commercial overlap discovered here makes customer-specific problem validation essential before committing the business to this direction. We have not established low competition, patent novelty, customer demand, or an advantage over existing suppliers.

## Research method and scope

This review covers fixed/updateable models, neural and classical signal processing, microscope feedback, photon timing, quantum readout, calibration transfer, FPGA toolchains, datasets, interfaces, and commercial alternatives. It prioritizes primary papers, author code, official manuals, dataset custodians, and supplier documentation. It is a bounded review, not every paper, company, patent, or inaccessible source.

Full text was inspected where accessible, including the FLIM and event-acquisition studies and the calibration-transfer paper. Some findings rely only on an abstract or official project description; the source register labels these boundaries. Product pages are capability claims, not independently reproduced benchmarks. Live documentation can change; pin versions before implementation.

Evidence labels used throughout:

- **Experimental research:** published system or dataset results under the authors' conditions.
- **Design evaluation:** simulation/synthesis estimates; not fabricated measurements.
- **Official/vendor documentation:** described features, interfaces, and limitations.
- **Preambl proposal:** an experiment, architecture, or commercial hypothesis still to test.

No new training, benchmark, sensor purchase, implementation, or customer interview was performed for this review. Existing [project measurements](../../benchmarks/comparison.md) remain the source for current prototype results.

## Reading order

- [Evidence register](sources.md): scope, version, and limit for each source.
- [Where inference could help an instrument](workflows.md)
- [Hardware approaches and toolchains](hardware.md)
- [What should remain updateable?](adaptation.md)

## Related project research

- [ROMA and adaptable fixed-model hardware](../roma-fixed-model-adapters.md)
- [Compression and Qismet](../model-compression.md)
- [RRAM and compute-in-memory](../rram-compute-in-memory.md)

The machine-readable [source register](sources.json) provides stable source IDs and review notes. Source IDs in the documents refer to the evidence section in that document and the register. The linked public originals support the factual claims; proposals are labeled separately.
