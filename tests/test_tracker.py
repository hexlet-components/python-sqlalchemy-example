import os
import subprocess
import sys
import unittest
from uuid import uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


class TrackerTest(unittest.TestCase):
    def test_upgrading_a_populated_database(self) -> None:
        url = make_url(os.environ["TEST_DATABASE_URL"])
        schema = f"tracker_test_{uuid4().hex}"
        admin = create_engine(url)
        with admin.begin() as connection:
            connection.exec_driver_sql(f"CREATE SCHEMA {schema}")
        self.addCleanup(admin.dispose)

        def remove_schema() -> None:
            with admin.begin() as connection:
                connection.exec_driver_sql(f"DROP SCHEMA {schema} CASCADE")

        self.addCleanup(remove_schema)
        scoped_url = url.update_query_dict({"options": f"-csearch_path={schema}"})
        env = dict(
            os.environ, DATABASE_URL=scoped_url.render_as_string(hide_password=False)
        )
        engine = create_engine(scoped_url)
        self.addCleanup(engine.dispose)

        def run(module: str, *args: str) -> str:
            return subprocess.check_output(
                [sys.executable, "-m", module, *args], env=env, text=True
            )

        run("alembic", "upgrade", "32e016547c7d")
        with engine.begin() as connection:
            key = connection.execute(
                text(
                    "INSERT INTO tasks (title, is_done) VALUES ('Контроль', false) RETURNING id"
                )
            ).scalar_one()
        run("alembic", "upgrade", "head")
        run("alembic", "check")
        with engine.connect() as connection:
            self.assertEqual(
                connection.execute(text("SELECT id, name, is_done FROM tasks")).one(),
                (key, "Контроль", False),
            )
            self.assertIsNone(connection.scalar(text("SELECT project_id FROM tasks")))
        output = run("tracker.demo")
        self.assertIn("Отложенная загрузка: 4 SELECT", output)
        self.assertIn("Предварительная загрузка: 2 SELECT", output)
        self.assertIn("Справка: 0", output)
        self.assertIn("Архив: 0", output)
        self.assertIn("Сайт: 2", output)
        with engine.connect() as connection:
            counts = (
                connection.execute(text("SELECT id FROM projects ORDER BY id"))
                .scalars()
                .all()
            )
        self.assertGreaterEqual(len(counts), 2)
        run("tracker.demo")
        result = run("tracker.async_report", str(counts[0]), str(counts[1]))
        self.assertIn(f"{counts[0]}: []", result)
        self.assertIn(f"{counts[1]}: ['Меню', 'Поиск']", result)
        with engine.connect() as connection:
            self.assertEqual(
                connection.scalar(text("SELECT COUNT(*) FROM projects")), len(counts)
            )
        run("alembic", "downgrade", "base")
        run("alembic", "upgrade", "head")
