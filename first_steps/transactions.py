from sqlalchemy import select
from sqlalchemy.orm import Session
from tracker.db import engine

from first_steps.models import Base, Task


def import_tasks(titles: list[str]) -> None:
    with Session(engine) as session, session.begin():
        for title in titles:
            if not title.strip():
                raise ValueError("У задачи нет названия")
            session.add(Task(title=title))
            session.flush()


def main() -> None:
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        task = Task(title="Написать инструкцию")
        session.add(task)
        print(task.id)
        session.flush()
        task_id = task.id
        print(task_id)
        session.rollback()

    with Session(engine) as session:
        print(session.get(Task, task_id))

    title = "Подготовить выпуск"
    try:
        import_tasks([title, ""])
    except ValueError as error:
        print(error)

    with Session(engine) as session:
        query = select(Task.id).where(Task.title == title)
        print(session.scalars(query).all())


if __name__ == "__main__":
    main()
