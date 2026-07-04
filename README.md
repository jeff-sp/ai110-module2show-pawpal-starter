# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:
Today's Schedule for Sam
(available time: 60 min)
========================================
  [ ] Feed — Milo (10 min)
  [ ] Morning walk — Rex (30 min)
  [ ] Play / enrichment — Milo (15 min)

Couldn't fit today:
  - Grooming — Rex (40 min)

Why this plan:
Scheduled 'Feed' for Milo (10 min, priority 5).
Scheduled 'Morning walk' for Rex (30 min, priority 5).
Scheduled 'Play / enrichment' for Milo (15 min, priority 3).
Skipped 'Grooming' for Rex — not enough time remaining.

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

Beyond the basic priority-greedy plan in `Scheduler.generate_schedule()`, PawPal+
adds several small algorithms that make the daily plan more realistic for a pet
owner. Each feature and the method that implements it:

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Orders tasks chronologically by their `"HH:MM"` start time so the plan reads as a real day. Selection still happens by priority; this only reorders the final plan. |
| Filtering | `Scheduler.filter_tasks()` | Returns tasks matching a completion status and/or pet name. Both filters are optional; pet-name matching is case-insensitive. |
| Conflict detection | `Scheduler.detect_conflicts()`, `Scheduler.check_conflicts()`, `Scheduler._overlaps()` | Flags tasks whose time slots overlap on the same day (across pets, not just within one). |
| Recurring tasks | `Task.mark_task_complete()`, `Task.next_occurrence()` | Completing a `"daily"` or `"weekly"` task auto-creates its next occurrence. |

### Sorting behavior — `Scheduler.sort_by_time()`

Each `Task` carries a `time` field (`"HH:MM"`, 24-hour). `sort_by_time()` returns
the tasks ordered earliest-first, using the shared `_start_minutes()` helper to
convert `"HH:MM"` into minutes past midnight (so unpadded times like `"9:30"`
still sort correctly). `generate_schedule()` selects tasks by priority to fill
the time budget, then calls `sort_by_time()` so the printed plan is chronological.

### Filtering behavior — `Scheduler.filter_tasks()`

`filter_tasks(tasks, completed=None, pet_name=None)` narrows a task list:

- `completed=True` / `completed=False` filters by completion status (`None` ignores it).
- `pet_name="rex"` returns only that pet's tasks, matched case-insensitively.
- Passing both combines them (e.g. "Milo's incomplete tasks").

The demo uses `filter_tasks(owner.all_tasks(), completed=True)` to print an
"Already done today" section.

### Conflict detection — `Scheduler.detect_conflicts()` / `check_conflicts()`

Each task occupies the half-open interval `[start, start + duration)`.
`_overlaps()` is the core predicate: two tasks conflict when they share a due
date and each starts before the other ends (identical start times count).

- `detect_conflicts()` returns the overlapping **pairs** (earliest first), using
  `itertools.combinations` over the time-sorted list.
- `check_conflicts()` is the **lightweight** wrapper: it returns a human-readable
  warning string (empty when there are none) and never raises — tasks with a
  malformed time are skipped and noted rather than crashing the program.

Conflicts are detected across different pets, not just within one pet.

### Recurring task logic — `Task.mark_task_complete()` / `next_occurrence()`

Marking a recurring task complete queues up its next instance automatically:

- `next_occurrence()` builds a fresh, uncompleted copy for `"daily"` or
  `"weekly"` tasks (returns `None` otherwise), advancing the `due` date with
  `timedelta(days=1)` / `timedelta(weeks=1)`. The delta is added to the task's
  **own** due date so the cadence stays anchored even if completed late, and
  `timedelta` handles month/year/leap-year rollovers correctly.
- `mark_task_complete()` marks the task done and attaches the new occurrence to
  the same pet.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
