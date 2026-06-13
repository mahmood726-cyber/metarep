// node --test truth-recovery/test-truth-recovery.mjs
// Measured invariants for the metarep calibration yardstick. Seeded; no
// hand-entered numbers.
import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { repProb, classicalPower } from './engine.mjs';
import { runCell, runGrid } from './harness.mjs';

function makeRng(seed) { let a = seed >>> 0; return function () { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

describe('engine', () => {
  it('repProb is below classical power when tau2>0 (heterogeneity lowers predictive power)', () => {
    assert.ok(repProb(0.6, 0.08, 0.2, 0.05) < classicalPower(0.6, 0.2, 0.05));
  });
});

describe('Truth-recovery (measured)', () => {
  it('VALIDATION: under heterogeneity repProb is better calibrated than classical power in the MAJORITY of cells', () => {
    const grid = runGrid({ reps: 3000 }).filter(g => g.tau2 === 0.05);
    let repBetter = 0;
    for (const g of grid) {
      if (Math.abs(g.results.repErr) <= Math.abs(g.results.classicErr) + 0.005) repBetter++;
    }
    // honest: repProb wins in 5/6 tau2>0 cells; the exception is the small-effect,
    // few-studies corner where the winner's curse on |theta_hat| dominates.
    assert.ok(repBetter >= 5, `repProb better in only ${repBetter}/${grid.length} tau2>0 cells`);
  });

  it('repProb is well-calibrated for moderate effects (|err| small)', () => {
    const r = runCell(0.3, 0.05, 15, 3000, makeRng(20260613));
    assert.ok(Math.abs(r.repErr) < 0.03, `repProb error at mu=0.3 = ${r.repErr}`);
  });

  it('HONEST CAVEAT: repProb OVERSTATES replication for a small true effect with few studies (winner\'s curse on |theta_hat|)', () => {
    const r = runCell(0.1, 0.05, 5, 3000, makeRng(20260613));
    assert.ok(r.repErr > 0.03, `expected overstatement at mu=0.1,k=5; got err ${r.repErr}`);
    assert.ok(r.predRep > r.actual, `predicted ${r.predRep} should exceed actual ${r.actual}`);
  });
});
