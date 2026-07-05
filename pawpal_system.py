"""PawPal+ core system.

Implements the four core classes from the UML (Owner, Pet, Task, Scheduler)
plus the Time value object and the TaskType / Recurrence enums.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

MINUTES_PER_DAY = 24 * 60


class TaskType(Enum):
    """The kind of care a task represents."""

    WALK = "walk"
    FEEDING = "feeding"
    MEDS = "meds"
    ENRICHMENT = "enrichment"
    GROOMING = "grooming"


class Recurrence(Enum):
    """How often a task repeats (README: daily vs. weekly)."""

    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class Time:
    """A time-of-day value object (24-hour clock)."""

    hour: int
    minute: int

    def to_minutes(self) -> int:
        """Return this time as minutes since midnight."""
        return self.hour * 60 + self.minute

    def add_minutes(self, minutes: int) -> "Time":
        """Return a new Time offset by the given minutes (wraps within a day)."""
        total = (self.to_minutes() + minutes) % MINUTES_PER_DAY
        return Time(total // 60, total % 60)

    def is_before(self, other: "Time") -> bool:
        """Return True if this time is earlier than other."""
        return self.to_minutes() < other.to_minutes()

    def overlaps(self, start: "Time", duration_minutes: int) -> bool:
        """Return True if this time falls inside [start, start + duration)."""
        start_min = start.to_minutes()
        return start_min <= self.to_minutes() < start_min + duration_minutes

    def format(self) -> str:
        """Return a human-readable string like '08:00'."""
        return f"{self.hour:02d}:{self.minute:02d}"


@dataclass
class Task:
    """A single unit of pet care.

    priority: lower number = higher priority (1 = most important).
    """

    name: str
    type: TaskType
    duration_minutes: int
    priority: int
    recurrence: Recurrence = Recurrence.ONCE
    scheduled_start: Optional[Time] = None
    completed: bool = False

    def schedule(self, start: Time) -> None:
        """Assign a start time to this task (called during planning)."""
        self.scheduled_start = start

    def get_end_time(self) -> Optional[Time]:
        """Return the time this task would finish, or None if unscheduled."""
        if self.scheduled_start is None:
            return None
        return self.scheduled_start.add_minutes(self.duration_minutes)

    def set_priority(self, priority: int) -> None:
        """Update the task's priority."""
        self.priority = priority

    def mark_completed(self, done: bool = True) -> None:
        """Set the task's completion status."""
        self.completed = done

    def fits_within(self, available_minutes: int) -> bool:
        """Return True if the task fits in the given available minutes."""
        return self.duration_minutes <= available_minutes

    def conflicts_with(self, other: "Task") -> bool:
        """Return True if this task's window overlaps another scheduled task."""
        if self.scheduled_start is None or other.scheduled_start is None:
            return False
        start_a = self.scheduled_start.to_minutes()
        end_a = start_a + self.duration_minutes
        start_b = other.scheduled_start.to_minutes()
        end_b = start_b + other.duration_minutes
        # Two windows overlap when each starts before the other ends.
        return start_a < end_b and start_b < end_a


@dataclass
class Pet:
    """An owner's animal and the tasks that belong to it."""

    name: str
    species: str
    breed: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Detach a care task from this pet."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_tasks_by_priority(self) -> List[Task]:
        """Return this pet's tasks sorted by priority (1 = most important first)."""
        return sorted(self.tasks, key=lambda t: t.priority)


@dataclass
class Owner:
    """The pet owner, their pets, and their available care window.

    The availability window is the single source of truth for capacity;
    total_available_minutes() is derived from it (no duplicated counter).
    """

    name: str
    pets: List[Pet] = field(default_factory=list)
    available_start: Optional[Time] = None
    available_end: Optional[Time] = None

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def set_availability(self, start: Time, end: Time) -> None:
        """Set the owner's available care window."""
        self.available_start = start
        self.available_end = end

    def total_available_minutes(self) -> int:
        """Return total care capacity, derived from the availability window."""
        if self.available_start is None or self.available_end is None:
            return 0
        return self.available_end.to_minutes() - self.available_start.to_minutes()

    def all_tasks(self) -> List[Task]:
        """Return every task across all of this owner's pets (flattened)."""
        return [task for pet in self.pets for task in pet.tasks]

    def list_pets(self) -> List[Pet]:
        """Return all pets belonging to this owner."""
        return self.pets


class Scheduler:
    """Builds a daily plan from an owner's availability and pets' tasks.

    Owns only the *remaining* time during a planning pass; total capacity
    lives on Owner, so the two never drift out of sync.
    """

    def __init__(self) -> None:
        """Create an empty scheduler with no remaining time or planned tasks."""
        self.remaining_minutes: int = 0
        self.planned_tasks: List[Task] = []

    def build_plan(self, owner: Owner) -> List[Task]:
        """Place the owner's incomplete tasks, in priority order, into the day's plan."""
        self.remaining_minutes = owner.total_available_minutes()
        self.planned_tasks = []

        # Retrieve every task across all pets, then order by priority.
        tasks = sorted(owner.all_tasks(), key=lambda t: t.priority)
        current = owner.available_start

        for task in tasks:
            if task.completed:
                continue
            if not self.can_fit(task):
                continue

            if current is not None:
                task.schedule(current)
                if self.has_conflict(task):
                    task.scheduled_start = None
                    continue

            self.planned_tasks.append(task)
            self.remaining_minutes -= task.duration_minutes
            if current is not None:
                current = current.add_minutes(task.duration_minutes)

        return self.planned_tasks

    def can_fit(self, task: Task) -> bool:
        """Return True if the task still fits in the remaining time."""
        return task.fits_within(self.remaining_minutes)

    def has_conflict(self, task: Task) -> bool:
        """Return True if the task overlaps an already-planned task."""
        return any(task.conflicts_with(planned) for planned in self.planned_tasks)

    def explain_plan(self) -> str:
        """Return a human-readable explanation of the chosen plan."""
        if not self.planned_tasks:
            return "No tasks could be scheduled in the available time."

        lines = ["Daily plan:"]
        for task in self.planned_tasks:
            start = task.scheduled_start.format() if task.scheduled_start else "--:--"
            lines.append(
                f"  {start} - {task.name} ({task.duration_minutes} min) "
                f"[priority: {task.priority}]"
            )
        lines.append(f"Remaining free time: {self.remaining_minutes} min")
        return "\n".join(lines)
