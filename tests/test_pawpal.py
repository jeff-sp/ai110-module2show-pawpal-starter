import os
import sys
from datetime import date, timedelta

# Make the project root importable when running the test directly.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Owner, Pet, Task, Scheduler  # noqa: E402


def test_task_completion():
    """mark_task_complete() should flip the task's status to done."""
    task = Task("Morning walk", duration_minutes=30, priority=5)
    assert task.completed is False

    task.mark_task_complete()

    assert task.completed is True


def test_daily_recurrence_advances_due_date():
    """Completing a daily task should queue a new one due the next day."""
    rex = Pet(name="Rex", species="dog")
    walk = Task("Walk", duration_minutes=30, priority=5,
                frequency="daily", due=date(2024, 2, 28))
    rex.add_task(walk)

    walk.mark_task_complete()

    assert len(rex.tasks) == 2
    upcoming = rex.tasks[-1]
    assert upcoming.completed is False
    assert upcoming.due == date(2024, 2, 28) + timedelta(days=1)  # leap year -> Feb 29


def test_non_recurring_task_does_not_repeat():
    """A one-off task should not spawn a next occurrence."""
    rex = Pet(name="Rex", species="dog")
    groom = Task("Grooming", duration_minutes=40, priority=1, frequency="once")
    rex.add_task(groom)

    groom.mark_task_complete()

    assert len(rex.tasks) == 1


def test_detect_conflicts_finds_overlaps():
    """Overlapping time slots on the same day should be flagged, across pets."""
    scheduler = Scheduler()
    d = date(2026, 7, 4)
    walk = Task("Walk", 30, 5, time="07:30", due=d)   # 07:30-08:00
    feed = Task("Feed", 10, 5, time="07:45", due=d)   # 07:45-07:55 (overlaps)
    play = Task("Play", 15, 3, time="17:00", due=d)   # no overlap

    conflicts = scheduler.detect_conflicts([walk, feed, play])

    assert conflicts == [(walk, feed)]


def test_detect_conflicts_ignores_different_days():
    """Identical times on different due dates should not conflict."""
    scheduler = Scheduler()
    today = Task("Walk", 30, 5, time="07:30", due=date(2026, 7, 4))
    tomorrow = Task("Walk", 30, 5, time="07:30", due=date(2026, 7, 5))

    assert scheduler.detect_conflicts([today, tomorrow]) == []


def test_check_conflicts_returns_warning_string():
    """check_conflicts should return a human-readable warning for overlaps."""
    scheduler = Scheduler()
    d = date(2026, 7, 4)
    walk = Task("Walk", 30, 5, time="07:30", due=d)
    meds = Task("Medicine", 5, 5, time="07:30", due=d)  # same start time

    warning = scheduler.check_conflicts([walk, meds])

    assert "conflict" in warning.lower()
    assert "Walk" in warning and "Medicine" in warning


def test_check_conflicts_no_overlap_is_empty():
    """No overlaps should yield an empty string, not a warning."""
    scheduler = Scheduler()
    d = date(2026, 7, 4)
    a = Task("Walk", 30, 5, time="07:30", due=d)
    b = Task("Play", 15, 3, time="17:00", due=d)

    assert scheduler.check_conflicts([a, b]) == ""


def test_check_conflicts_does_not_crash_on_bad_time():
    """A malformed time must produce a warning, never raise."""
    scheduler = Scheduler()
    bad = Task("Broken", 10, 5, time="not-a-time")

    warning = scheduler.check_conflicts([bad])  # must not raise

    assert "Broken" in warning


def test_task_addition():
    """Adding a task to a Pet should increase that pet's task count."""
    rex = Pet(name="Rex", species="dog")
    assert len(rex.tasks) == 0

    rex.add_task(Task("Feed", duration_minutes=10, priority=5))

    assert len(rex.tasks) == 1


# --- Recurrence edge cases -------------------------------------------------

def test_weekly_recurrence_advances_seven_days():
    """Completing a weekly task should queue one due seven days later."""
    rex = Pet(name="Rex", species="dog")
    bath = Task("Bath", duration_minutes=20, priority=2,
                frequency="weekly", due=date(2026, 7, 4))
    rex.add_task(bath)

    bath.mark_task_complete()

    assert len(rex.tasks) == 2
    assert rex.tasks[-1].due == date(2026, 7, 11)


def test_recurrence_anchors_to_due_not_today():
    """next_occurrence advances from the task's own due date, even if late."""
    walk = Task("Walk", duration_minutes=30, priority=5,
                frequency="daily", due=date(2000, 1, 1))

    upcoming = walk.next_occurrence()

    assert upcoming.due == date(2000, 1, 2)  # not tomorrow relative to today


