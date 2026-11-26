import argparse
import asyncio
import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from tracker.models import Project


async def task_names(
    sessions: async_sessionmaker[AsyncSession], project_id: int
) -> list[str]:
    stmt = (
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.tasks))
    )
    async with sessions() as session:
        project = (await session.scalars(stmt)).one_or_none()
        if project is None:
            raise ValueError(f"Проект с ключом {project_id} не найден")
        return sorted(task.name for task in project.tasks)


async def show_projects(first_id: int, second_id: int) -> None:
    engine = create_async_engine(os.environ["DATABASE_URL"])
    sessions = async_sessionmaker(engine)
    try:
        # Дождёмся закрытия обеих сессий и при ошибке в одном из запросов.
        results = await asyncio.gather(
            task_names(sessions, first_id),
            task_names(sessions, second_id),
            return_exceptions=True,
        )
        for project_id, result in zip((first_id, second_id), results, strict=True):
            if isinstance(result, BaseException):
                raise result
            print(f"{project_id}: {result}")
    finally:
        await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Показать задачи двух проектов")
    parser.add_argument("first_id", type=int, help="ключ первого проекта")
    parser.add_argument("second_id", type=int, help="ключ второго проекта")
    args = parser.parse_args()
    try:
        asyncio.run(show_projects(args.first_id, args.second_id))
    except ValueError as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
