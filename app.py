import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ interactive demo.

Add care tasks for your pet, then let the **Scheduler** sort them, warn about
time conflicts, and build a plan that fits your available time.
"""
)

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

st.divider()

# Higher number = more important, matching Task.priority in the backend.
PRIORITY_LEVELS = {"low": 1, "medium": 3, "high": 5}
# Reverse map so we can show friendly labels next to the numeric priority.
PRIORITY_LABELS = {1: "low", 3: "medium", 5: "high"}


def time_range(task) -> str:
    """Human-readable 'HH:MM–HH:MM' span for a task, or its raw time if unparseable."""
    try:
        start = Scheduler._start_minutes(task)
    except (ValueError, AttributeError):
        return task.time
    end = start + task.duration_minutes
    fmt = lambda m: f"{(m // 60) % 24:02d}:{m % 60:02d}"
    return f"{fmt(start)}–{fmt(end)}"


def priority_label(value: int) -> str:
    """Map a numeric priority back to its friendly label (falls back to the number)."""
    return PRIORITY_LABELS.get(value, str(value))

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")
available_time = st.number_input(
    "Available time today (minutes)", min_value=1, max_value=1440, value=60
)

# --- Pets: maintain a list so tasks can be assigned to different pets. ---
if "pets" not in st.session_state:
    # Seed with two pets so the multi-pet flow is obvious on first run.
    st.session_state.pets = [
        {"name": "Mochi", "species": "cat"},
        {"name": "Rex", "species": "dog"},
    ]

st.markdown("### Pets")
st.caption("Add each pet once, then assign tasks to them below.")

pcol1, pcol2 = st.columns(2)
with pcol1:
    new_pet_name = st.text_input("Pet name", value="", key="new_pet_name")
with pcol2:
    new_pet_species = st.selectbox("Species", ["dog", "cat", "other"], key="new_pet_species")

if st.button("Add pet"):
    name = new_pet_name.strip()
    if not name:
        st.warning("Give the pet a name first.")
    elif any(p["name"].lower() == name.lower() for p in st.session_state.pets):
        st.warning(f"A pet named {name} already exists.")
    else:
        st.session_state.pets.append({"name": name, "species": new_pet_species})
        st.rerun()

if st.session_state.pets:
    st.table(st.session_state.pets)
else:
    st.info("No pets yet. Add one above before creating tasks.")

st.markdown("### Tasks")
st.caption("Add a few tasks, each assigned to a pet. These feed into the scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

pet_names = [p["name"] for p in st.session_state.pets]

if pet_names:
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        task_pet = st.selectbox("Pet", pet_names)

    col4, col5 = st.columns(2)
    with col4:
        start_time = st.text_input("Start time (HH:MM)", value="07:30")
    with col5:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        st.session_state.tasks.append(
            {
                "title": task_title,
                "duration_minutes": int(duration),
                "time": start_time,
                "priority": priority,
                "pet": task_pet,
            }
        )
else:
    st.info("Add a pet above to start creating tasks.")

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
    if st.button("Clear tasks"):
        st.session_state.tasks = []
        st.rerun()
else:
    st.info("No tasks yet. Add one above.")


def build_owner() -> Owner:
    """Assemble the backend objects from the current UI inputs."""
    owner = Owner(name=owner_name, available_time_minutes=int(available_time))

    # Create one Pet per entry and keep a name -> Pet lookup for task routing.
    pets_by_name = {}
    for p in st.session_state.pets:
        pet = Pet(name=p["name"], species=p["species"])
        owner.add_pet(pet)
        pets_by_name[p["name"]] = pet

    for t in st.session_state.tasks:
        pet = pets_by_name.get(t["pet"])
        if pet is None:
            # Task refers to a pet that was removed; skip rather than crash.
            continue
        pet.add_task(
            Task(
                description=t["title"],
                duration_minutes=t["duration_minutes"],
                priority=PRIORITY_LEVELS[t["priority"]],
                time=t["time"],
            )
        )
    return owner


st.divider()

st.subheader("Build Schedule")
st.caption("Runs the Scheduler: sorts by time, flags conflicts, and fits your day.")

if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        owner = build_owner()
        scheduler = Scheduler()
        all_tasks = owner.all_tasks()

        # --- Conflicts: one clear, actionable warning per overlapping pair. ---
        valid = [t for t in all_tasks if scheduler._has_valid_time(t)]
        bad_time = [t for t in all_tasks if not scheduler._has_valid_time(t)]
        conflicts = scheduler.detect_conflicts(valid)

        st.markdown("### ⏰ Time conflicts")
        if not conflicts and not bad_time:
            st.success("No scheduling conflicts — every task has its own time slot. 🎉")
        for a, b in conflicts:
            a_who = a.pet.name if a.pet else "pet"
            b_who = b.pet.name if b.pet else "pet"
            st.warning(
                f"**Overlap:** {a_who}'s *{a.description}* ({time_range(a)}) runs into "
                f"{b_who}'s *{b.description}* ({time_range(b)}).\n\n"
                f"Consider moving one to a different time so you can give each "
                f"full attention."
            )
        for t in bad_time:
            st.info(
                f"Couldn't check *{t.description}* for conflicts — its time "
                f"\"{t.time}\" isn't in HH:MM format."
            )

        plan = scheduler.generate_schedule(owner)

        # --- Overview metrics. ---
        st.markdown(f"### 📋 Today's schedule for {owner.name}")
        m1, m2, m3 = st.columns(3)
        scheduled_minutes = sum(t.duration_minutes for t in plan.scheduled)
        m1.metric("Scheduled", len(plan.scheduled))
        m2.metric("Skipped", len(plan.skipped))
        m3.metric("Time used", f"{scheduled_minutes}/{owner.available_time_minutes} min")

        # --- The plan itself, sorted chronologically by the Scheduler. ---
        if plan.scheduled:
            st.success(f"Planned {len(plan.scheduled)} task(s) within your available time.")
            st.table(
                [
                    {
                        "time": time_range(task),
                        "task": task.description,
                        "pet": task.pet.name if task.pet else "",
                        "duration (min)": task.duration_minutes,
                        "priority": priority_label(task.priority),
                    }
                    for task in plan.scheduled
                ]
            )
        else:
            st.info("Nothing could be scheduled within your available time.")

        if plan.skipped:
            st.markdown("#### ⚠️ Couldn't fit today")
            st.warning(
                "These tasks were left out because the day's time budget ran out "
                "(lowest priority first):"
            )
            st.table(
                [
                    {
                        "time": time_range(task),
                        "task": task.description,
                        "pet": task.pet.name if task.pet else "",
                        "duration (min)": task.duration_minutes,
                        "priority": priority_label(task.priority),
                    }
                    for task in plan.skipped
                ]
            )

        with st.expander("Why this plan?"):
            st.text(plan.rationale)
