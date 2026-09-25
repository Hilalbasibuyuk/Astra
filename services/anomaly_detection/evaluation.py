from dataclasses import dataclass


@dataclass
class EvaluationMetrics:
    true_positive: int
    true_negative: int
    false_positive: int
    false_negative: int

    precision: float
    recall: float
    f1_score: float


def evaluate_predictions(
    ground_truth: list[bool],
    predictions: list[bool],
) -> EvaluationMetrics:

    if len(ground_truth) != len(predictions):
        raise ValueError(
            "Ground truth and predictions must have the same length."
        )

    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0

    for actual, predicted in zip(
        ground_truth,
        predictions,
    ):
        if actual and predicted:
            true_positive += 1

        elif not actual and not predicted:
            true_negative += 1

        elif not actual and predicted:
            false_positive += 1

        elif actual and not predicted:
            false_negative += 1

    precision_denominator = (
        true_positive + false_positive
    )

    recall_denominator = (
        true_positive + false_negative
    )

    precision = (
        true_positive / precision_denominator
        if precision_denominator
        else 0.0
    )

    recall = (
        true_positive / recall_denominator
        if recall_denominator
        else 0.0
    )

    f1_denominator = precision + recall

    f1_score = (
        2 * precision * recall / f1_denominator
        if f1_denominator
        else 0.0
    )

    return EvaluationMetrics(
        true_positive=true_positive,
        true_negative=true_negative,
        false_positive=false_positive,
        false_negative=false_negative,
        precision=precision,
        recall=recall,
        f1_score=f1_score,
    )