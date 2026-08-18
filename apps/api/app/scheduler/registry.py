HARD_RULES = tuple(f"H{i}" for i in range(1, 13))
SOFT_RULES = tuple(f"S{i}" for i in range(1, 9))
UNSCHEDULED_REASON_CODES = (
    "NO_REVIEWER_AVAILABILITY",
    "H1_CONFLICT",
    "H8_CONFLICT",
    "H11_CONTINUITY",
    "H12_QUOTA",
    "NO_ROOM",
    "NO_TIMESLOT",
)

