from datetime import time as dtime

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler, Time, TaskType

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ app. Enter your owner and pet info, add care tasks,
then generate a daily plan built by your scheduling logic.
"""
)

# --- Persist core objects in the session "vault" so they survive reruns ---
# Streamlit re-runs this whole script on every interaction. Without
# st.session_state, the Owner (and its pets/tasks) would be rebuilt from
# scratch every time. Create it once; reuse it on every later rerun.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
    st.session_state.scheduler = Scheduler()

owner = st.session_state.owner
scheduler = st.session_state.scheduler

# Map the friendly priority labels in the UI to the integer priority the
# Task class expects (1 = most important).
PRIORITY_MAP = {"high": 1, "medium": 2, "low": 3}

st.divider()

# --- Owner + availability -------------------------------------------------
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

col_a, col_b = st.columns(2)
with col_a:
    start_time = st.time_input("Available from", value=dtime(8, 0))
with col_b:
    end_time = st.time_input("Available until", value=dtime(12, 0))

# Store the availability window on the Owner as our Time value objects.
owner.set_availability(
    Time(start_time.hour, start_time.minute),
    Time(end_time.hour, end_time.minute),
)

st.divider()

# --- Adding a Pet ---------------------------------------------------------
st.subheader("Add a Pet")
pcol1, pcol2 = st.columns(2)
with pcol1:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
with pcol2:
    breed = st.text_input("Breed", value="")
    age = st.number_input("Age", min_value=0, max_value=40, value=1)

if st.button("Add pet"):
    if any(p.name == pet_name for p in owner.list_pets()):
        st.warning(f"{pet_name} is already added.")
    else:
        # Wired to the class method: register a new Pet on the Owner.
        owner.add_pet(Pet(name=pet_name, species=species, breed=breed, age=int(age)))
        st.success(f"Added pet {pet_name}.")

# Show the owner's current pets.
pets = owner.list_pets()
if pets:
    st.caption("Pets: " + ", ".join(f"{p.name} ({p.species})" for p in pets))

st.divider()

# --- Scheduling a Task ----------------------------------------------------
st.markdown("### Add a Task")
st.caption("Add tasks for a pet. These feed directly into the scheduler.")

if not pets:
    st.info("Add a pet above before creating tasks.")
else:
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        target_pet_name = st.selectbox("Pet", [p.name for p in pets])
    with col2:
        task_title = st.text_input("Task title", value="Morning walk")
    with col3:
        task_type = st.selectbox("Type", [t.value for t in TaskType])
    with col4:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col5:
        priority = st.selectbox("Priority", ["high", "medium", "low"])

    # Optional fixed appointment time (e.g. meds that must happen at a set
    # hour). Flexible tasks leave this off and get packed into free gaps.
    use_fixed = st.checkbox("Fixed start time (e.g. meds at a set hour)")
    fixed_start_val = None
    if use_fixed:
        fixed_start_val = st.time_input("Starts at", value=dtime(9, 0), key="fixed_start")

    if st.button("Add task"):
        # Find the selected pet and wire the button to Pet.add_task().
        target_pet = next(p for p in pets if p.name == target_pet_name)
        fixed_start = (
            Time(fixed_start_val.hour, fixed_start_val.minute) if use_fixed else None
        )
        target_pet.add_task(
            Task(
                name=task_title,
                type=TaskType(task_type),
                duration_minutes=int(duration),
                priority=PRIORITY_MAP[priority],
                fixed_start=fixed_start,
            )
        )
        st.success(f"Added '{task_title}' to {target_pet.name}.")

# Show every task across all of the owner's pets.
all_tasks = owner.all_tasks()
if all_tasks:
    st.markdown("#### Current Tasks")

    # --- Filter controls, wired to Owner.filter_tasks() -------------------
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        pet_filter = st.selectbox(
            "Filter by pet", ["All pets"] + [p.name for p in pets]
        )
    with fcol2:
        status_filter = st.selectbox("Filter by status", ["All", "Pending", "Completed"])

    # Translate the friendly UI choices into filter_tasks() arguments.
    pet_arg = None if pet_filter == "All pets" else pet_filter
    completed_arg = {"All": None, "Pending": False, "Completed": True}[status_filter]
    filtered = owner.filter_tasks(pet_name=pet_arg, completed=completed_arg)

    # Present them sorted by priority (1 = most important first).
    filtered = sorted(filtered, key=lambda t: t.priority)

    # --- At-a-glance summary metrics -------------------------------------
    mcol1, mcol2, mcol3 = st.columns(3)
    mcol1.metric("Shown", len(filtered))
    mcol2.metric("Pending", sum(1 for t in filtered if not t.completed))
    mcol3.metric("Completed", sum(1 for t in filtered if t.completed))

    if filtered:
        st.table(
            [
                {
                    "Task": t.name,
                    "Type": t.type.value.title(),
                    "Duration": f"{t.duration_minutes} min",
                    "Priority": {1: "🔴 High", 2: "🟡 Medium", 3: "🟢 Low"}.get(
                        t.priority, str(t.priority)
                    ),
                    "Fixed start": t.fixed_start.format() if t.fixed_start else "—",
                    "Status": "✅ Done" if t.completed else "⏳ Pending",
                }
                for t in filtered
            ]
        )
    else:
        st.warning("No tasks match the current filters.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Build schedule -------------------------------------------------------
st.subheader("Build Schedule")
st.caption("Generates a daily plan by priority within your availability window.")

if st.button("Generate schedule"):
    if not all_tasks:
        st.warning("Add at least one task first.")
    else:
        plan = scheduler.build_plan(owner)
        if not plan:
            st.warning("No tasks fit in the available time. Try widening your window.")
        else:
            st.success(
                f"Planned {len(plan)} task(s) for {owner.name} — "
                f"{scheduler.remaining_minutes} min free."
            )
            st.markdown(f"### 📅 Today's Schedule for {owner.name}")
            # Display the plan in chronological order using the Scheduler's own
            # sorting method rather than re-sorting here in the UI.
            ordered_plan = scheduler.sort_by_time(plan)
            st.table(
                [
                    {
                        "Start": t.scheduled_start.format() if t.scheduled_start else "--:--",
                        "End": t.get_end_time().format() if t.get_end_time() else "--:--",
                        "Task": t.name,
                        "Duration": f"{t.duration_minutes} min",
                        "Priority": {1: "🔴 High", 2: "🟡 Medium", 3: "🟢 Low"}.get(
                            t.priority, str(t.priority)
                        ),
                        "Type": "📌 Fixed" if t.fixed_start else "🔄 Flexible",
                    }
                    for t in ordered_plan
                ]
            )
            # Surface any overlapping time windows via the Scheduler's conflict
            # check (e.g. two pets' tasks landing on the same slot).
            conflicts = scheduler.detect_conflicts(ordered_plan)
            if conflicts:
                st.error("⚠️ Schedule conflicts detected:")
                for warning in conflicts:
                    st.write(f"- {warning}")
            # Tell the owner plainly if anything got left out, and why.
            if scheduler.skipped_tasks:
                st.warning(
                    "Couldn't schedule: "
                    + ", ".join(
                        f"{t.name} ({reason})"
                        for t, reason in scheduler.skipped_tasks
                    )
                )
            st.code(scheduler.explain_plan())
