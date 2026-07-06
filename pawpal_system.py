"""PawPal+ core system.

Implements the four core classes from the UML (Owner, Pet, Task, Scheduler)
plus the Time value object and the TaskType / Recurrence enums.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
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

    @classmethod
    def from_minutes(cls, total: int) -> "Time":
        """Build a Time from minutes since midnight."""
        return cls(total // 60, total % 60)

    def add_minutes(self, minutes: int) -> "Time":
        """Return a new Time offset by the given minutes (wraps within a day)."""
        return Time.from_minutes((self.to_minutes() + minutes) % MINUTES_PER_DAY)

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
    # A fixed appointment time (e.g. "meds at 09:00"). Flexible tasks leave
    # this as None and get placed into whatever free gaps remain.
    fixed_start: Optional[Time] = None
    scheduled_start: Optional[Time] = None
    completed: bool = False
    # The calendar day this task is due. Recurring tasks advance this when
    # they spawn their next occurrence.
    due_date: Optional[date] = None

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

    def next_occurrence(self) -> Optional["Task"]:
        """Return a fresh, uncompleted copy of this task due on its next date,
        or None if the task does not recur.

        The next due date is computed with datetime.timedelta so calendar
        boundaries (month/year rollovers) are handled correctly:
          * DAILY  -> due_date + timedelta(days=1)
          * WEEKLY -> due_date + timedelta(weeks=1)
        If this task has no due_date, today is used as the base.
        """
        if self.recurrence == Recurrence.DAILY:
            step = timedelta(days=1)
        elif self.recurrence == Recurrence.WEEKLY:
            step = timedelta(weeks=1)
        else:  # Recurrence.ONCE -- nothing to repeat.
            return None

        base = self.due_date if self.due_date is not None else date.today()
        return Task(
            name=self.name,
            type=self.type,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            recurrence=self.recurrence,
            fixed_start=self.fixed_start,
            due_date=base + step,
            scheduled_start=None,  # re-planned fresh for the new day
            completed=False,
        )

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

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Mark one of this pet's tasks complete.

        If the task is recurring (daily/weekly), automatically create the next
        occurrence, attach it to this pet, and return it. Returns None for
        one-off tasks (nothing new is created).
        """
        task.mark_completed(True)
        next_task = task.next_occurrence()
        if next_task is not None:
            self.add_task(next_task)
        return next_task


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

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[Task]:
        """Return tasks filtered by pet name and/or completion status.

        Each filter is optional and applied only when provided:
          * pet_name=None    -> tasks from every pet
          * completed=None    -> both completed and pending tasks
        Passing both narrows on both at once (e.g. Mochi's pending tasks).
        """
        results: List[Task] = []
        for pet in self.pets:
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.tasks:
                if completed is not None and task.completed != completed:
                    continue
                results.append(task)
        return results


