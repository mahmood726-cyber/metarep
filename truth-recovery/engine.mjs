// engine.mjs -- replication-probability core EXTRACTED VERBATIM from metarep.html

function normalCDF(x) {
  if (x > 8) return 1; if (x < -8) return 0;
  const a1=0.254829592,a2=-0.284496736,a3=1.421413741,a4=-1.453152027,a5=1.061405429,p=0.3275911;
  const s = x < 0 ? -1 : 1;
  const ax = Math.abs(x) / Math.sqrt(2);
  const t = 1 / (1 + p * ax);
  const y = 1 - (((((a5*t+a4)*t)+a3)*t+a2)*t+a1)*t*Math.exp(-ax*ax);
  return 0.5 * (1 + s * y);
}

function normalQuantile(p) {
  if (p <= 0) return -Infinity; if (p >= 1) return Infinity; if (p === 0.5) return 0;
  const pLow = p < 0.5 ? p : 1 - p;
  const t = Math.sqrt(-2 * Math.log(pLow));
  let z = t - (2.515517 + 0.802853*t + 0.010328*t*t) / (1 + 1.432788*t + 0.189269*t*t + 0.001308*t*t*t);
  return p < 0.5 ? -z : z;
}


function repProb(theta, tau2, seNew, alpha) {
  if (!isFinite(theta) || !isFinite(tau2) || !isFinite(seNew) || seNew <= 0) return 0;
  const zAlpha = normalQuantile(1 - (alpha ?? 0.05) / 2);
  const absTheta = Math.abs(theta);
  const predSD = Math.sqrt(tau2 + seNew * seNew);
  if (predSD <= 0) return absTheta > zAlpha * seNew ? 1 : 0;
  return normalCDF((absTheta - zAlpha * seNew) / predSD);
}

function classicalPower(theta, seNew, alpha) {
  const zAlpha = normalQuantile(1 - (alpha ?? 0.05) / 2);
  const absTheta = Math.abs(theta);
  return normalCDF(absTheta / seNew - zAlpha);
}

export { repProb, classicalPower, normalCDF, normalQuantile };
