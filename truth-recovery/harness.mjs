// ============================================================
// harness.mjs -- Truth-recovery yardstick for metarep.
//
// metarep predicts the probability that the NEXT study replicates (significant +
// same direction), using P(rep)=Phi((|theta|-z*se)/sqrt(tau2+se^2)) with the
// pooled estimate. The honest test is CALIBRATION: does the predicted replication
// probability match the ACTUAL replication rate under a known truth -- and is the
// heterogeneity-aware repProb better calibrated than classical power (which
// ignores tau2)?
//
// A subtlety it probes: the formula plugs in |theta_hat| of the ESTIMATED pooled
// effect. Because |.| of a noisy estimate is upward biased (winner's curse), the
// prediction may OVERSTATE replication, especially for small true effects / few
// studies. We measure that.
//
// Truth-first: every number printed comes from seeded simulation here.
// Run:  node truth-recovery/harness.mjs --reps 4000
// ============================================================

import { repProb, classicalPower } from './engine.mjs';

const BASE_SEED = 20260613;
const ZA = 1.959963984540054;
function makeRng(seed) { let a = seed >>> 0; return function () { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
function randn(rng) { let u1 = rng(), u2 = rng(); if (u1 < 1e-12) u1 = 1e-12; return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2); }

function dlPool(yi, vi) {
  const k = yi.length;
  const w = vi.map(v => 1 / v); const sw = w.reduce((a, b) => a + b, 0);
  const muFE = yi.reduce((s, y, i) => s + w[i] * y, 0) / sw;
  const Q = yi.reduce((s, y, i) => s + w[i] * (y - muFE) ** 2, 0);
  const C = sw - w.reduce((s, x) => s + x * x, 0) / sw;
  const tau2 = Math.max(0, (Q - (k - 1)) / C);
  const ws = vi.map(v => 1 / (v + tau2)); const sws = ws.reduce((a, b) => a + b, 0);
  const mu = yi.reduce((s, y, i) => s + ws[i] * y, 0) / sws;
  return { mu, tau2, se: Math.sqrt(1 / sws) };
}

export function runCell(muTrue, tau2True, k, reps, rng, nNewReps = 30) {
  let predRep = 0, predClassic = 0, actual = 0, n = 0;
  const seLo = 0.12, seHi = 0.35;
  for (let r = 0; r < reps; r++) {
    const se = [], yi = [], vi = [];
    for (let i = 0; i < k; i++) {
      const s = Math.exp(Math.log(seLo) + (Math.log(seHi) - Math.log(seLo)) * rng());
      const theta = muTrue + Math.sqrt(tau2True) * randn(rng);
      se.push(s); yi.push(theta + s * randn(rng)); vi.push(s * s);
    }
    const p = dlPool(yi, vi);
    const seNew = [...se].sort((a, b) => a - b)[Math.floor(k / 2)];   // typical study SE
    predRep += repProb(p.mu, p.tau2, seNew, 0.05);
    predClassic += classicalPower(p.mu, seNew, 0.05);
    // actual replication rate vs the OBSERVED pooled direction (the tool's definition)
    const dir = Math.sign(p.mu) || 1;
    let rep = 0;
    for (let j = 0; j < nNewReps; j++) {
      const thetaNew = muTrue + Math.sqrt(tau2True) * randn(rng);
      const yNew = thetaNew + seNew * randn(rng);
      if (Math.abs(yNew) > ZA * seNew && Math.sign(yNew) === dir) rep++;
    }
    actual += rep / nNewReps;
    n++;
  }
  return {
    predRep: +(predRep / n).toFixed(3), predClassic: +(predClassic / n).toFixed(3),
    actual: +(actual / n).toFixed(3),
    repErr: +((predRep - actual) / n).toFixed(3), classicErr: +((predClassic - actual) / n).toFixed(3),
  };
}

export function runGrid({ reps = 4000 } = {}) {
  const rng = makeRng(BASE_SEED);
  const cells = [];
  for (const mu of [0.1, 0.3, 0.5]) for (const tau2 of [0, 0.05]) for (const k of [5, 15])
    cells.push({ mu, tau2, k, results: runCell(mu, tau2, k, reps, rng) });
  return cells;
}

const isMain = process.argv[1]?.endsWith('harness.mjs');
if (isMain) {
  const i = process.argv.indexOf('--reps');
  const reps = i >= 0 ? Number(process.argv[i + 1]) : 4000;
  const t0 = Date.now();
  const grid = runGrid({ reps });
  console.log(`\n# Truth-recovery yardstick -- metarep (replication probability calibration)`);
  console.log(`reps=${reps}/cell  seed=${BASE_SEED}\n`);
  console.log('mu   tau2  k  | pred repProb | pred classical | ACTUAL | repProb err | classical err');
  for (const g of grid) {
    const r = g.results;
    console.log(`${String(g.mu).padEnd(4)} ${String(g.tau2).padEnd(5)} ${String(g.k).padStart(2)} | ` +
      `${String(r.predRep).padStart(12)} | ${String(r.predClassic).padStart(14)} | ${String(r.actual).padStart(6)} | ` +
      `${String(r.repErr).padStart(11)} | ${String(r.classicErr).padStart(13)}`);
  }
  console.log(`\n(err = predicted - actual; positive = OVERSTATES replication. ${((Date.now() - t0) / 1000).toFixed(1)}s)`);
}
