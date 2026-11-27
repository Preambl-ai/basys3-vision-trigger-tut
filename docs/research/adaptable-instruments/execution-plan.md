# Proposed execution plan

**Reviewed:** November 26, 2026. [Research index](README.md).

**Status:** Plan only. No new training, hardware execution, purchasing, or outreach was performed in this documentation series.

## Decision to pursue

Investigate whether a small updateable inference component can solve one measured instrument problem better than a classical/CPU baseline or an existing supplier. A fixed feature extractor with a writable head is the first technical hypothesis, not a required final architecture.

Do not abandon the current vision prototype or claim its full CNN runs on hardware. Its CPU results and dot-product fit report are separate evidence. A compact 1D/vector task is an additional way to test updates and latency within the board's limits.

## Stage A: establish the problem

Conduct a small set of engineer conversations across at least two relevant organizations, with permission before any messages are sent. Ask for the deadline, raw/processed data format, current solution, quality target, update need, acceptable integration boundary, and decision owner. No interviews were conducted for this report.

**Exit evidence:** one concrete workflow, representative data or an approved proxy, a timing breakdown, and a named technical evaluator. Stop hardware selection if these remain unknown. Connection acceptance alone does not satisfy this stage.

## Stage B: test the adaptation hypothesis in software

Use the [dataset protocol](datasets-validation.md). Start with classical and small neural baselines on paired spectra or temporal sensor features; retain existing CIFAR-10 evidence as a separate vision task. Compare full training/fine-tuning, frozen-plus-head, and only then intermediate adapters. Keep test partitions untouched.

Measure source/target quality against update-label budget and update size. Quantize the selected candidate and repeat evaluation. Report failures and performance across conditions, not just aggregate accuracy.

**Exit evidence:** a reproducible split manifest, baseline and adaptation results, numerical export, and a documented quality tolerance chosen with the evaluator. If frozen features fail, keep more of the model programmable or reject specialization for that task.

## Stage C: prove the update path on Basys 3

Implement the smallest supported reference model with a writable classifier. Validate software/RTL agreement before measuring speed. Build, route, and verify resource headroom. Load update A, classify golden inputs, load B without regenerating the bitstream, and show the expected changed outputs. Check corruption, compatibility, reset, and rollback behavior.

Compare with a BRAM-backed version or an appropriate existing tool-generated design. A constant-weight variant is optional if there is a plausible resource/timing benefit. Keep precision and quality consistent. Do not require a physically new memory technology.

**Exit evidence:** implementation reports, board programming/build identifiers, actual result logs, update bytes and time, and core timing. If a board is unavailable, simulation and routed timing must remain labeled as such.

## Stage D: evaluate complete workflow value

Replay is sufficient for initial logic verification. It is insufficient to claim complete sensor-to-action performance. Obtain a real interface or a documented timing-equivalent source and account for preprocessing, framing, transfer, queuing, and output.

Compare latency distribution/deadline misses, quality, power, raw-data reduction, and engineering effort with the existing solution. Use a baseline that the customer would actually buy or maintain, including a simple rule or established software where applicable.

**Exit evidence:** a requirement-matched comparison reviewed by the evaluator. Choose another board only when the existing board cannot meet a specified interface/resource requirement.

## Stage E: determine if it is a product

Ask whether a second installation can reuse the design, whether the first evaluator will fund a pilot, who supports updates, and whether a supplier already meets the need. An OEM IP block, embedded module, or deployment package are possible forms, not decisions made by this report.

**Exit evidence:** a repeatable integration boundary and credible buyer commitment. Do not infer product-market fit from an impressive video, public research, or one friendly laboratory.

## Proposed decision record

| Question | Required record | Current status |
| --- | --- | --- |
| Does an unmet instrument problem exist? | Engineer requirement and incumbent comparison | Unverified |
| Does limited adaptation retain quality? | Held-out source/target results | Not run |
| Does specialization help this hardware? | Matched implementation comparison | Not run |
| Can updates be activated correctly? | Board logs and failure checks | Not implemented |
| Is complete latency useful? | Sensor-to-result/action timing | Not measured |
| Can the work become repeatable business? | Reuse evidence and buyer commitment | Unverified |

Targets such as an accuracy tolerance, maximum response time, and acceptable update downtime must be predeclared. Any provisional engineering target should be labeled as a target, not a customer requirement or measured result.

## Strongest finding from this review

There is real technical precedent and direct commercial overlap. The broad direction is less distinctive than initially implied. The next investment should therefore be a small adaptation experiment and concrete problem discovery, followed by hardware only when the evidence justifies it. See [competition](competition-business.md) before selecting a market or claiming novelty.
