# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
A user should be able to add a pet, schedule a walk, and see today's tasks.
One Owner has 1 or many Pets.
Owner requests plan from Scheduler.
Scheduler reads constraints from Owner.
Scheduler reads Pet; Scheduler looks at a Pet's data to build the plan but does not own or store the Pet.
Scheduler plans Tasks.
0 or many Tasks belong to each Pet.
- What classes did you include, and what responsibilities did you assign to each?
There should be four classes: Scheduler, Owner, Pet, and Task.
Scheduler behaviors:
    - generates a schedule when given an owner, pet, and tasks, returned a list of Tasks.
    - explain plan: input a list of Tasks and return a string.
Owner has a (string) name, (integer) available_time_minutes, (dictionary) preferences, and (list of type Pet) pets.
Owner behavior:
    - add_pet given input Pet (return None), append to list of Pets
Pet has (string) name and (string) species.
Task has (string) title, (integer) durtaion_in_minutes, and (integer) priority.

**b. Design changes**

- Did your design change during implementation?
Yes
- If yes, describe at least one change and why you made it.
1. Changed `def generate_schedule(self, owner: Owner, pet: Pet, tasks: list[Task]) -> list[Task]:` to `def generate_schedule(self, owner: Owner, tasks: list[Task]) -> list[Task]:` because an Owner owns `list[Pet]`, and each Task already references its own pet. So passing one `pet` is both redundant (it's on the Task) and too narrow (a daily plan should cover all the owner's lets). The scheduler gets pets via `task.pet` or `owner.pets`, no separate `pet` param needed.
2. `generate_schedule` returns `list[Task]` and `explain_plan` takes `list[Task]`. But therequirement says the assistant must "produce a daily plan and explain why." A bare list can't hold the reasoning, scheduled times, or which tasks were dropped for lack of time. Consider a `Plan` dataclass with attributes (list[Task]) scheduled, (list[Task]) skipped, and (string) rationale. Now `explain_plan(plan: Plan)` has something to explain. Right now the "explain why" behavior has no data to draw on.
3. `preferences: dict` is untyled. `dict` loses all structure so the scheduler won't know what keys exist ("preferred_walk_time"? "skip_grooming"?). Fine for a skeleton, but it'll become a source of KeyErrors. A small dataclass or documented keys would help once you know what constraints matter.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
The scheduler considers five constraints:
1. Time budget: each owner has available_time_minutes, and the scheduler greedily fills that limit and won't exceed it.
2. Priority: higher-priority tasks are selected first.
3. Durtaion: ties broken by shortest task first, to fit more into the day.
4. Fiarness across pets: a per-pet rank so one pet can't monopolize the whole time budget.
5. Time-slow conflicts: detects overlapping start/end times and warns.

- How did you decide which constraints mattered most?
The guiding principle is feasibility > correctness > fairness > efficiency > preference.
Time budget matters most because a plan that overbooks the owner's day is useless so the owner physically cannot do it. Given limited time, high priority matters more than medium priority matters more than low priority + fairness across pets avoiding one pet taking up a majority of the schedule. When two tasks are equal, the shorter one wins so more tasks fit. Lastly, preferred time is last. 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
Lost guaranteed O(n²). The old version sorted by start time and breaked out of the the inner loop as soon as a task started after the current one ended. In a typical day (tasks spread across morning/afternoon/evening), that made most comparisons stop early — closer to linear in practice. The combinations version always checks all n(n−1)/2 pairs, with no shortcut.

What we gained — clarity and a reusable predicate. The overlap rule now lives in one named, independently testable method (_overlaps), and detect_conflicts is a single readable comprehension. No index arithmetic, no list-slice copies.

- Why is that tradeoff reasonable for this scenario?
Why the trade is worth it here: n is a pet owner's daily task list — a handful of items, maybe a few dozen. At that scale the difference between "early break" and "all pairs" is microseconds, invisible to the user. Meanwhile the code is read and maintained far more often than it runs, so readability is the higher-value asset.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used Claude for design brainstorming, implementing code, debugging, refactoring, and testing.
- What kinds of prompts or questions were most helpful?
Target prompts specific to a block of code in a specific file were most helpful when debugging or clarifying behavior.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
I did not accept the initial design Claude gave as-is.
- How did you evaluate or verify what the AI suggested?
I asked Claude clarifying questions e.g. "Should the scheduler use an Owner or should an Owner use a Scheduler?"
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
1. Task lifecycle and recurrence
- Completion flips completed False → True (test_task_completion)
- Daily recurrence spawns a next task due +1 day (including a leap-year Feb 28 → 29 case) (test_daily_recurrence_advances_due_date)
- Weekly recurrence advances +7 days (test_weekly_recurrence_advances_seven_days)
- One-off tasks don't repeat (test_non_recurring_task_does_not_repeat, test_next_occurrence_none_for_non_recurring)
- Recurrence anchors to the task's own due date, not today (test_recurrence_anchors_to_due_not_today)
- Adding a task increments the pet's task count (test_task_addition)
2. Conflict detection
- Overlapping time slots on the same day are flagged across pets (test_detect_conflicts_finds_overlaps)
- Same times on different days don't conflict (test_detect_conflicts_ignores_different_days)
- Exact same start time overlaps (test_same_start_time_conflicts)
- Back-to-back / adjacent tasks (half-open intervals) don't conflict (test_adjacent_tasks_do_not_conflict)
- check_conflicts returns a human-readable warning naming both tasks (test_check_conflicts_returns_warning_string), an empty string when clean (test_check_conflicts_no_overlap_is_empty), and never crashes on malformed time (test_check_conflicts_does_not_crash_on_bad_time)
3. Sorting and filtering
- sort_by_time orders earliest-first (test_sort_by_time_orders_earliest_first)
- filter_tasks by completion status, by case-insensitive pet name, and returns all when no criteria given
4. Schedule generation (greedy budget)
Fits everything when there's room; skips lowest priority when over budget; output is chronological, not priority-ordered; ties break on shorter duration; exact fit is inclusive; completed tasks excluded; empty owner yields a clear rationale; zero available time skips all without crashing
5. Multi-pet fairness (round-robin)
- A tight budget is split evenly across pets rather than hogged by the first-added one (test_generate_schedule_shares_budget_across_pets)
- Each pet's top task is served before any pet's second (test_fairness_serves_each_pets_top_task_first)
- Within a pet's turn, its higher-priority task ranks first (test_fairness_still_respects_priority_within_a_round)
- Why were these tests important?
These tests were important because Pawpal+ makes decisions on the Owner's behalf including what to schedule, what to skip, what to warn about and each test guards a place where a plausible-looking implementation quietly does the wrong thing.

**b. Confidence**

- How confident are you that your scheduler works correctly?
I am failry confident the scheduler works correctly.
- What edge cases would you test next if you had more time?
Mixed scheduled/skipped rationale output, unsupported/whitespace frequency values, and add_pet dedup.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I am most satified with the Multi-pet fairness (round-robin) so that one pet is not favored above all others.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would improve use of frequency. I would allow conflicts of being able to walk multiple pets at the same time.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
The hard part of a schedulign is the decisions the system makes on my behalf are tests help identify the decisions.