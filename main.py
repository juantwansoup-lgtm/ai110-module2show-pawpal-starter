"""PawPal+ demo script.

Builds a small scenario -- one owner, two pets, several tasks -- and prints
today's generated schedule to the terminal.
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

    # 3. Add at least three tasks with different durations/priorities.
    biscuit.add_task(Task("Morning walk", TaskType.WALK, 30, priority=2,
                          recurrence=Recurrence.DAILY))
    biscuit.add_task(Task("Feeding", TaskType.FEEDING, 10, priority=1,
                          recurrence=Recurrence.DAILY))
    mochi.add_task(Task("Medication", TaskType.MEDS, 5, priority=1,
                        recurrence=Recurrence.DAILY))
    mochi.add_task(Task("Playtime", TaskType.ENRICHMENT, 20, priority=3,
                        recurrence=Recurrence.DAILY))

    # 4. Let the Scheduler organize the tasks, then print today's schedule.
    scheduler = Scheduler()
    scheduler.build_plan(owner)

    print("=" * 40)
    print(f"Today's Schedule for {owner.name}")
    print(f"Pets: {', '.join(pet.name for pet in owner.list_pets())}")
    print("=" * 40)
    print(scheduler.explain_plan())
    print("=" * 40)


if __name__ == "__main__":
    main()
