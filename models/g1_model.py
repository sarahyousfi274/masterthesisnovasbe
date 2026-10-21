"""G1 reference step: two-period launch model.

Period 1 (launch): budget B, share s on the first channel, (1-s) split equally
over K untested alternative channels. Period 2 (scale-up): budget h*B, put into
the best channel known after period 1.

Each channel 'works' independently with probability p (base rate). A working
channel acquires customers at cost c; a channel that does not work acquires at
cost c / r_f (r_f = relative efficiency of a failing channel, 0..1).
A test on an alternative reveals whether it works with probability
d = min(1, spend / m), where m is the minimum spend for a reliable read.
The first channel's performance is always observed if s > 0.

Unit of output: expected customers in units of B / c.
"""
from itertools import product

def expected(s, p, K=3, r_f=0.25, m_rel=0.2, h=1.0):
    # m_rel = minimum test spend per channel as share of B
    # period 1
    e1 = s * (p * 1 + (1 - p) * r_f)
    alt_spend = (1 - s) / K if K else 0
    e1 += (1 - s) * (p * 1 + (1 - p) * r_f)
    # detection probability per alternative
    d = min(1.0, alt_spend / m_rel) if alt_spend > 0 else 0.0
    # probability that at least one tested alternative is identified as working
    q_found = 1 - (1 - p * d) ** K
    blind = p * 1 + (1 - p) * r_f
    # period 2
    if s > 0:
        e2 = p * 1 + (1 - p) * (q_found * 1 + (1 - q_found) * blind)
    else:
        e2 = q_found * 1 + (1 - q_found) * blind
    return e1 + h * e2

STEPS = [1.0, 0.7, 0.4, 0.2]

def best(p, **kw):
    vals = {s: expected(s, p, **kw) for s in STEPS}
    return max(vals, key=vals.get), vals

if __name__ == "__main__":
    for p in (0.3, 0.6):
        b, vals = best(p)
        print(f"p={p} base case -> best {b}", {k: round(v, 3) for k, v in vals.items()})
    print()
    # sensitivity grid
    from collections import Counter
    for p in (0.3, 0.6):
        cnt = Counter(); rows = []
        for r_f, m_rel, h, K in product((0.0, 0.25, 0.5), (0.1, 0.2, 0.3), (0.5, 1.0, 2.0), (2, 3)):
            b, _ = best(p, r_f=r_f, m_rel=m_rel, h=h, K=K)
            cnt[b] += 1
        print(f"p={p} grid ({sum(cnt.values())} combos):", dict(cnt))
