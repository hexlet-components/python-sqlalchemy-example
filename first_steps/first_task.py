from sqlalchemy import select
from sqlalchemy.orm import Session

from first_steps.models import Base, Task
from tracker.db import engine


def main() -> None:
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        task = Task(title="Проверить отчёт")
        session.add(task)
        session.commit()

    with Session(engine) as session:
        for saved_task in session.scalars(select(Task)):
            print(saved_task.id, saved_task.title, saved_task.is_done)


if __name__ == "__main__":
    main()
