"""Trial-level safe-performance and non-inferiority reporting for CASP."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from .decoder import DecodedTrial


@dataclass
class SafeMetrics:
    trials: int
    correct_accept_rate: float
    wrong_accept_rate: float
    accepted_accuracy: float
    coverage: float
    rejection_or_repeat_rate: float
    reseat_rate: float


@dataclass
class NonInferiorityResult:
    metric: str
    candidate_minus_reference: float
    bootstrap_lower_bound: float
    bootstrap_upper_bound: float
    noninferiority_margin: float
    false_accept_constraint_met: bool
    conclusion: str


def safe_metrics(results: list[DecodedTrial]) -> SafeMetrics:
    known = [result for result in results if result.true_symbol is not None]
    if not known:
        return SafeMetrics(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    accepted = [result for result in known if result.action == "ACCEPT"]
    correct_accepts = sum(result.predicted_symbol == result.true_symbol for result in accepted)
    wrong_accepts = len(accepted) - correct_accepts
    trials = len(known)
    return SafeMetrics(
        trials=trials,
        correct_accept_rate=correct_accepts / trials,
        wrong_accept_rate=wrong_accepts / trials,
        accepted_accuracy=correct_accepts / len(accepted) if accepted else 0.0,
        coverage=len(accepted) / trials,
        rejection_or_repeat_rate=sum(result.action in {"REPEAT", "REJECT"} for result in known) / trials,
        reseat_rate=sum(result.action == "RESEAT_HEADSET" for result in known) / trials,
    )


def assess_noninferiority(
    reference: list[DecodedTrial],
    candidate: list[DecodedTrial],
    *,
    margin: float = 0.05,
    false_accept_tolerance: float = 0.02,
    bootstrap_samples: int = 2000,
    seed: int = 7,
) -> NonInferiorityResult:
    """Compare correct-accept rates with a false-accept safety constraint.

    Both result sets must contain the same labelled trial IDs. The primary
    endpoint is correct accepted outputs per attempted trial, preventing a
    candidate from appearing superior merely by abstaining on every hard trial.
    The result is an engineering comparison, not a clinical statistical claim.
    """

    ref = {item.trial_id: item for item in reference if item.true_symbol is not None}
    cand = {item.trial_id: item for item in candidate if item.true_symbol is not None}
    if set(ref) != set(cand) or not ref:
        raise ValueError("reference and candidate need identical labelled trial IDs")
    ids = np.asarray(sorted(ref), dtype=int)
    reference_correct = np.asarray([
        int(ref[i].action == "ACCEPT" and ref[i].predicted_symbol == ref[i].true_symbol) for i in ids
    ])
    candidate_correct = np.asarray([
        int(cand[i].action == "ACCEPT" and cand[i].predicted_symbol == cand[i].true_symbol) for i in ids
    ])
    reference_wrong = np.asarray([
        int(ref[i].action == "ACCEPT" and ref[i].predicted_symbol != ref[i].true_symbol) for i in ids
    ])
    candidate_wrong = np.asarray([
        int(cand[i].action == "ACCEPT" and cand[i].predicted_symbol != cand[i].true_symbol) for i in ids
    ])
    observed = float(candidate_correct.mean() - reference_correct.mean())
    rng = np.random.default_rng(seed)
    draws = np.empty(bootstrap_samples, dtype=float)
    for index in range(bootstrap_samples):
        sample = rng.integers(0, len(ids), size=len(ids))
        draws[index] = candidate_correct[sample].mean() - reference_correct[sample].mean()
    lower, upper = np.quantile(draws, [0.025, 0.975])
    false_accept_constraint = float(candidate_wrong.mean() - reference_wrong.mean()) <= false_accept_tolerance
    conclusion = "NON_INFERIOR" if lower >= -margin and false_accept_constraint else "INCONCLUSIVE_OR_NOT_NONINFERIOR"
    return NonInferiorityResult(
        metric="correct_accept_rate",
        candidate_minus_reference=observed,
        bootstrap_lower_bound=float(lower),
        bootstrap_upper_bound=float(upper),
        noninferiority_margin=margin,
        false_accept_constraint_met=false_accept_constraint,
        conclusion=conclusion,
    )


def as_dict(value: SafeMetrics | NonInferiorityResult) -> dict:
    return asdict(value)