class Scheduler:
    """Builds a daily plan from an owner's availability and pets' tasks.

    Owns only the *remaining* time during a planning pass; total capacity
    lives on Owner, so the two never drift out of sync.
    """

    def __init__(self) -> None:
        """Create an empty scheduler with no remaining time or planned tasks."""
        self.remaining_minutes: int = 0
        self.planned_tasks: List[Task] = []
        # (task, reason) pairs for tasks that could not be placed, so the
        # owner is told *why* the meds/walk didn't make it into the day.
        self.skipped_tasks: List[tuple] = []

    def build_plan(self, owner: Owner) -> List[Task]:
        """Build the day's plan: anchor fixed-time tasks, then flow flexible
        tasks into the remaining gaps in priority order."""
        self.planned_tasks = []
        self.skipped_tasks = []
        self.remaining_minutes = 0

        if owner.available_start is None or owner.available_end is None:
            return self.planned_tasks

        window_start = owner.available_start.to_minutes()
        window_end = owner.available_end.to_minutes()

        tasks = [t for t in owner.all_tasks() if not t.completed]
        fixed = [t for t in tasks if t.fixed_start is not None]
        flexible = [t for t in tasks if t.fixed_start is None]

        # --- Anchor fixed-time tasks first ---------------------------------
        # Earlier commitments claim their slot first; anything that lands
        # outside the window or overlaps an earlier fixed task is skipped.
        fixed.sort(key=lambda t: t.fixed_start.to_minutes())
        occupied: List[tuple] = []  # (start_min, end_min) already committed
        for task in fixed:
            start = task.fixed_start.to_minutes()
            end = start + task.duration_minutes
            if start < window_start or end > window_end:
                self.skipped_tasks.append((task, "outside availability window"))
                continue
            if any(start < o_end and o_start < end for o_start, o_end in occupied):
                self.skipped_tasks.append((task, "conflicts with a fixed task"))
                continue
            task.schedule(Time.from_minutes(start))
            self.planned_tasks.append(task)
            occupied.append((start, end))

        # --- Flow flexible tasks into the free gaps ------------------------
        # Highest priority first; ties broken by shortest duration so more
        # small tasks pack into the day.
        free = self._free_intervals(window_start, window_end, occupied)
        flexible.sort(key=lambda t: (t.priority, t.duration_minutes))
        for task in flexible:
            placed = False
            for i, (g_start, g_end) in enumerate(free):
                if task.duration_minutes <= g_end - g_start:
                    task.schedule(Time.from_minutes(g_start))
                    self.planned_tasks.append(task)
                    free[i] = (g_start + task.duration_minutes, g_end)
                    placed = True
                    break
            if not placed:
                self.skipped_tasks.append((task, "no free time slot"))

        self.remaining_minutes = sum(g_end - g_start for g_start, g_end in free)
        # Present the plan as a timeline, earliest start first. Every planned
        # task has a start time by now, so the key is unconditional.
        self.planned_tasks.sort(key=lambda t: t.scheduled_start.to_minutes())
        return self.planned_tasks

    @staticmethod
    def _free_intervals(
        window_start: int, window_end: int, occupied: List[tuple]
    ) -> List[tuple]:
        """Return the free (start, end) gaps inside the window, given the
        occupied fixed-task intervals."""
        free: List[tuple] = []
        cursor = window_start
        for o_start, o_end in sorted(occupied):
            if o_start > cursor:
                free.append((cursor, o_start))
            cursor = max(cursor, o_end)
        if cursor < window_end:
            free.append((cursor, window_end))
        return free

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return tasks ordered by their scheduled start time.

        Each start time is formatted as a zero-padded "HH:MM" string (e.g.
        "08:30", "10:00"). Because the hours and minutes are zero-padded and
        fixed-width, these strings sort correctly with a plain lexicographic
        comparison -- "08:30" < "10:00" as text -- so the sort key is simply
        a lambda that reads each task's formatted start string. Tasks with no
        start time yet sort to the end.

        Defaults to sorting this scheduler's planned tasks, but any list of
        tasks can be passed in.
        """
        tasks = self.planned_tasks if tasks is None else tasks
        return sorted(
            tasks,
            key=lambda t: t.scheduled_start.format() if t.scheduled_start else "99:99",
        )

    def detect_conflicts(self, tasks: Optional[List[Task]] = None) -> List[str]:
        """Scan scheduled tasks for overlapping time windows.

        Lightweight and non-fatal: this never raises. It compares each pair of
        tasks that have a start time (using Task.conflicts_with) and returns a
        list of human-readable warning messages -- empty if nothing overlaps.
        Because it works on the flattened task list, it catches clashes whether
        the two tasks belong to the same pet or to different pets.

        Defaults to this scheduler's planned tasks, but any list can be passed.
        """
        tasks = self.planned_tasks if tasks is None else tasks
        scheduled = [t for t in tasks if t.scheduled_start is not None]
        warnings: List[str] = []
        for i in range(len(scheduled)):
            for j in range(i + 1, len(scheduled)):
                a, b = scheduled[i], scheduled[j]
                if a.conflicts_with(b):
                    warnings.append(
                        f"WARNING: '{a.name}' "
                        f"({a.scheduled_start.format()}-{a.get_end_time().format()}) "
                        f"overlaps '{b.name}' "
                        f"({b.scheduled_start.format()}-{b.get_end_time().format()})."
                    )
        return warnings

    def explain_plan(self) -> str:
        """Return a human-readable explanation of the chosen plan, including
        anything that could not be scheduled and why."""
        lines: List[str] = []
        if self.planned_tasks:
            lines.append("Daily plan:")
            for task in self.planned_tasks:
                start = task.scheduled_start.format() if task.scheduled_start else "--:--"
                marker = " (fixed)" if task.fixed_start is not None else ""
                lines.append(
                    f"  {start} - {task.name} ({task.duration_minutes} min) "
                    f"[priority: {task.priority}]{marker}"
                )
            lines.append(f"Remaining free time: {self.remaining_minutes} min")
        else:
            lines.append("No tasks could be scheduled in the available time.")

        if self.skipped_tasks:
            lines.append("")
            lines.append("Not scheduled:")
            for task, reason in self.skipped_tasks:
                lines.append(
                    f"  {task.name} ({task.duration_minutes} min) - {reason}"
                )
        return "\n".join(lines)
