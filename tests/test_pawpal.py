"""Basic tests for PawPal+ core classes."""

from datetime import date

from pawpal_system import Pet, Recurrence, Scheduler, Task, TaskType, Time


def test_mark_completed_changes_status():
    """Calling mark_completed() should flip the task's completion status."""
    task = Task("Feeding", TaskType.FEEDING, duration_minutes=10, priority=1)

    # A new task starts out not completed.
    assert task.completed is False

    task.mark_completed()

    # After marking it, the status should be True.
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet should increase that pet's task count by one."""
    pet = Pet(name="Biscuit", species="Dog", breed="Golden Retriever", age=3)

    # A new pet starts with no tasks.
    assert len(pet.tasks) == 0

    pet.add_task(Task("Morning walk", TaskType.WALK, duration_minutes=30, priority=2))

    # The count should now be one.
    assert len(pet.tasks) == 1


def test_sort_by_time_returns_chronological_order():
    """Sorting Correctness: tasks come back ordered by scheduled start time."""
    # Build three tasks and deliberately give them start times out of order,
    # so a correct sort has real work to do (not already sorted by accident).
    noon = Task("Lunch feeding", TaskType.FEEDING, duration_minutes=15, priority=1)
    morning = Task("Morning walk", TaskType.WALK, duration_minutes=30, priority=2)
    evening = Task("Evening meds", TaskType.MEDS, duration_minutes=10, priority=1)
    noon.schedule(Time(12, 0))
    morning.schedule(Time(8, 30))
    evening.schedule(Time(18, 0))

    # Feed them in scrambled order to prove the sort reorders them.
    ordered = Scheduler().sort_by_time([noon, evening, morning])

    # Expect earliest -> latest: 08:30, 12:00, 18:00.
    assert [t.scheduled_start.format() for t in ordered] == ["08:30", "12:00", "18:00"]


def test_completing_daily_task_creates_next_days_task():
    """Recurrence Logic: completing a DAILY task spawns tomorrow's copy."""
    pet = Pet(name="Biscuit", species="Dog", breed="Golden Retriever", age=3)
    task = Task(
        "Breakfast",
        TaskType.FEEDING,
        duration_minutes=10,
        priority=1,
        recurrence=Recurrence.DAILY,
        due_date=date(2026, 7, 5),
    )
    pet.add_task(task)

    # Marking complete returns the newly created next occurrence.
    next_task = pet.mark_task_complete(task)

    # The original is now done.
    assert task.completed is True
    # A brand-new task exists for the following day, fresh and unscheduled.
    assert next_task is not None
    assert next_task.due_date == date(2026, 7, 6)
    assert next_task.completed is False
    assert next_task.scheduled_start is None
    # It was actually attached to the pet (original + new occurrence).
    assert next_task in pet.tasks
    assert len(pet.tasks) == 2


def test_detect_conflicts_flags_tasks_at_same_time():
    """Conflict Detection: overlapping (duplicate) times produce a warning."""
    walk = Task("Walk", TaskType.WALK, duration_minutes=30, priority=1)
    meds = Task("Meds", TaskType.MEDS, duration_minutes=30, priority=1)
    # Both scheduled at exactly 09:00 -> their windows overlap.
    walk.schedule(Time(9, 0))
    meds.schedule(Time(9, 0))

    warnings = Scheduler().detect_conflicts([walk, meds])

    # Exactly one clash, naming both tasks involved.
    assert len(warnings) == 1
    assert "Walk" in warnings[0]
    assert "Meds" in warnings[0]


def test_detect_conflicts_ignores_back_to_back_tasks():
    """Conflict Detection: a task ending as the next begins is NOT a conflict."""
    first = Task("Walk", TaskType.WALK, duration_minutes=60, priority=1)
    second = Task("Meds", TaskType.MEDS, duration_minutes=30, priority=1)
    # 08:00-09:00 then 09:00-09:30: they touch but do not overlap.
    first.schedule(Time(8, 0))
    second.schedule(Time(9, 0))

    assert Scheduler().detect_conflicts([first, second]) == []
