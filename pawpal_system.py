# logic layer where all backend classes live
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    """A single pet-care activity (walk, feeding, meds, etc.)."""
    description: str
    duration_minutes: int
    priority: int              # higher number = more important
    frequency: str = "daily"   # e.g. "daily", "weekly", "twice daily"
    completed: bool = False
    pet: Optional["Pet"] = None  # set by Pet.add_task; lets the plan name the pet

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


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
