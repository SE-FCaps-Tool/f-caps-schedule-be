"""Round-type groups shared by the API, result workflow and scheduler.

The old values are retained as legacy database values. New rounds should use
the canonical five-name vocabulary.
"""

REVIEW_1_1_TYPES = frozenset({"REVIEW_1_1", "REVIEW_1"})
REVIEW_2_1_TYPES = frozenset({"REVIEW_2_1", "REVIEW_2"})
DEFENSE_1_1_TYPES = frozenset({"DEFENSE_1_1", "REVIEW_3"})
DEFENSE_1_2_TYPES = frozenset({"DEFENSE_1_2", "DEFENSE_1"})
RESULT_OWNER_TYPES = DEFENSE_1_1_TYPES | {"DEFENSE_2"}

ROUND_REVIEWER_COUNTS = {
    "REVIEW_1_1": 2,
    "REVIEW_1": 2,
    "REVIEW_2_1": 2,
    "REVIEW_2": 2,
    "DEFENSE_1_1": 3,
    "REVIEW_3": 3,
    "DEFENSE_1_2": 5,
    "DEFENSE_1": 5,
    "DEFENSE_2": 5,
}
