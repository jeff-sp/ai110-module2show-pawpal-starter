# testing ground to verify logic works in the terminal
from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # Create an owner with a limited daily time budget.
    owner = Owner(name="Sam", available_time_minutes=60)

    # Create at least two pets.
    rex = Pet(name="Rex", species="dog")
    milo = Pet(name="Milo", species="cat")
    owner.add_pet(rex)
    owner.add_pet(milo)

    # Add at least three tasks with different durations.
    rex.add_task(Task("Morning walk", duration_minutes=30, priority=5))
    rex.add_task(Task("Grooming", duration_minutes=40, priority=1))
    milo.add_task(Task("Feed", duration_minutes=10, priority=5))
    milo.add_task(Task("Play / enrichment", duration_minutes=15, priority=3))

    # Ask the scheduler to build today's plan.
    scheduler = Scheduler()
    plan = scheduler.generate_schedule(owner)

    # Print "Today's Schedule".
    print("=" * 40)
    print(f"Today's Schedule for {owner.name}")
    print(f"(available time: {owner.available_time_minutes} min)")
    print("=" * 40)

    if plan.scheduled:
        for task in plan.scheduled:
            print(f"  [ ] {task.description} — {task.pet.name} ({task.duration_minutes} min)")
    else:
        print("  Nothing scheduled today.")

    if plan.skipped:
        print("\nCouldn't fit today:")
        for task in plan.skipped:
            print(f"  - {task.description} — {task.pet.name} ({task.duration_minutes} min)")

    print("\nWhy this plan:")
    print(plan.rationale)


if __name__ == "__main__":
    main()
