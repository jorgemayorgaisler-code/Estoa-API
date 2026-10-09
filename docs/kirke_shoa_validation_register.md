# ESTOA — Angostura Kirke (CUR011) SHOA 3015 validation register

Status: **software regression coverage available; independent hydrographic validation incomplete**.

This register separates published numerical evidence from internal model behavior. Do not label a model-generated crossing as a published SHOA window.

## Existing numerical reference cases

Source identified in existing regression suite: PUB 3015 (2026), pp. 166–168. These are lookup-table minute checks at threshold **1.0 kn**; they are **not** end-to-end independent validation of event timestamps.

| Table | Case | Previous maximum (kn) | Following maximum (kn) | Minutes before | Minutes after | Automated test |
|---|---|---:|---:|---:|---:|---|
| G | i | 2.3 | 1.5 | 58 | 67 | `test_published_worked_examples` |
| D | i | 3.9 | 1.2 | 27 | 75 | `test_published_worked_examples` |
| G | ii | 2.5 | 2.6 | 150 | 150 | `test_published_worked_examples` |
| C | ii | 3.0 | 2.1 | 132 | 140 | `test_published_worked_examples` |
| G | iii | 2.5 | 2.4 | 109 | 110 | `test_published_worked_examples` |

The code's `_nearest_minutes` selects the nearest available table intensity and returns no value on an unresolved exact midpoint tie. The tie behavior is intentionally conservative; the authoritative SHOA rounding convention has not yet been verified.

## Coverage and outstanding evidence

| Control | Current coverage | Required to claim independent SHOA validation |
|---|---|---|
| Five published worked examples | Automated table lookup assertions | Recheck transcription against page images, including table headings and units |
| Kirke date/time example | Window clipping test on 2026-09-03 19:00 | Independently transcribe source event, expected start/end and local civil time |
| 0–10 kn threshold bounds | Regression matrix, invalid-value rejection | Identify each supported empirical threshold in station registry and source publication |
| Unlisted thresholds | Marked `CALCULATED_CONTINUOUS` | Quantify model errors against independent observed/published benchmarks; never imply SHOA endorsement |
| Midnight transitions | Regression of clipped intervals | Independent source cases across date boundaries and applicable time-zone changes |
| Missing event/table coverage | Explicit empty result diagnostic | Audit omitted events and tie/missing table entries |
| Operational use | Planning disclaimer | Navigational review of SHOA tables and observed conditions by a qualified mariner |

## Release acceptance policy

1. Keep the original SHOA-derived values and source identifiers unchanged during comparison.
2. Record **expected**, **actual**, **difference**, **station**, **civil timestamp**, **threshold**, **method**, **source page** for each independent case.
3. A missing reference is **NOT VALIDATED**, never an implicit pass.
4. Do not use model agreement with itself as independent evidence.
5. Do not declare the Kirke current prediction 'exact' or suitable as the sole basis for navigation.

## Next data acquisition

Capture the relevant official 2026 PUB 3015 page images or an authoritative machine-readable extract for Kirke event times and the worked examples, then add fixed independent expected-value fixtures. Verify edition, page number, station, local time convention, direction and units before comparing.
