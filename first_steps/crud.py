from sqlalchemy import select
from sqlalchemy.orm import Session
from tracker.db import engine

from first_steps.models import Base, Task


def close_task(task_id: int) -> bool:
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if task is None:
            return False

        task.is_done = True
        session.commit()
        return True


def delete_task(task_id: int) -> bool:
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if task is None:
            return False

        session.delete(task)
        session.commit()
        return True


def main() -> None:
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        check_report = Task(title="Проверить отчёт")
        submit_report = Task(title="Сдать отчёт")
        session.add(check_report)
        session.add(submit_report)
        session.add(Task(title="Собрать данные", is_done=True))
        session.commit()
        check_id = check_report.id
        submit_id = submit_report.id

    open_tasks = select(Task).where(Task.is_done.is_(False)).order_by(Task.id.desc())

    with Session(engine) as session:
        for task in session.scalars(open_tasks):
            print(task.id, task.title)

    close_task(check_id)
    delete_task(submit_id)

    with Session(engine) as session:
        closed = session.get(Task, check_id)
        if closed is not None:
            print(closed.title, closed.is_done)
        print(session.get(Task, submit_id))


if __name__ == "__main__":
    main()
