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
