# logic layer where all backend classes live
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from itertools import combinations
from typing import Optional


@dataclass
class Task:
    """A single pet-care activity (walk, feeding, meds, etc.)."""
    description: str
    duration_minutes: int
    priority: int              # higher number = more important
    time: str = "09:00"        # preferred start time, "HH:MM" (24-hour)
    frequency: str = "daily"   # e.g. "daily", "weekly", "twice daily"
    due: date = field(default_factory=date.today)  # day this task is due
    completed: bool = False
    pet: Optional["Pet"] = None  # set by Pet.add_task; lets the plan name the pet

    def next_occurrence(self) -> Optional["Task"]:
        """Build a fresh, uncompleted copy of this task for its next occurrence.

        Returns None for non-recurring tasks (anything other than "daily"/"weekly").
        """
        deltas = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}
        if self.frequency not in deltas:
            return None
        return Task(
            description=self.description,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            time=self.time,
            frequency=self.frequency,
            # Advance from this task's own due date so the cadence stays
            # anchored to the schedule, even if completed late.
            due=self.due + deltas[self.frequency],
        )

    def mark_task_complete(self) -> None:
        """Mark this task complete and, if recurring, queue up the next occurrence."""
        self.completed = True
        upcoming = self.next_occurrence()
        if upcoming is not None and self.pet is not None:
            self.pet.add_task(upcoming)


@dataclass
class Pet:
    """Stores pet details and the tasks that belong to it."""
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and link it back to the pet."""
        task.pet = self
        self.tasks.append(task)


@dataclass
class Owner:
    """Manages multiple pets and provides access to all their tasks."""
    name: str
    available_time_minutes: int
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner, ignoring duplicates."""
        if pet not in self.pets:
            self.pets.append(pet)

    def all_tasks(self) -> list[Task]:
        """Flatten every pet's task list into one collection."""
        return [task for pet in self.pets for task in pet.tasks]


@dataclass
class Plan:
    scheduled: list[Task]
    skipped: list[Task] = field(default_factory=list)
    rationale: str = ""


class Scheduler:
    """The brain: retrieves, organizes, and manages tasks across pets."""

    @staticmethod
    def _start_minutes(task: Task) -> int:
        """Convert a task's 'HH:MM' start time into minutes past midnight."""
        hours, minutes = map(int, task.time.split(":"))
        return hours * 60 + minutes

    @classmethod
    def _has_valid_time(cls, task: Task) -> bool:
        """True if the task's time parses as 'HH:MM'; never raises."""
        try:
            cls._start_minutes(task)
            return True
        except (ValueError, AttributeError):
            return False

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by their preferred start time (earliest first)."""
        return sorted(tasks, key=self._start_minutes)

    def _overlaps(self, a: Task, b: Task) -> bool:
        """True if two tasks occupy overlapping time slots on the same day.

        Each task occupies the half-open interval [start, start + duration);
        they overlap iff each starts before the other ends. Identical start
        times count as overlapping.
        """
        a_start, b_start = self._start_minutes(a), self._start_minutes(b)
        return (a.due == b.due
                and a_start < b_start + b.duration_minutes
                and b_start < a_start + a.duration_minutes)

    def detect_conflicts(self, tasks: list[Task]) -> list[tuple[Task, Task]]:
        """Find pairs of tasks whose time slots overlap, earliest first."""
        ordered = self.sort_by_time(tasks)
        return [(a, b) for a, b in combinations(ordered, 2) if self._overlaps(a, b)]

    def check_conflicts(self, tasks: list[Task]) -> str:
        """Lightweight conflict check that returns a warning string, never raises.

        Returns "" when nothing overlaps. Tasks with an unparseable time are
        skipped (and noted) instead of crashing the caller, so this is safe to
        call on user-entered data.
        """
        skipped = [t for t in tasks if not self._has_valid_time(t)]
        valid = [t for t in tasks if self._has_valid_time(t)]

        conflicts = self.detect_conflicts(valid)

        lines: list[str] = []
        if conflicts:
            lines.append("⚠ Scheduling conflicts (overlapping times):")
            for a, b in conflicts:
                a_who = a.pet.name if a.pet else "pet"
                b_who = b.pet.name if b.pet else "pet"
                lines.append(
                    f"  {a.time} {a.description} ({a_who}) overlaps "
                    f"{b.time} {b.description} ({b_who})"
                )
        if skipped:
            names = ", ".join(f"'{t.description}'" for t in skipped)
            lines.append(f"⚠ Skipped conflict check for tasks with a bad time: {names}")

        return "\n".join(lines)

    def filter_tasks(
        self,
        tasks: list[Task],
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> list[Task]:
        """Return tasks matching the given completion status and/or pet name.

        Both filters are optional; when omitted that dimension is ignored.
        Pet-name matching is case-insensitive.
        """
        result = tasks
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if pet_name is not None:
            target = pet_name.lower()
            result = [t for t in result if t.pet and t.pet.name.lower() == target]
        return result

    def generate_schedule(self, owner: Owner) -> Plan:
        """Build a daily plan that fits the owner's tasks into their available time."""
        # Retrieve every task from all of the owner's pets.
        tasks = [t for t in owner.all_tasks() if not t.completed]

        # Organize: highest priority first, then shortest task to fit more in.
        tasks.sort(key=lambda t: (-t.priority, t.duration_minutes))

        scheduled: list[Task] = []
        skipped: list[Task] = []
        remaining = owner.available_time_minutes

        # Greedily fill the available time by priority.
        for task in tasks:
            if task.duration_minutes <= remaining:
                scheduled.append(task)
                remaining -= task.duration_minutes
            else:
                skipped.append(task)

        # Present the day in chronological order, even though we selected by priority.
        scheduled = self.sort_by_time(scheduled)

        plan = Plan(scheduled=scheduled, skipped=skipped)
        plan.rationale = self.explain_plan(plan)
        return plan

    def explain_plan(self, plan: Plan) -> str:
        """Return a human-readable explanation of what was scheduled and skipped."""
        lines = []
        for task in plan.scheduled:
            who = task.pet.name if task.pet else "pet"
            lines.append(
                f"Scheduled '{task.description}' for {who} "
                f"({task.duration_minutes} min, priority {task.priority})."
            )
        for task in plan.skipped:
            who = task.pet.name if task.pet else "pet"
            lines.append(
                f"Skipped '{task.description}' for {who} "
                f"— not enough time remaining."
            )
        if not lines:
            return "No tasks to schedule."
        return "\n".join(lines)
