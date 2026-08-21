from dataclasses import dataclass
from datetime import UTC, datetime, time, timedelta

from app.domain.errors import DomainError


@dataclass(frozen=True)
class GeneratedTemplateSlot:
    sequence_number: int
    start_time: time
    end_time: time


@dataclass(frozen=True)
class TimeframeBreakWindow:
    name: str
    start_time: time
    end_time: time


@dataclass(frozen=True)
class ManualTimeline:
    start_time: time
    end_time: time
    groups_per_slot: int


@dataclass(frozen=True)
class GeneratedTemplateBlock:
    sequence_number: int
    start_time: time
    end_time: time
    group_slots: tuple[GeneratedTemplateSlot, ...]


@dataclass(frozen=True)
class GeneratedTimeframeTemplate:
    start_time: time
    end_time: time
    block_duration_minutes: int | None
    group_duration_minutes: int
    break_between_blocks_minutes: int | None
    break_windows: tuple[TimeframeBreakWindow, ...]
    groups_per_block: int | None
    unused_minutes: int
    break_window_minutes: int
    applied_block_break_minutes: int
    blocks: tuple[GeneratedTemplateBlock, ...]

    @property
    def blocks_per_day(self) -> int:
        return len(self.blocks)

    @property
    def capacity_per_day(self) -> int:
        return sum(len(block.group_slots) for block in self.blocks)

    @property
    def total_break_minutes(self) -> int:
        return self.break_window_minutes + self.applied_block_break_minutes


