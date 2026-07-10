import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from models.schemas import (
    ApplicationCreate,
    ApplicationListResponse,
    ApplicationRecord,
    ApplicationStoreResponse,
    GeneratedEmail,
    Job,
)


class ApplicationStore:

    def __init__(self, db_path: str = "applications.db"):
        self.db_path = Path(db_path)
        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self) -> None:
        if self.db_path.parent != Path("."):
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    selected_job TEXT NOT NULL,
                    generated_email TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    @staticmethod
    def _row_to_application(row: sqlite3.Row) -> ApplicationRecord:
        return ApplicationRecord(
            id=row["id"],
            selected_job=Job(**json.loads(row["selected_job"])),
            generated_email=GeneratedEmail(**json.loads(row["generated_email"])),
            score=row["score"],
            status=row["status"],
            created_at=row["created_at"],
        )

    def create_application(
        self,
        selected_job: dict[str, Any],
        generated_email: dict[str, Any],
        score: int,
        status: str = "pending",
    ) -> dict[str, Any]:

        try:
            application = ApplicationCreate(
                selected_job=Job(**selected_job),
                generated_email=GeneratedEmail(**generated_email),
                score=score,
                status=status,
            )
            created_at = datetime.now(timezone.utc).isoformat()

            with self._connect() as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO applications (
                        selected_job,
                        generated_email,
                        score,
                        status,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        application.selected_job.model_dump_json(),
                        application.generated_email.model_dump_json(),
                        application.score,
                        application.status,
                        created_at,
                    ),
                )
                application_id = cursor.lastrowid

                row = connection.execute(
                    """
                    SELECT *
                    FROM applications
                    WHERE id = ?
                    """,
                    (application_id,),
                ).fetchone()

            return {
                "success": True,
                "data": ApplicationStoreResponse(
                    application=self._row_to_application(row)
                ).model_dump()
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }

    def get_application(self, application_id: int) -> dict[str, Any]:

        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT *
                    FROM applications
                    WHERE id = ?
                    """,
                    (application_id,),
                ).fetchone()

            if row is None:
                return {
                    "success": False,
                    "error": f"Application not found: {application_id}"
                }

            return {
                "success": True,
                "data": ApplicationStoreResponse(
                    application=self._row_to_application(row)
                ).model_dump()
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }

    def list_applications(self) -> dict[str, Any]:

        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT *
                    FROM applications
                    ORDER BY created_at DESC, id DESC
                    """
                ).fetchall()

            applications = [
                self._row_to_application(row)
                for row in rows
            ]

            return {
                "success": True,
                "data": ApplicationListResponse(
                    applications=applications
                ).model_dump()
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }

    def update_application_status(
        self,
        application_id: int,
        status: str,
    ) -> dict[str, Any]:

        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    """
                    UPDATE applications
                    SET status = ?
                    WHERE id = ?
                    """,
                    (status, application_id),
                )

                if cursor.rowcount == 0:
                    return {
                        "success": False,
                        "error": f"Application not found: {application_id}"
                    }

                row = connection.execute(
                    """
                    SELECT *
                    FROM applications
                    WHERE id = ?
                    """,
                    (application_id,),
                ).fetchone()

            return {
                "success": True,
                "data": ApplicationStoreResponse(
                    application=self._row_to_application(row)
                ).model_dump()
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }

    def delete_application(self, application_id: int) -> dict[str, Any]:

        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    """
                    DELETE FROM applications
                    WHERE id = ?
                    """,
                    (application_id,),
                )

            if cursor.rowcount == 0:
                return {
                    "success": False,
                    "error": f"Application not found: {application_id}"
                }

            return {
                "success": True,
                "data": {
                    "deleted": True,
                    "application_id": application_id
                }
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }
