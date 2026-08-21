from datetime import time, timedelta, timezone

import pytest

from app.domain.errors import DomainError
from app.domain.timeframes import (
    ManualTimeline,
    TimeframeBreakWindow,
    generate_manual_timeframe_template,
    generate_timeframe_template,
)


def test_generate_timeframe_template_calculates_daily_capacity():
    result = generate_timeframe_template(
        start_time=time(7),
        end_time=time(17, 30),
        block_duration_minutes=135,
        group_duration_minutes=45,
    )

    assert result.blocks_per_day == 4
    assert result.groups_per_block == 3
    assert result.capacity_per_day == 12
    assert result.unused_minutes == 90
    assert (result.blocks[0].start_time, result.blocks[0].end_time) == (
        time(7),
        time(9, 15),
    )
    assert [
        (slot.start_time, slot.end_time) for slot in result.blocks[0].group_slots
    ] == [
        (time(7), time(7, 45)),
        (time(7, 45), time(8, 30)),
        (time(8, 30), time(9, 15)),
    ]


def test_generate_timeframe_template_is_deterministic():
    values = {
        "start_time": time(8),
        "end_time": time(12),
        "block_duration_minutes": 120,
        "group_duration_minutes": 40,
    }

    first = generate_timeframe_template(**values)
    second = generate_timeframe_template(**values)

    assert first == second
    assert [block.sequence_number for block in first.blocks] == [1, 2]
    assert [slot.sequence_number for slot in first.blocks[0].group_slots] == [1, 2, 3]


def test_generate_timeframe_template_respects_block_gaps_and_lunch_break():
    result = generate_timeframe_template(
        start_time=time(7),
        end_time=time(17, 30),
        block_duration_minutes=120,
        group_duration_minutes=40,
        break_between_blocks_minutes=15,
        break_windows=(
            TimeframeBreakWindow("Nghi trua", time(11, 30), time(13)),
        ),
    )

    assert [(block.start_time, block.end_time) for block in result.blocks] == [
        (time(7), time(9)),
        (time(9, 15), time(11, 15)),
        (time(13), time(15)),
        (time(15, 15), time(17, 15)),
    ]
    assert result.blocks_per_day == 4
    assert result.groups_per_block == 3
    assert result.capacity_per_day == 12
    assert result.unused_minutes == 30
    assert result.break_window_minutes == 90
    assert result.applied_block_break_minutes == 30
    assert result.total_break_minutes == 120
    for block in result.blocks:
        assert block.group_slots[0].start_time == block.start_time
        assert block.group_slots[-1].end_time == block.end_time
        assert all(
            previous.end_time == following.start_time
            for previous, following in zip(block.group_slots, block.group_slots[1:])
        )


def test_generate_timeframe_template_sorts_flexible_break_windows():
    result = generate_timeframe_template(
        start_time=time(7),
        end_time=time(17),
        block_duration_minutes=60,
        group_duration_minutes=30,
        break_between_blocks_minutes=0,
        break_windows=(
            TimeframeBreakWindow("Chieu", time(15), time(15, 15)),
            TimeframeBreakWindow("Trua", time(11, 30), time(13)),
        ),
    )

    assert [item.name for item in result.break_windows] == ["Trua", "Chieu"]


@pytest.mark.parametrize(
    ("break_windows", "code"),
    [
        (
            (
                TimeframeBreakWindow("A", time(11), time(12)),
                TimeframeBreakWindow("B", time(11, 30), time(13)),
            ),
            "TIMEFRAME_BREAK_OVERLAP",
        ),
        (
            (TimeframeBreakWindow("Outside", time(6), time(8)),),
            "TIMEFRAME_BREAK_OUTSIDE_RANGE",
        ),
        (
            (TimeframeBreakWindow("Invalid", time(12), time(11)),),
            "TIMEFRAME_BREAK_INVALID_RANGE",
        ),
        (
            (TimeframeBreakWindow("   ", time(11), time(12)),),
            "TIMEFRAME_BREAK_NAME_REQUIRED",
        ),
        (
            (
                TimeframeBreakWindow(
                    "Offset",
                    time(11, tzinfo=timezone(timedelta(hours=7))),
                    time(12, tzinfo=timezone(timedelta(hours=7))),
                ),
            ),
            "TIMEFRAME_TIMEZONE_NOT_ALLOWED",
        ),
    ],
)
def test_generate_timeframe_template_rejects_invalid_break_windows(break_windows, code):
    with pytest.raises(DomainError, match=code):
        generate_timeframe_template(
            start_time=time(7),
            end_time=time(17),
            block_duration_minutes=120,
            group_duration_minutes=40,
            break_between_blocks_minutes=15,
            break_windows=break_windows,
        )