def test_next_occurrence_none_for_non_recurring():
    """A non-recurring task has no next occurrence."""
    groom = Task("Grooming", duration_minutes=40, priority=1, frequency="once")

    assert groom.next_occurrence() is None


# --- sort_by_time ----------------------------------------------------------

def test_sort_by_time_orders_earliest_first():
    """sort_by_time returns tasks ordered by start time, earliest first."""
    scheduler = Scheduler()
    late = Task("Play", 15, 3, time="17:00")
    early = Task("Walk", 30, 5, time="07:30")
    mid = Task("Feed", 10, 5, time="12:15")

    ordered = scheduler.sort_by_time([late, early, mid])

    assert ordered == [early, mid, late]


# --- Conflict boundaries ---------------------------------------------------

def test_same_start_time_conflicts():
    """Two tasks at the exact same start time overlap and are returned as a pair."""
    scheduler = Scheduler()
    d = date(2026, 7, 4)
    walk = Task("Walk", 30, 5, time="07:30", due=d)
    meds = Task("Medicine", 5, 5, time="07:30", due=d)

    assert scheduler.detect_conflicts([walk, meds]) == [(walk, meds)]


def test_adjacent_tasks_do_not_conflict():
    """Back-to-back tasks (half-open intervals) must not be flagged."""
    scheduler = Scheduler()
    d = date(2026, 7, 4)
    walk = Task("Walk", 30, 5, time="07:30", due=d)   # 07:30-08:00
    feed = Task("Feed", 15, 5, time="08:00", due=d)    # 08:00-08:15

    assert scheduler.detect_conflicts([walk, feed]) == []


# --- filter_tasks ----------------------------------------------------------

def test_filter_by_completion_status():
    """filter_tasks(completed=...) returns only tasks with that status."""
    scheduler = Scheduler()
    done = Task("Walk", 30, 5, completed=True)
    todo = Task("Feed", 10, 5, completed=False)

    assert scheduler.filter_tasks([done, todo], completed=False) == [todo]
    assert scheduler.filter_tasks([done, todo], completed=True) == [done]


def test_filter_by_pet_name_is_case_insensitive():
    """Pet-name filtering matches regardless of case."""
    scheduler = Scheduler()
    rex = Pet(name="Rex", species="dog")
    mia = Pet(name="Mia", species="cat")
    rex.add_task(Task("Walk", 30, 5))
    mia.add_task(Task("Feed", 10, 5))

    result = scheduler.filter_tasks(rex.tasks + mia.tasks, pet_name="rEx")

    assert len(result) == 1 and result[0].pet is rex


def test_filter_with_no_criteria_returns_all():
    """Omitting both filters returns the full list unchanged."""
    scheduler = Scheduler()
    tasks = [Task("Walk", 30, 5), Task("Feed", 10, 5)]

    assert scheduler.filter_tasks(tasks) == tasks


# --- generate_schedule -----------------------------------------------------

def _owner_with(available, *tasks):
    owner = Owner(name="Sam", available_time_minutes=available)
    pet = Pet(name="Rex", species="dog")
    for t in tasks:
        pet.add_task(t)
    owner.add_pet(pet)
    return owner


def test_generate_schedule_fits_everything():
    """When everything fits, all tasks are scheduled and none skipped."""
    scheduler = Scheduler()
    owner = _owner_with(
        60,
        Task("Walk", 30, 5, time="07:00"),
        Task("Feed", 10, 5, time="08:00"),
    )

    plan = scheduler.generate_schedule(owner)

    assert len(plan.scheduled) == 2
    assert plan.skipped == []


def test_generate_schedule_skips_by_priority():
    """When over budget, lower-priority tasks are skipped."""
    scheduler = Scheduler()
    high = Task("Meds", 30, 9, time="08:00")
    low = Task("Play", 30, 1, time="17:00")
    owner = _owner_with(30, high, low)

    plan = scheduler.generate_schedule(owner)

    assert plan.scheduled == [high]
    assert plan.skipped == [low]


def test_generate_schedule_output_is_chronological():
    """Scheduled tasks are returned in time order, not priority order."""
    scheduler = Scheduler()
    later_high = Task("Meds", 10, 9, time="18:00")
    earlier_low = Task("Walk", 10, 1, time="06:00")
    owner = _owner_with(60, later_high, earlier_low)

    plan = scheduler.generate_schedule(owner)

    assert plan.scheduled == [earlier_low, later_high]


