"""PawPal+ demo script.

Builds a small scenario -- one owner, two pets, several tasks -- and prints
today's generated schedule to the terminal, then demonstrates the new
sort-by-time and filter-by-pet/status logic.
"""

from pawpal_system import Owner, Pet, Task, Scheduler, Time, TaskType, Recurrence


def main() -> None:
    # 1. Create an owner and set how much time they have for pet care today.
    owner = Owner("Sam")
    owner.set_availability(Time(8, 0), Time(12, 0))  # 4-hour care window

    # 2. Create at least two pets and register them under the owner.
    biscuit = Pet(name="Biscuit", species="Dog", breed="Golden Retriever", age=3)
    mochi = Pet(name="Mochi", species="Cat", breed="Tabby", age=5)
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # 3. Add tasks OUT OF ORDER on purpose. Some have fixed appointment times
    #    that are added in a jumbled sequence (10:00 before 08:30 before
    #    09:15) so we can prove sort_by_time() actually reorders them.
    mochi.add_task(Task("Late playtime", TaskType.ENRICHMENT, 20, priority=3,
                        fixed_start=Time(10, 0)))
    biscuit.add_task(Task("Morning walk", TaskType.WALK, 30, priority=2,
                          fixed_start=Time(8, 30), recurrence=Recurrence.DAILY))
    mochi.add_task(Task("Medication", TaskType.MEDS, 5, priority=1,
                        fixed_start=Time(9, 15), recurrence=Recurrence.DAILY))
    # A couple of flexible tasks (no fixed time) that flow into the gaps.
    biscuit.add_task(Task("Feeding", TaskType.FEEDING, 10, priority=1,
                          recurrence=Recurrence.DAILY))
    mochi.add_task(Task("Grooming", TaskType.GROOMING, 15, priority=2))

    # Mark one task completed so the status filter has something to hide.
    mochi.tasks[0].mark_completed(True)  # "Late playtime" is done

    # 4. Let the Scheduler organize the tasks, then print today's schedule.
    scheduler = Scheduler()
    scheduler.build_plan(owner)

    print("=" * 44)
    print(f"Today's Schedule for {owner.name}")
    print(f"Pets: {', '.join(pet.name for pet in owner.list_pets())}")
    print("=" * 44)
    print(scheduler.explain_plan())

    # 5. SORTING: prove sort_by_time() orders the planned tasks by their
    #    "HH:MM" start time regardless of the order they were added.
    print("\n" + "=" * 44)
    print("Planned tasks sorted by time (sort_by_time)")
    print("=" * 44)
    for task in scheduler.sort_by_time():
        start = task.scheduled_start.format() if task.scheduled_start else "--:--"
        print(f"  {start}  {task.name}")

    # 6. FILTERING: by pet name, and by completion status.
    print("\n" + "=" * 44)
    print("Filtering (filter_tasks)")
    print("=" * 44)

    print("Mochi's tasks:")
    for task in owner.filter_tasks(pet_name="Mochi"):
        print(f"  - {task.name}")

    print("Pending (not completed) tasks:")
    for task in owner.filter_tasks(completed=False):
        print(f"  - {task.name}")

    print("Completed tasks:")
    for task in owner.filter_tasks(completed=True):
        print(f"  - {task.name}")

    print("Mochi's pending tasks (both filters at once):")
    for task in owner.filter_tasks(pet_name="Mochi", completed=False):
        print(f"  - {task.name}")

    # 7. RECURRENCE: completing a daily/weekly task auto-spawns its next
    #    occurrence with the due date advanced via timedelta.
    print("\n" + "=" * 44)
    print("Recurrence (mark_task_complete)")
    print("=" * 44)

    from datetime import date

    today = date.today()
    # "Feeding" is DAILY; give it a due date of today so we can see +1 day.
    feeding = next(t for t in biscuit.tasks if t.name == "Feeding")
    feeding.due_date = today
    # Add a WEEKLY task to show the +7 day step as well.
    biscuit.add_task(Task("Bath", TaskType.GROOMING, 30, priority=2,
                          recurrence=Recurrence.WEEKLY, due_date=today))

    print(f"Today is {today}")
    print(f"Biscuit's tasks before completing: {[t.name for t in biscuit.tasks]}")

    new_feeding = biscuit.mark_task_complete(feeding)
    print(f"\nCompleted daily 'Feeding' (due {feeding.due_date}, "
          f"completed={feeding.completed})")
    print(f"  -> auto-created next: '{new_feeding.name}' "
          f"due {new_feeding.due_date}, completed={new_feeding.completed}")

    bath = next(t for t in biscuit.tasks if t.name == "Bath")
    new_bath = biscuit.mark_task_complete(bath)
    print(f"Completed weekly 'Bath' (due {bath.due_date})")
    print(f"  -> auto-created next: '{new_bath.name}' due {new_bath.due_date}")

    # A one-off task should NOT spawn a repeat.
    grooming = next(t for t in mochi.tasks if t.name == "Grooming")
    result = mochi.mark_task_complete(grooming)
    print(f"Completed one-off 'Grooming' -> next occurrence: {result}")

    print(f"\nBiscuit's tasks after completing:  {[t.name for t in biscuit.tasks]}")

    # 8. CONFLICT DETECTION: two tasks scheduled at the SAME TIME, one per pet.
    #    The planner normally avoids overlaps, so we schedule these by hand to
    #    prove the detector catches the clash and warns instead of crashing.
    print("\n" + "=" * 44)
    print("Conflict detection (detect_conflicts)")
    print("=" * 44)

    # Biscuit's vet call and Mochi's grooming both land at 09:00 -> conflict.
    vet_call = Task("Biscuit: Vet call", TaskType.MEDS, 30, priority=1)
    groom_appt = Task("Mochi: Grooming appt", TaskType.GROOMING, 30, priority=2)
    evening_walk = Task("Biscuit: Evening walk", TaskType.WALK, 20, priority=2)
    biscuit.add_task(vet_call)
    mochi.add_task(groom_appt)
    biscuit.add_task(evening_walk)

    vet_call.schedule(Time(9, 0))
    groom_appt.schedule(Time(9, 0))     # same 09:00 start -> conflicts (different pets!)
    evening_walk.schedule(Time(18, 0))  # clear, no overlap

    print("Scheduled: Vet call 09:00, Grooming appt 09:00, Evening walk 18:00")
    warnings = scheduler.detect_conflicts([vet_call, groom_appt, evening_walk])
    if warnings:
        print(f"Found {len(warnings)} conflict(s):")
        for msg in warnings:
            print(f"  {msg}")
    else:
        print("No scheduling conflicts found.")

    print("=" * 44)


if __name__ == "__main__":
    main()
