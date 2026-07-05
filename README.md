# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## ✨ Features

The implemented algorithms (all in `pawpal_system.py`, detailed under
[Smarter Scheduling](#-smarter-scheduling)):

- **Priority-greedy planning** — fills the day's time budget highest-priority-first,
  shortest-task-first, and reports what couldn't fit (`generate_schedule`).
- **Fair multi-pet scheduling** — round-robins across pets so a tight budget is
  shared, not monopolized by whichever pet was added first (`_fairness_ranks`).
- **Sorting by time** — orders the final plan chronologically by each task's
  `"HH:MM"` start time (`sort_by_time`).
- **Conflict warnings** — flags overlapping time slots (across pets) and returns a
  human-readable, crash-safe warning string (`detect_conflicts`, `check_conflicts`).
- **Filtering** — narrows tasks by completion status and/or pet name, case-insensitively
  (`filter_tasks`).
- **Daily / weekly recurrence** — completing a recurring task auto-queues its next
  occurrence with the due date advanced (`mark_task_complete`, `next_occurrence`).
- **Plan explanation** — generates a line-by-line rationale of what was scheduled
  and what was skipped (`explain_plan`).

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
```
========================================
Insertion order (as added):
========================================
  14:00 Grooming — Rex
  07:30 Morning walk — Rex
  17:00 Play / enrichment — Milo
  08:00 Feed — Milo
  07:30 Medicine — Milo
  08:00 Feed — Milo

========================================
After sort_by_time (chronological):
========================================
  07:30 Morning walk — Rex
  07:30 Medicine — Milo
  08:00 Feed — Milo
  08:00 Feed — Milo
  14:00 Grooming — Rex
  17:00 Play / enrichment — Milo

========================================
filter_tasks demos:
========================================
  Rex's tasks: ['Grooming', 'Morning walk']
  Completed:   ['Feed']
  Incomplete:  ['Grooming', 'Morning walk', 'Play / enrichment', 'Medicine', 'Feed']

========================================
Today's Schedule for Sam
(available time: 60 min)
========================================
  [ ] 2026-07-04 07:30 Medicine — Milo (5 min)
  [ ] 2026-07-04 07:30 Morning walk — Rex (30 min)
  [ ] 2026-07-05 08:00 Feed — Milo (10 min)
  [ ] 2026-07-04 17:00 Play / enrichment — Milo (15 min)

Couldn't fit today:
  - 14:00 Grooming — Rex (40 min)

Already done today:
  [x] 08:00 Feed — Milo (10 min)

⚠ Scheduling conflicts (overlapping times):
  07:30 Medicine (Milo) overlaps 07:30 Morning walk (Rex)

Why this plan:
Scheduled 'Medicine' for Milo (5 min, priority 5).
Scheduled 'Morning walk' for Rex (30 min, priority 5).
Scheduled 'Feed' for Milo (10 min, priority 5).
Scheduled 'Play / enrichment' for Milo (15 min, priority 3).
Skipped 'Grooming' for Rex — not enough time remaining.
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python3 -m pytest

# Coverage for the whole project, terminal summary
python -m pytest --cov=. tests/

# Just the module under test, showing which lines are missed
python -m pytest --cov=pawpal_system --cov-report=term-missing tests/

```

Confidence Level in the system's reliability based on the test results: 5 stars

Sample test output:

```
$ python3 -m pytest              
================================================================== test session starts ==================================================================
platform darwin -- Python 3.8.17, pytest-8.3.5, pluggy-1.5.0
rootdir: /Users/jeffsanpedro/codepath/AI110/ai110-module2show-pawpal-starter
plugins: cov-5.0.0
collected 29 items                                                                                                                                      

tests/test_pawpal.py .............................                                                                                                [100%]

================================================================== 29 passed in 0.08s ===================================================================

$ python -m pytest --cov=. tests/
================================================================== test session starts ==================================================================
platform darwin -- Python 3.8.17, pytest-8.3.5, pluggy-1.5.0
rootdir: /Users/jeffsanpedro/codepath/AI110/ai110-module2show-pawpal-starter
plugins: cov-5.0.0
collected 29 items                                                                                                                                      

tests/test_pawpal.py .............................                                                                                                [100%]

---------- coverage: platform darwin, python 3.8.17-final-0 ----------
Name                   Stmts   Miss  Cover
------------------------------------------
app.py                   122    122     0%
main.py                   59     59     0%
pawpal_system.py         129      0   100%
tests/test_pawpal.py     214      0   100%
------------------------------------------
TOTAL                    524    181    65%


================================================================== 29 passed in 0.23s ===================================================================

$ python -m pytest --cov=pawpal_system --cov-report=term-missing tests/
================================================================== test session starts ==================================================================
platform darwin -- Python 3.8.17, pytest-8.3.5, pluggy-1.5.0
rootdir: /Users/jeffsanpedro/codepath/AI110/ai110-module2show-pawpal-starter
plugins: cov-5.0.0
collected 29 items                                                                                                                                      

tests/test_pawpal.py .............................                                                                                                [100%]

---------- coverage: platform darwin, python 3.8.17-final-0 ----------
Name               Stmts   Miss  Cover   Missing
------------------------------------------------
pawpal_system.py     129      0   100%
------------------------------------------------
TOTAL                129      0   100%


================================================================== 29 passed in 0.14s ===================================================================
```

## 📐 Smarter Scheduling

Beyond the basic priority-greedy plan in `Scheduler.generate_schedule()`, PawPal+
adds several small algorithms that make the daily plan more realistic for a pet
owner. Each feature and the method that implements it:

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Fair multi-pet scheduling | `Scheduler.generate_schedule()`, `Scheduler._fairness_ranks()` | Round-robins across pets so a tight time budget is shared instead of being consumed entirely by whichever pet was added first. |
| Task sorting | `Scheduler.sort_by_time()` | Orders tasks chronologically by their `"HH:MM"` start time so the plan reads as a real day. Selection happens by fairness + priority; this only reorders the final plan. |
| Filtering | `Scheduler.filter_tasks()` | Returns tasks matching a completion status and/or pet name. Both filters are optional; pet-name matching is case-insensitive. |
| Conflict detection | `Scheduler.detect_conflicts()`, `Scheduler.check_conflicts()`, `Scheduler._overlaps()` | Flags tasks whose time slots overlap on the same day (across pets, not just within one). |
| Recurring tasks | `Task.mark_task_complete()`, `Task.next_occurrence()` | Completing a `"daily"` or `"weekly"` task auto-creates its next occurrence. |

### Fair multi-pet scheduling — `Scheduler.generate_schedule()` / `_fairness_ranks()`

When several pets compete for a limited time budget, a naive "highest priority,
then shortest" sort lets ties fall back to insertion order — so every task of the
first-added pet gets scheduled before any task of the second. `generate_schedule()`
avoids this by **round-robining across pets**:

- `_fairness_ranks()` ranks each task **within its own pet** (`0` = that pet's most
  important task), ordered by priority (highest first) then duration (shortest first).
- `generate_schedule()` then sorts by `(rank, -priority, duration_minutes)`. The
  leading `rank` means every pet's #1 task is considered before any pet's #2, so
  the budget is split fairly. Within a single round, `-priority` still wins and
  `duration` breaks remaining ties.
- The greedy fill and final `sort_by_time()` are unchanged; only the selection
  order is fairer.

This is *fairness-first within each round*: a pet's most important task outranks
another pet's second task even if that second task has higher priority.

### Sorting behavior — `Scheduler.sort_by_time()`

Each `Task` carries a `time` field (`"HH:MM"`, 24-hour). `sort_by_time()` returns
the tasks ordered earliest-first, using the shared `_start_minutes()` helper to
convert `"HH:MM"` into minutes past midnight (so unpadded times like `"9:30"`
still sort correctly). `generate_schedule()` selects tasks by fairness + priority
to fill the time budget, then calls `sort_by_time()` so the printed plan is
chronological.

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

### Main UI features

Launch the app with `streamlit run app.py`. The page is organized top to bottom:

- **Owner** — set the owner's name and the total time available for pet care today
  (the budget the scheduler fits tasks into).
- **Pets** — maintain a list of pets. Add a pet by name + species; duplicate and
  blank names are rejected. Each pet must exist before you can assign tasks to it.
- **Tasks** — add a task with a title, duration, start time (`HH:MM`), priority
  (low / medium / high), and **which pet it belongs to**. Added tasks appear in a
  table; "Clear tasks" empties the list.
- **Build Schedule** — press **Generate schedule** to run the `Scheduler`. Results
  show time-conflict warnings, an overview (scheduled / skipped / time used), the
  chronological plan, any tasks that couldn't fit, and an expandable rationale.

### Example workflow

1. Enter the owner (e.g. *Jordan*, 120 minutes available).
2. Add two pets — *Mochi* (cat) and *Rex* (dog).
3. Add tasks and assign each to a pet: *Morning walk* for Mochi at `07:30`,
   *Morning walk* for Rex at `07:30`, *breakfast* for each, and so on.
4. Press **Generate schedule**.
5. Review the results: overlapping tasks are flagged, the plan lists what fits in
   time order, and the leftovers appear under "Couldn't fit today."

### Key Scheduler behaviors on display

- **Fair multi-pet scheduling** — with a tight budget, slots are split evenly
  across pets rather than being consumed by whichever pet was added first.
- **Sorting by time** — the final plan is chronological even though tasks are
  *selected* by priority.
- **Conflict warnings** — each overlapping pair (across pets) is shown as its own
  warning with start–end ranges and a suggested fix.
- **Priority-based fit** — when everything won't fit, lower-priority tasks are the
  ones skipped, and the rationale explains why.

### Sample CLI output

The same core logic runs headless via `python main.py`, which exercises sorting,
filtering, scheduling, conflict detection, and recurrence:

```
========================================
Insertion order (as added):
========================================
  14:00 Grooming — Rex
  07:30 Morning walk — Rex
  17:00 Play / enrichment — Milo
  08:00 Feed — Milo
  07:30 Medicine — Milo
  08:00 Feed — Milo

========================================
After sort_by_time (chronological):
========================================
  07:30 Morning walk — Rex
  07:30 Medicine — Milo
  08:00 Feed — Milo
  08:00 Feed — Milo
  14:00 Grooming — Rex
  17:00 Play / enrichment — Milo

========================================
filter_tasks demos:
========================================
  Rex's tasks: ['Grooming', 'Morning walk']
  Completed:   ['Feed']
  Incomplete:  ['Grooming', 'Morning walk', 'Play / enrichment', 'Medicine', 'Feed']

========================================
Today's Schedule for Sam
(available time: 60 min)
========================================
  [ ] 2026-07-04 07:30 Medicine — Milo (5 min)
  [ ] 2026-07-04 07:30 Morning walk — Rex (30 min)
  [ ] 2026-07-05 08:00 Feed — Milo (10 min)
  [ ] 2026-07-04 17:00 Play / enrichment — Milo (15 min)

Couldn't fit today:
  - 14:00 Grooming — Rex (40 min)

Already done today:
  [x] 08:00 Feed — Milo (10 min)

⚠ Scheduling conflicts (overlapping times):
  07:30 Medicine (Milo) overlaps 07:30 Morning walk (Rex)

Why this plan:
Scheduled 'Medicine' for Milo (5 min, priority 5).
Scheduled 'Morning walk' for Rex (30 min, priority 5).
Scheduled 'Feed' for Milo (10 min, priority 5).
Scheduled 'Play / enrichment' for Milo (15 min, priority 3).
Skipped 'Grooming' for Rex — not enough time remaining.
```