def test_generate_schedule_priority_tie_breaks_on_duration():
    """Equal priority: the shorter task wins the last available slot."""
    scheduler = Scheduler()
    short = Task("Feed", 10, 5, time="08:00")
    long = Task("Walk", 30, 5, time="09:00")
    owner = _owner_with(10, short, long)  # only room for one

    plan = scheduler.generate_schedule(owner)

    assert plan.scheduled == [short]
    assert plan.skipped == [long]


def test_generate_schedule_exact_fit_is_inclusive():
    """A task exactly filling the remaining time should be scheduled."""
    scheduler = Scheduler()
    owner = _owner_with(30, Task("Walk", 30, 5, time="07:00"))

    plan = scheduler.generate_schedule(owner)

    assert len(plan.scheduled) == 1
    assert plan.skipped == []


def test_generate_schedule_excludes_completed_tasks():
    """Already-completed tasks are not part of the generated plan."""
    scheduler = Scheduler()
    done = Task("Walk", 30, 5, time="07:00", completed=True)
    todo = Task("Feed", 10, 5, time="08:00")
    owner = _owner_with(60, done, todo)

    plan = scheduler.generate_schedule(owner)

    assert plan.scheduled == [todo]


def test_generate_schedule_empty_owner():
    """An owner with no pets/tasks yields an empty plan with a clear rationale."""
    scheduler = Scheduler()
    owner = Owner(name="Sam", available_time_minutes=60)

    plan = scheduler.generate_schedule(owner)

    assert plan.scheduled == []
    assert plan.skipped == []
    assert plan.rationale == "No tasks to schedule."


def test_generate_schedule_zero_available_time():
    """With zero available time, every task is skipped and nothing crashes."""
    scheduler = Scheduler()
    owner = _owner_with(0, Task("Walk", 30, 5), Task("Feed", 10, 5))

    plan = scheduler.generate_schedule(owner)

    assert plan.scheduled == []
    assert len(plan.skipped) == 2


# --- Multi-pet fairness ----------------------------------------------------

def _two_pet_owner(available, pet_a_tasks, pet_b_tasks):
    """Owner with two pets; each argument is a list of Tasks for that pet."""
    owner = Owner(name="Jordan", available_time_minutes=available)
    a = Pet(name="Mochi", species="cat")
    b = Pet(name="Rex", species="dog")
    for t in pet_a_tasks:
        a.add_task(t)
    for t in pet_b_tasks:
        b.add_task(t)
    owner.add_pet(a)
    owner.add_pet(b)
    return owner


def test_generate_schedule_shares_budget_across_pets():
    """Equal priority/duration: a tight budget is split evenly, not hogged by one pet.

    Regression test for the bug where all of the first-added pet's tasks were
    scheduled before any of the second pet's got a turn.
    """
    scheduler = Scheduler()
    mochi = [Task(f"M{i}", 20, 5, time=f"{7 + i:02d}:00") for i in range(5)]
    rex = [Task(f"R{i}", 20, 5, time=f"{7 + i:02d}:30") for i in range(4)]
    owner = _two_pet_owner(120, mochi, rex)  # room for 6 of the 9 tasks

    plan = scheduler.generate_schedule(owner)

    assert len(plan.scheduled) == 6
    per_pet = {"Mochi": 0, "Rex": 0}
    for task in plan.scheduled:
        per_pet[task.pet.name] += 1
    assert per_pet == {"Mochi": 3, "Rex": 3}


def test_fairness_serves_each_pets_top_task_first():
    """Each pet's most important task is scheduled before any pet's second task."""
    scheduler = Scheduler()
    # Mochi's two tasks would consume the whole budget under a naive sort.
    mochi = [Task("M-top", 20, 5, time="07:00"), Task("M-second", 20, 5, time="08:00")]
    rex = [Task("R-top", 20, 5, time="07:30")]
    owner = _two_pet_owner(40, mochi, rex)  # room for only 2 tasks

    plan = scheduler.generate_schedule(owner)

    names = {t.description for t in plan.scheduled}
    assert names == {"M-top", "R-top"}
    assert plan.skipped[0].description == "M-second"


def test_fairness_still_respects_priority_within_a_round():
    """Within a pet, its higher-priority task is ranked first for its turn."""
    scheduler = Scheduler()
    mochi = [Task("M-low", 20, 1, time="09:00"), Task("M-high", 20, 9, time="08:00")]
    rex = [Task("R-mid", 20, 5, time="07:30")]
    owner = _two_pet_owner(40, mochi, rex)  # room for 2 tasks

    plan = scheduler.generate_schedule(owner)

    names = {t.description for t in plan.scheduled}
    # Mochi's slot goes to its high-priority task, not its low one.
    assert "M-high" in names and "M-low" not in names
