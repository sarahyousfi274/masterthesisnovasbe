"""G3 reference distribution: new paying customers in month 9, given 9, 16, 21
in months 1-3. Discrete-time Bass model (Bass 1969) with broad monthly priors,
conditioned on the pilot data by importance weighting (Poisson likelihood).

n_t = (p + q * N_{t-1} / M) * (M - N_{t-1}),  N_t = cumulative adopters.
Priors (monthly scale; annual meta-analytic values of Sultan et al. 1990 are
not used unscaled):
  p ~ LogUniform(0.001, 0.05)   innovation (base variant A)
  q ~ Uniform(0, 0.5)           imitation
  M ~ LogUniform(100, 3000)     customers the channel can reach
Observation: Poisson around the model's monthly values.
Prediction for month 9 includes Poisson noise.
"""
import numpy as np
rng = np.random.default_rng(20261020)
N = 2_000_000
obs = np.array([9, 16, 21])

p = np.exp(rng.uniform(np.log(0.001), np.log(0.05), N))
q = rng.uniform(0, 0.5, N)
M = np.exp(rng.uniform(np.log(100), np.log(3000), N))

cum = np.zeros(N); traj = []
for t in range(1, 10):
    n = (p + q * cum / M) * (M - cum)
    n = np.clip(n, 1e-9, None)
    traj.append(n); cum = cum + n
traj = np.array(traj)  # 9 x N
lam = traj[:3]
loglik = (obs[:, None] * np.log(lam) - lam).sum(0)
w = np.exp(loglik - loglik.max()); w /= w.sum()
ess = 1 / (w ** 2).sum()
idx = rng.choice(N, size=200_000, p=w)
pred = rng.poisson(traj[8][idx])
pct = {k: int(np.percentile(pred, k)) for k in (10, 25, 50, 75, 90)}
print("ESS", round(ess), "| month-9 percentiles", pct)
print("mean", round(pred.mean(), 1), "| P(<=57)", round((pred <= 57).mean(), 3))
print("posterior medians p,q,M:", np.median(p[idx]).round(4), np.median(q[idx]).round(3), np.median(M[idx]).round(0))
# share of accepted paths that are already decreasing by month 9
print("share saturating by month 9:", round((traj[8][idx] < traj[2][idx]).mean(), 3))
