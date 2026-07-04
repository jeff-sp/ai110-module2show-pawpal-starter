import os
import sys

# Make the project root importable when running the test directly.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Owner, Pet, Task, Scheduler  # noqa: E402


def test_task_completion():
    """mark_complete() should flip the task's status to done."""
    task = Task("Morning walk", duration_minutes=30, priority=5)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_task_addition():
    """Adding a task to a Pet should increase that pet's task count."""
    rex = Pet(name="Rex", species="dog")
    assert len(rex.tasks) == 0

    rex.add_task(Task("Feed", duration_minutes=10, priority=5))

    assert len(rex.tasks) == 1
