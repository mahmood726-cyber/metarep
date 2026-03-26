# REVIEW CLEAN — Round 2 (5 Personas, All P0+P1 Fixed)
## Multi-Persona Review: metarep.html (668 lines)
### Date: 2026-03-26
### Summary: R1: 3P0+7P1 fixed. R2: 1P0+5P1 fixed. Total: 4P0+12P1 = 16 fixes. 20/20 tests pass.

---

## Round 2 Fixes (2026-03-26)
- **P0-1** [FIXED] [SM]: Chart `renderRepCurve` used different SE formula than `seForNewStudy` — now calls `seForNewStudy(scaleType, n, sePool, k)`
- **P1-1** [FIXED] [SM+DE]: Diff-scale `seForNewStudy` hardcoded refN=200 — now uses `window._diffRefN` set per example (SSRI: 150)
- **P1-2** [FIXED] [SM]: Log scale skipped I2-to-tau2 conversion — added else block
- **P1-3** [FIXED] [SM+DE]: About modal + manuscript claimed tau2 always reduces P(rep) — corrected to note paradoxical increase for underpowered studies
- **P1-4** [FIXED] [SE]: R export hardcoded ratio SE formula — now branches on scaleType for both se_new and curve
- **P2-1** [FIXED] [SE]: Dead variable `sThLog` removed

## Round 1 Fixes (2026-03-25)
- **P0-1** [FIXED]: I2-to-tau2 uses `seLog^2 * k` (typical vi, not pooled vi)
- **P0-2** [FIXED]: New `seForNewStudy()` helper for ratio + diff scales
- **P0-3** [FIXED]: Dead `minNForRep` function + dead `seNew` variable removed
- **P1-1** [FIXED]: Ratio-scale 50% event rate assumption documented
- **P1-2** [FIXED]: Delta-method SE/theta degradation documented
- **P1-3** [FIXED]: Compute button `type="button"`
- **P1-4** [FIXED]: aria-live narrowed to gauge
- **P1-5** [FIXED]: Min-N proper binary search (30 iterations)
- **P1-6** [FIXED]: `Object.freeze()` on `_lastRep`
- **P1-7** [FIXED]: tau2 tooltip + aria-describedby

## Remaining P2 (deferred)
- I2=100 → Infinity tau2 (edge case, low impact)
- Dark mode gauge label contrast on green background