def generate_timeframe_template(
    *,
    start_time: time,
    end_time: time,
    block_duration_minutes: int,
    group_duration_minutes: int,
    break_between_blocks_minutes: int = 0,
    break_windows: tuple[TimeframeBreakWindow, ...] = (),
) -> GeneratedTimeframeTemplate:
    all_times = (start_time, end_time) + tuple(
        item for window in break_windows for item in (window.start_time, window.end_time)
    )
    if any(value.utcoffset() is not None for value in all_times):
        raise DomainError(
            "TIMEFRAME_TIMEZONE_NOT_ALLOWED",
            "Timeframe times must be local wall-clock values without a UTC offset.",
        )
    if (
        block_duration_minutes <= 0
        or group_duration_minutes <= 0
        or break_between_blocks_minutes < 0
    ):
        raise DomainError("TIMEFRAME_DURATION_INVALID", "Durations must be positive.")
    if block_duration_minutes % group_duration_minutes != 0:
        raise DomainError(
            "GROUP_DURATION_NOT_DIVISIBLE",
            "Block duration must be divisible by group duration.",
        )
    anchor = datetime(2000, 1, 1, tzinfo=UTC)
    start_at = datetime.combine(anchor.date(), start_time)
    end_at = datetime.combine(anchor.date(), end_time)
    if end_at <= start_at:
        raise DomainError("TIMEFRAME_INVALID_RANGE", "endTime must be after startTime.")

    normalized_breaks = tuple(
        sorted(
            (
                TimeframeBreakWindow(
                    name=window.name.strip(),
                    start_time=window.start_time,
                    end_time=window.end_time,
                )
                for window in break_windows
            ),
            key=lambda item: (item.start_time, item.end_time, item.name),
        )
    )

    segments: list[tuple[datetime, datetime]] = []
    cursor = start_at
    break_window_minutes = 0
    for index, window in enumerate(normalized_breaks):
        if not window.name:
            raise DomainError("TIMEFRAME_BREAK_NAME_REQUIRED", "Break window name must not be blank.")
        break_start = datetime.combine(anchor.date(), window.start_time)
        break_end = datetime.combine(anchor.date(), window.end_time)
        if break_end <= break_start:
            raise DomainError(
                "TIMEFRAME_BREAK_INVALID_RANGE",
                "Each break window endTime must be after startTime.",
            )
        if break_start < start_at or break_end > end_at:
            raise DomainError(
                "TIMEFRAME_BREAK_OUTSIDE_RANGE",
                "Break windows must stay inside the Timeframe daily range.",
            )
        if index > 0:
            previous_end = datetime.combine(anchor.date(), normalized_breaks[index - 1].end_time)
            if break_start < previous_end:
                raise DomainError(
                    "TIMEFRAME_BREAK_OVERLAP",
                    "Break windows must not overlap.",
                )
        if cursor < break_start:
            segments.append((cursor, break_start))
        cursor = break_end
        break_window_minutes += int((break_end - break_start).total_seconds() // 60)
    if cursor < end_at:
        segments.append((cursor, end_at))

    block_delta = timedelta(minutes=block_duration_minutes)
    group_delta = timedelta(minutes=group_duration_minutes)
    gap_delta = timedelta(minutes=break_between_blocks_minutes)
    groups_per_block = block_duration_minutes // group_duration_minutes
    blocks = []
    unused_minutes = 0
    applied_block_break_minutes = 0
    for segment_start, segment_end in segments:
        segment_minutes = int((segment_end - segment_start).total_seconds() // 60)
        divisor = block_duration_minutes + break_between_blocks_minutes
        block_count = (segment_minutes + break_between_blocks_minutes) // divisor
        used_minutes = block_count * block_duration_minutes
        segment_break_minutes = max(0, block_count - 1) * break_between_blocks_minutes
        unused_minutes += segment_minutes - used_minutes - segment_break_minutes
        applied_block_break_minutes += segment_break_minutes
        for segment_index in range(block_count):
            block_start = segment_start + segment_index * (block_delta + gap_delta)
            blocks.append(
                GeneratedTemplateBlock(
                    sequence_number=len(blocks) + 1,
                    start_time=block_start.time(),
                    end_time=(block_start + block_delta).time(),
                    group_slots=tuple(
                        GeneratedTemplateSlot(
                            sequence_number=slot_index + 1,
                            start_time=(block_start + slot_index * group_delta).time(),
                            end_time=(block_start + (slot_index + 1) * group_delta).time(),
                        )
                        for slot_index in range(groups_per_block)
                    ),
                )
            )
    if not blocks:
        raise DomainError(
            "TIMEFRAME_NO_BLOCK_FITS",
            "No available segment is long enough for one block.",
        )
    return GeneratedTimeframeTemplate(
        start_time=start_time,
        end_time=end_time,
        block_duration_minutes=block_duration_minutes,
        group_duration_minutes=group_duration_minutes,
        break_between_blocks_minutes=break_between_blocks_minutes,
        break_windows=normalized_breaks,
        groups_per_block=groups_per_block,
        unused_minutes=unused_minutes,
        break_window_minutes=break_window_minutes,
        applied_block_break_minutes=applied_block_break_minutes,
        blocks=tuple(blocks),
    )


def generate_manual_timeframe_template(
    *,
    group_duration_minutes: int,
    timelines: tuple[ManualTimeline, ...],
) -> GeneratedTimeframeTemplate:
    if group_duration_minutes <= 0:
        raise DomainError("TIMEFRAME_DURATION_INVALID", "Group duration must be positive.")
    if not timelines:
        raise DomainError(
            "MANUAL_TIMELINE_REQUIRED",
            "At least one manual timeline is required.",
        )
    if any(
        value.utcoffset() is not None
        for timeline in timelines
        for value in (timeline.start_time, timeline.end_time)
    ):
        raise DomainError(
            "TIMEFRAME_TIMEZONE_NOT_ALLOWED",
            "Timeframe times must be local wall-clock values without a UTC offset.",
        )
    if any(
        value.second != 0 or value.microsecond != 0
        for timeline in timelines
        for value in (timeline.start_time, timeline.end_time)
    ):
        raise DomainError(
            "MANUAL_TIMELINE_MINUTE_ALIGNMENT_REQUIRED",
            "Manual timeline times must align to whole minutes.",
        )

    normalized = tuple(sorted(timelines, key=lambda item: (item.start_time, item.end_time)))
    anchor = datetime(2000, 1, 1, tzinfo=UTC)
    group_delta = timedelta(minutes=group_duration_minutes)
    blocks: list[GeneratedTemplateBlock] = []
    breaks: list[TimeframeBreakWindow] = []
    durations: list[int] = []
    group_counts: list[int] = []
    break_minutes = 0
    previous_end: datetime | None = None

    for index, timeline in enumerate(normalized, start=1):
        if timeline.groups_per_slot <= 0:
            raise DomainError(
                "MANUAL_TIMELINE_GROUP_COUNT_INVALID",
                "groupsPerSlot must be positive.",
            )
        start_at = datetime.combine(anchor.date(), timeline.start_time)
        end_at = datetime.combine(anchor.date(), timeline.end_time)
        if end_at <= start_at:
            raise DomainError(
                "MANUAL_TIMELINE_INVALID_RANGE",
                "Each manual timeline endTime must be after startTime.",
            )
        if previous_end is not None and start_at < previous_end:
            raise DomainError(
                "MANUAL_TIMELINE_OVERLAP",
                "Manual timelines must not overlap.",
            )
        duration_seconds = int((end_at - start_at).total_seconds())
        duration_minutes = duration_seconds // 60
        required_minutes = group_duration_minutes * timeline.groups_per_slot
        if duration_seconds != required_minutes * 60:
            raise DomainError(
                "MANUAL_TIMELINE_DURATION_MISMATCH",
                "Timeline duration must equal groupDurationMinutes multiplied by groupsPerSlot.",
            )
        if previous_end is not None and start_at > previous_end:
            gap_minutes = int((start_at - previous_end).total_seconds() // 60)
            breaks.append(
                TimeframeBreakWindow(
                    name=f"Khoảng nghỉ {len(breaks) + 1}",
                    start_time=previous_end.time(),
                    end_time=start_at.time(),
                )
            )
            break_minutes += gap_minutes

        blocks.append(
            GeneratedTemplateBlock(
                sequence_number=index,
                start_time=timeline.start_time,
                end_time=timeline.end_time,
                group_slots=tuple(
                    GeneratedTemplateSlot(
                        sequence_number=slot_index + 1,
                        start_time=(start_at + slot_index * group_delta).time(),
                        end_time=(start_at + (slot_index + 1) * group_delta).time(),
                    )
                    for slot_index in range(timeline.groups_per_slot)
                ),
            )
        )
        durations.append(duration_minutes)
        group_counts.append(timeline.groups_per_slot)
        previous_end = end_at

    common_duration = durations[0] if len(set(durations)) == 1 else None
    common_group_count = group_counts[0] if len(set(group_counts)) == 1 else None
    return GeneratedTimeframeTemplate(
        start_time=normalized[0].start_time,
        end_time=normalized[-1].end_time,
        block_duration_minutes=common_duration,
        group_duration_minutes=group_duration_minutes,
        break_between_blocks_minutes=None,
        break_windows=tuple(breaks),
        groups_per_block=common_group_count,
        unused_minutes=0,
        break_window_minutes=break_minutes,
        applied_block_break_minutes=0,
        blocks=tuple(blocks),
    )