@pytest.mark.parametrize(
    ("start", "end", "block_minutes", "group_minutes", "code"),
    [
        (time(17), time(7), 135, 45, "TIMEFRAME_INVALID_RANGE"),
        (time(7), time(8), 135, 45, "TIMEFRAME_NO_BLOCK_FITS"),
        (time(7), time(17), 130, 45, "GROUP_DURATION_NOT_DIVISIBLE"),
        (time(7), time(17), 0, 45, "TIMEFRAME_DURATION_INVALID"),
        (
            time(7, tzinfo=timezone(timedelta(hours=7))),
            time(17, tzinfo=timezone(timedelta(hours=7))),
            120,
            40,
            "TIMEFRAME_TIMEZONE_NOT_ALLOWED",
        ),
    ],
)
def test_generate_timeframe_template_rejects_invalid_configuration(
    start,
    end,
    block_minutes,
    group_minutes,
    code,
):
    with pytest.raises(DomainError, match=code):
        generate_timeframe_template(
            start_time=start,
            end_time=end,
            block_duration_minutes=block_minutes,
            group_duration_minutes=group_minutes,
        )


def test_generate_timeframe_template_rejects_negative_block_gap():
    with pytest.raises(DomainError, match="TIMEFRAME_DURATION_INVALID"):
        generate_timeframe_template(
            start_time=time(7),
            end_time=time(17),
            block_duration_minutes=120,
            group_duration_minutes=40,
            break_between_blocks_minutes=-1,
        )


def test_generate_manual_timeframe_template_normalizes_edited_timelines():
    result = generate_manual_timeframe_template(
        group_duration_minutes=45,
        timelines=(
            ManualTimeline(time(13), time(14, 30), 2),
            ManualTimeline(time(7, 30), time(9), 2),
            ManualTimeline(time(9, 15), time(11, 30), 3),
        ),
    )

    assert result.start_time == time(7, 30)
    assert result.end_time == time(14, 30)
    assert result.blocks_per_day == 3
    assert result.capacity_per_day == 7
    assert result.block_duration_minutes is None
    assert result.groups_per_block is None
    assert result.break_between_blocks_minutes is None
    assert result.break_window_minutes == 105
    assert result.total_break_minutes == 105
    assert [(block.start_time, block.end_time) for block in result.blocks] == [
        (time(7, 30), time(9)),
        (time(9, 15), time(11, 30)),
        (time(13), time(14, 30)),
    ]
    assert [len(block.group_slots) for block in result.blocks] == [2, 3, 2]
    assert result.blocks[1].group_slots[-1].end_time == time(11, 30)


@pytest.mark.parametrize(
    ("timelines", "code"),
    [
        ((ManualTimeline(time(7), time(9), 3),), "MANUAL_TIMELINE_DURATION_MISMATCH"),
        (
            (
                ManualTimeline(time(7), time(8, 30), 2),
                ManualTimeline(time(8), time(9, 30), 2),
            ),
            "MANUAL_TIMELINE_OVERLAP",
        ),
        (
            (ManualTimeline(time(7, 0, 30), time(7, 45, 30), 1),),
            "MANUAL_TIMELINE_MINUTE_ALIGNMENT_REQUIRED",
        ),
        ((), "MANUAL_TIMELINE_REQUIRED"),
    ],
)
def test_generate_manual_timeframe_template_rejects_invalid_timelines(timelines, code):
    with pytest.raises(DomainError, match=code):
        generate_manual_timeframe_template(
            group_duration_minutes=45,
            timelines=timelines,
        )
