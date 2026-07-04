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

    # Add tasks intentionally OUT OF TIME ORDER so sorting has real work to do.
    milo.add_task(Task("Play / enrichment", duration_minutes=15, priority=3, time="17:00"))
    rex.add_task(Task("Grooming", duration_minutes=40, priority=1, time="14:00"))
    milo.add_task(Task("Feed", duration_minutes=10, priority=5, time="08:00"))
    rex.add_task(Task("Morning walk", duration_minutes=30, priority=5, time="07:30"))
    # Two tasks at the SAME time (07:30) to demonstrate conflict detection.
    milo.add_task(Task("Medicine", duration_minutes=5, priority=5, time="07:30"))

    # Mark a task done to show filtering by completion status.
    milo.tasks[1].mark_task_complete()  # "Feed"

    scheduler = Scheduler()

    # --- Demonstrate sort_by_time on the raw, unsorted task list. ---
    print("=" * 40)
    print("Insertion order (as added):")
    print("=" * 40)
    for task in owner.all_tasks():
        print(f"  {task.time} {task.description} — {task.pet.name}")

    print("\n" + "=" * 40)
    print("After sort_by_time (chronological):")
    print("=" * 40)
    for task in scheduler.sort_by_time(owner.all_tasks()):
        print(f"  {task.time} {task.description} — {task.pet.name}")

    # --- Demonstrate filter_tasks. ---
    print("\n" + "=" * 40)
    print("filter_tasks demos:")
    print("=" * 40)
    rex_tasks = scheduler.filter_tasks(owner.all_tasks(), pet_name="rex")
    print(f"  Rex's tasks: {[t.description for t in rex_tasks]}")
    completed = scheduler.filter_tasks(owner.all_tasks(), completed=True)
    print(f"  Completed:   {[t.description for t in completed]}")
    incomplete = scheduler.filter_tasks(owner.all_tasks(), completed=False)
    print(f"  Incomplete:  {[t.description for t in incomplete]}")

    # --- Build today's plan. ---
    plan = scheduler.generate_schedule(owner)

    print("\n" + "=" * 40)
    print(f"Today's Schedule for {owner.name}")
    print(f"(available time: {owner.available_time_minutes} min)")
    print("=" * 40)

    if plan.scheduled:
        for task in plan.scheduled:
            print(f"  [ ] {task.due} {task.time} {task.description} — {task.pet.name} ({task.duration_minutes} min)")
    else:
        print("  Nothing scheduled today.")

    if plan.skipped:
        print("\nCouldn't fit today:")
        for task in plan.skipped:
            print(f"  - {task.time} {task.description} — {task.pet.name} ({task.duration_minutes} min)")

    done = scheduler.filter_tasks(owner.all_tasks(), completed=True)
    if done:
        print("\nAlready done today:")
        for task in done:
            print(f"  [x] {task.time} {task.description} — {task.pet.name} ({task.duration_minutes} min)")

    warning = scheduler.check_conflicts(plan.scheduled)
    if warning:
        print()
        print(warning)

    print("\nWhy this plan:")
    print(plan.rationale)


if __name__ == "__main__":
    main()
