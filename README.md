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

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
