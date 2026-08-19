from copy import deepcopy
from dataclasses import replace
from typing import Any

from app.domain.errors import DomainError
from app.scheduler.models import ScheduleVersion


class VersionStore:
    def __init__(self) -> None:
        self._versions: dict[int, ScheduleVersion] = {}
        self._next_id = 1

    def create(
        self,
        *,
        round_id: int,
        snapshot: dict[str, Any],
        algorithm_parameters: dict[str, Any] | None = None,
        random_seed: int | None = None,
        solver_status: str | None = None,
        objective: int = 0,
        soft_scores: dict[str, int] | None = None,
        unscheduled: tuple[dict[str, Any], ...] = (),
    ) -> ScheduleVersion:
        version = ScheduleVersion(
            id=self._next_id,
            round_id=round_id,
            snapshot=deepcopy(snapshot),
            algorithm_parameters=deepcopy(algorithm_parameters or {}),
            random_seed=random_seed,
            solver_status=solver_status,
            objective=objective,
            soft_scores=deepcopy(soft_scores or {}),
            unscheduled=deepcopy(unscheduled),
        )
        self._versions[version.id] = version
        self._next_id += 1
        return deepcopy(version)

    def activate(self, version_id: int) -> ScheduleVersion:
        version = self.get(version_id)
        for other_id, other in list(self._versions.items()):
            if other.round_id == version.round_id and other.status in {"DRAFT", "ACTIVE"}:
                self._versions[other_id] = replace(other, status="DISCARDED")
        version = replace(version, status="ACTIVE")
        self._versions[version.id] = version
        return deepcopy(version)

    def get(self, version_id: int) -> ScheduleVersion:
        if version_id not in self._versions:
            raise DomainError("VERSION_NOT_FOUND", "ScheduleVersion does not exist.")
        return deepcopy(self._versions[version_id])

    def list(self, *, round_id: int) -> list[ScheduleVersion]:
        return [deepcopy(version) for version in self._versions.values() if version.round_id == round_id]

    def active(self, *, round_id: int) -> ScheduleVersion | None:
        active = next(
            (version for version in self._versions.values() if version.round_id == round_id and version.status == "ACTIVE"),
            None,
        )
        return deepcopy(active) if active is not None else None

    def compare(self, first_id: int, second_id: int) -> dict[str, Any]:
        first = self.get(first_id)
        second = self.get(second_id)
        return {
            "first_version_id": first.id,
            "second_version_id": second.id,
            "scheduled_groups_delta": second.objective - first.objective,
            "objective_delta": second.objective - first.objective,
            "soft_scores_delta": {
                rule: second.soft_scores.get(rule, 0) - first.soft_scores.get(rule, 0)
                for rule in sorted(set(first.soft_scores) | set(second.soft_scores))
            },
            "unscheduled_count_delta": len(second.unscheduled) - len(first.unscheduled),
        }
