from uuid import UUID

RRF_RANK_OFFSET = 60


def _sort_key(result: tuple[UUID, float]) -> tuple[float, str]:
    child_id, score = result
    # sort highest scores first, using the ID to break ties.
    return -score, str(child_id)


def reciprocal_rank_fusion(
    rankings: list[list[UUID]], limit: int
) -> list[tuple[UUID, float]]:
    """Combine ranked ID lists and return the top IDs with their total scores."""
    combined_scores: dict[UUID, float] = {}

    for ranking in rankings:
        for rank, child_id in enumerate(ranking, start=1):
            # higher-ranked chunks contribute more to the total score.
            rank_score = 1 / (RRF_RANK_OFFSET + rank)
            previous_score = combined_scores.get(child_id, 0.0)
            combined_scores[child_id] = previous_score + rank_score

    ranked_results = sorted(combined_scores.items(), key=_sort_key)

    return ranked_results[:limit]
