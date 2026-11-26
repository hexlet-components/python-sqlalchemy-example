from sqlalchemy import and_, event, func, select, text
from sqlalchemy.orm import ORMExecuteState, Session, selectinload

from tracker.db import engine
from tracker.models import Project, Tag, Task


def prepare_projects() -> None:
    with Session(engine) as session, session.begin():
        # Два одновременных запуска должны увидеть один и тот же набор проектов.
        session.execute(text("SELECT pg_advisory_xact_lock(hashtext('tracker.demo'))"))
        if session.scalar(select(Project.id).limit(1)) is not None:
            return

        release = Tag(name="Релиз")
        site = Project(
            name="Сайт",
            tasks=[
                Task(name="Меню", tags=[release]),
                Task(name="Поиск"),
            ],
        )
        docs = Project(
            name="Справка",
            tasks=[Task(name="Словарь", is_done=True, tags=[release])],
        )
        session.add_all([Project(name="Архив"), site, docs])


def project_tasks(*, preload: bool) -> tuple[list[tuple[int, str, list[str]]], int]:
    stmt = select(Project).order_by(Project.id)
    if preload:
        stmt = stmt.options(selectinload(Project.tasks))

    query_count = 0

    def count_select(state: ORMExecuteState) -> None:
        nonlocal query_count
        if state.is_select:
            query_count += 1

    with Session(engine) as session:
        event.listen(session, "do_orm_execute", count_select)
        projects = [
            (project.id, project.name, sorted(task.name for task in project.tasks))
            for project in session.scalars(stmt)
        ]
    return projects, query_count


def show_tags() -> None:
    stmt = select(Task.name, Tag.name).join(Task.tags).order_by(Task.id, Tag.id)
    with Session(engine) as session:
        for task_name, tag_name in session.execute(stmt):
            print(f"  {task_name}: {tag_name}")


def show_open_counts() -> None:
    projects = Project.__table__
    tasks = Task.__table__
    open_tasks = and_(
        projects.c.id == tasks.c.project_id,
        tasks.c.is_done.is_(False),
    )
    stmt = (
        select(projects.c.id, projects.c.name, func.count(tasks.c.id))
        .select_from(projects.outerjoin(tasks, open_tasks))
        .group_by(projects.c.id, projects.c.name)
        .order_by(projects.c.id)
    )
    with engine.connect() as connection:
        for project_id, name, open_count in connection.execute(stmt):
            print(f"  {project_id} {name}: {open_count}")


def main() -> None:
    prepare_projects()
    lazy, lazy_count = project_tasks(preload=False)
    eager, eager_count = project_tasks(preload=True)
    if lazy != eager:
        raise RuntimeError("Списки проектов и задач при двух загрузках различаются")

    print(f"Отложенная загрузка: {lazy_count} SELECT")
    print(f"Предварительная загрузка: {eager_count} SELECT")
    print("Проекты и задачи при обоих способах загрузки:")
    for project_id, name, tasks in eager:
        print(f"  {project_id} {name}: {tasks}")
    print("Назначенные метки:")
    show_tags()
    print("Открытые задачи по проектам:")
    show_open_counts()


if __name__ == "__main__":
    main()
