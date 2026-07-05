"""Basic tests for PawPal+ core classes."""

from pawpal_system import Pet, Task, TaskType


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
