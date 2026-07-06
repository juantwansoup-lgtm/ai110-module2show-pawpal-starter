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

## ✨ Features

The scheduling logic in `pawpal_system.py` implements the following algorithms:

- **Priority-based plan building** — anchors fixed-time tasks (e.g. "meds at 09:00") at their exact slot, then greedily packs flexible tasks into the remaining gaps in priority order (ties broken by shortest duration, so more tasks fit).
- **Free-interval computation** — scans the availability window and computes the open gaps *around* fixed commitments, so flexible tasks never land on an occupied slot.
- **Sorting by time** — orders the plan chronologically using zero-padded `"HH:MM"` string comparison (`"08:30"` < `"10:00"`); unscheduled tasks sort to the end.
- **Conflict warnings** — pairwise overlap detection across *all* pets that returns human-readable warnings without crashing; back-to-back tasks (one ending as the next begins) are correctly *not* flagged.
- **Daily / weekly recurrence** — completing a recurring task auto-spawns its next occurrence, advancing the due date with `datetime.timedelta` (+1 day daily, +7 days weekly) so month/year/leap-year rollovers are handled correctly.
- **Task filtering** — filter by pet name and/or completion status, with both filters combining (e.g. one pet's pending tasks only).
- **Availability-derived capacity** — total care minutes are derived from the availability window, so capacity never drifts out of sync with a duplicate counter.

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

========================================
Today's Schedule for Sam
Pets: Biscuit, Mochi
========================================
Daily plan:
  08:00 - Feeding (10 min) [priority: 1]
  08:10 - Medication (5 min) [priority: 1]
  08:15 - Morning walk (30 min) [priority: 2]
  08:45 - Playtime (20 min) [priority: 3]
Remaining free time: 175 min
========================================

## 🧪 Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

The tests live in `tests/test_pawpal.py` and cover the most important
scheduling behaviors:

- **Task basics** — marking a task complete flips its status; adding a task to a pet increases that pet's task count.
- **Sorting correctness** — `Scheduler.sort_by_time()` returns tasks in chronological order by start time, even when given them out of order.
- **Recurrence logic** — completing a daily task creates a fresh, uncompleted copy due the following day and attaches it to the pet.
- **Conflict detection** — two tasks scheduled at the same time are flagged, while back-to-back tasks (one ending as the next begins) are correctly *not* flagged.

Sample test output:

```
6 passed in 0.02s
```

## 📐 Smarter Scheduling

PawPal+ goes beyond a basic plan with four pieces of smarter scheduling logic, all implemented in `pawpal_system.py`.

| Feature            | Method(s)                                                 | Notes                                                                  |
| ------------------ | --------------------------------------------------------- | ---------------------------------------------------------------------- |
| Task sorting       | `Scheduler.sort_by_time()`, `Pet.get_tasks_by_priority()` | Orders the plan by `"HH:MM"` start time; unscheduled tasks sort last.  |
| Filtering          | `Owner.filter_tasks(pet_name, completed)`                 | Optional filters that combine — e.g. one pet's pending tasks only.     |
| Conflict detection | `Scheduler.detect_conflicts()`, `Task.conflicts_with()`   | Returns overlap warnings without crashing; catches same- and cross-pet.|
| Recurring tasks    | `Task.next_occurrence()`, `Pet.mark_task_complete()`      | Completing a task spawns the next (+1 day daily, +7 days weekly).      |
| Plan building      | `Scheduler.build_plan()`, `Scheduler._free_intervals()`   | Anchors fixed times first, then gap-fills flexible tasks by priority.  |

### Sorting behavior

`Scheduler.sort_by_time()` orders tasks by their scheduled start time. Each start is compared as a zero-padded `"HH:MM"` string (so `"08:30"` < `"10:00"`), and unscheduled tasks fall to the end. `Pet.get_tasks_by_priority()` provides the alternative priority ordering (1 = most important first).

### Filtering behavior

`Owner.filter_tasks(pet_name=None, completed=None)` returns tasks narrowed by pet name and/or completion status. Both filters are optional and combine — e.g. `filter_tasks(pet_name="Mochi", completed=False)` returns only Mochi's pending tasks; passing nothing returns every task.

### Conflict detection logic

`Scheduler.detect_conflicts()` scans scheduled tasks pairwise via `Task.conflicts_with()` and returns a list of warning messages for overlapping time windows (empty if none). It is lightweight and non-fatal — it never raises, so the program keeps running and just reports the clash, whether the two tasks belong to the same pet or different pets.

### Recurring task logic

`Task.next_occurrence()` builds a fresh, uncompleted copy of a recurring task with its due date advanced by `datetime.timedelta` — +1 day for **daily** tasks, +7 days for **weekly** (one-off tasks return `None`). `Pet.mark_task_complete()` ties this to completion: finishing a recurring task automatically creates the next occurrence and attaches it to the pet.

## 🎬 Demo Walkthrough

### Main UI features (Streamlit app — `app.py`)

The app is a single scrolling page where a user can:

- **Set owner + availability** — enter the owner's name and pick an available-from / available-until window (the care window the scheduler plans within).
- **Add pets** — enter name, species, breed, and age; a running caption lists the current pets and duplicates are rejected with a warning.
- **Add tasks** — for a chosen pet, enter a title, type (walk / feeding / meds / enrichment / grooming), duration, and priority (high / medium / low). Optionally mark a task as a **fixed start time** for appointments.
- **Browse tasks** — a **Current Tasks** panel with filter dropdowns (by pet, by status) and summary metrics (shown / pending / completed), rendered as a polished table with colored priority badges.
- **Generate the schedule** — one button builds the day's plan and displays it as a timeline table, plus a plain-English explanation.

### Example workflow

1. Set the owner to **Sam** and the availability window to **08:00–12:00**.
2. **Add a pet** → Biscuit (Dog) and Mochi (Cat).
3. **Schedule tasks** → e.g. a fixed *Morning walk* at 08:30, fixed *Medication* at 09:15, and flexible *Feeding* and *Grooming*.
4. Click **Generate schedule** to **view today's schedule** as a chronological timeline.
5. Use the **Current Tasks** filters to view, say, only Mochi's pending tasks.

### Key Scheduler behaviors shown

- **Sorting** — the plan is displayed earliest-start-first via `sort_by_time()`, even though the tasks were added out of order.
- **Priority gap-filling** — fixed tasks anchor first; flexible tasks flow into the free gaps by priority.
- **Conflict warnings** — two tasks landing on the same slot (even across different pets) raise a warning instead of crashing.
- **Recurrence** — completing a daily/weekly task auto-creates its next occurrence.
- **Filtering** — tasks can be narrowed by pet and/or completion status.

### Sample CLI output

Running the demo script (`python main.py`) exercises the same logic in the terminal:

```
============================================
Today's Schedule for Sam
Pets: Biscuit, Mochi
============================================
Daily plan:
  08:00 - Feeding (10 min) [priority: 1]
  08:10 - Grooming (15 min) [priority: 2]
  08:30 - Morning walk (30 min) [priority: 2] (fixed)
  09:15 - Medication (5 min) [priority: 1] (fixed)
Remaining free time: 180 min

============================================
Planned tasks sorted by time (sort_by_time)
============================================
  08:00  Feeding
  08:10  Grooming
  08:30  Morning walk
  09:15  Medication

============================================
Filtering (filter_tasks)
============================================
Mochi's tasks:
  - Late playtime
  - Medication
  - Grooming
Pending (not completed) tasks:
  - Morning walk
  - Feeding
  - Medication
  - Grooming
Completed tasks:
  - Late playtime
Mochi's pending tasks (both filters at once):
  - Medication
  - Grooming

============================================
Recurrence (mark_task_complete)
============================================
Today is 2026-07-05
Biscuit's tasks before completing: ['Morning walk', 'Feeding', 'Bath']

Completed daily 'Feeding' (due 2026-07-05, completed=True)
  -> auto-created next: 'Feeding' due 2026-07-06, completed=False
Completed weekly 'Bath' (due 2026-07-05)
  -> auto-created next: 'Bath' due 2026-07-12
Completed one-off 'Grooming' -> next occurrence: None

Biscuit's tasks after completing:  ['Morning walk', 'Feeding', 'Bath', 'Feeding', 'Bath']

============================================
Conflict detection (detect_conflicts)
============================================
Scheduled: Vet call 09:00, Grooming appt 09:00, Evening walk 18:00
Found 1 conflict(s):
  WARNING: 'Biscuit: Vet call' (09:00-09:30) overlaps 'Mochi: Grooming appt' (09:00-09:30).
============================================
```
