import numpy as np
obs = np.array([9, 16, 21])
def run(p_lo, p_hi, q_hi, M_lo, M_hi, seed=1, N=1_500_000):
    rng = np.random.default_rng(seed)
    p = np.exp(rng.uniform(np.log(p_lo), np.log(p_hi), N))
    q = rng.uniform(0, q_hi, N)
    M = np.exp(rng.uniform(np.log(M_lo), np.log(M_hi), N))
    cum = np.zeros(N); traj = []
    for t in range(9):
        n = np.clip((p + q * cum / M) * (M - cum), 1e-9, None); traj.append(n); cum += n
    traj = np.array(traj)
    ll = (obs[:, None] * np.log(traj[:3]) - traj[:3]).sum(0)
    w = np.exp(ll - ll.max()); w /= w.sum()
    idx = rng.choice(N, 200_000, p=w)
    pred = rng.poisson(traj[8][idx])
    return {k: int(np.percentile(pred, k)) for k in (10, 25, 50, 75, 90)}, round(1/(w**2).sum())
variants = {
 "A base: p .001-.05, q 0-.5, M 100-3000": (0.001, 0.05, 0.5, 100, 3000),
 "B narrower q 0-.3":                     (0.001, 0.05, 0.3, 100, 3000),
 "C wider M 60-10000":                    (0.001, 0.05, 0.5, 60, 10000),
 "D wider q 0-1":                         (0.001, 0.05, 1.0, 100, 3000),
 "E wider p .0005-.2":                    (0.0005, 0.2, 0.5, 100, 3000),
}
for name, args in variants.items():
    print(name, *run(*args))
