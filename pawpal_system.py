# logic layer where all backend classes live
from dataclasses import dataclass, field


@dataclass
class Pet:
    name: str
    species: str


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: int
    pet: Pet


@dataclass
class Owner:
    name: str
    available_time_minutes: int
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        raise NotImplementedError


class Scheduler:
    def generate_schedule(self, owner: Owner, pet: Pet, tasks: list[Task]) -> list[Task]:
        raise NotImplementedError

    def explain_plan(self, plan: list[Task]) -> str:
        raise NotImplementedError
