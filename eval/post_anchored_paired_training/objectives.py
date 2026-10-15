"""Task-aware CE and one-way KL; shared parameters are not a frozen teacher."""
import torch


def ce(logits, target):
    return -logits.log_softmax(-1).gather(-1, target[..., None]).squeeze(-1).mean(1)


def transfer(post_logits, auxiliary_logits, routing, temperature=2.):
    # routing maps independent auxiliary rows to post rows, averaging group probabilities.
    q = torch.bmm(routing, (auxiliary_logits/temperature).softmax(-1)).detach()
    logp = (post_logits/temperature).log_softmax(-1)
    value = (q*(q.clamp_min(1e-30).log()-logp)).sum(-1).mean(1)*temperature**2
    return value, q


def objective(post_logits, auxiliary_logits, yp, ya, routing, coefficients, regularizer):
    lp, la = ce(post_logits, yp), ce(auxiliary_logits, ya)
    lk, _ = transfer(post_logits, auxiliary_logits, routing)
    return .5*(lp+la)+coefficients*lk+regularizer, (lp, la, lk, regularizer)
