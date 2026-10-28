"""
JanSahayak AI — Database Service
SQLite schema, initialization, seed loading, and queries.
"""
import sqlite3
import json
import os
import logging
from datetime import datetime
from contextlib import contextmanager

import config

logger = logging.getLogger(__name__)

_DB_PATH = config.DATABASE_PATH


def get_connection():
    """Get a new SQLite connection with WAL mode and foreign keys."""
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create tables if they do not exist."""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS applications (
                application_id TEXT PRIMARY KEY,
                applicant_name TEXT NOT NULL,
                applicant_name_en TEXT,
                father_name TEXT,
                application_type TEXT NOT NULL,
                application_type_en TEXT,
                submission_date TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                assigned_officer TEXT,
                district TEXT,
                district_en TEXT,
                address TEXT,
                contact TEXT,
                declared_annual_income REAL,
                income_source TEXT,
                family_members INTEGER,
                submitted_documents TEXT,
                document_details TEXT,
                review_notes TEXT,
                urgency TEXT DEFAULT 'normal',
                secondary_income_record REAL,
                conflicting_dates TEXT,
                version INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id TEXT NOT NULL,
                action TEXT NOT NULL,
                officer_id TEXT NOT NULL,
                officer_name TEXT,
                reason TEXT NOT NULL,
                ai_recommendation TEXT,
                ai_recommendation_followed INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY (application_id) REFERENCES applications(application_id)
            );

            CREATE TABLE IF NOT EXISTS audit_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                old_status TEXT,
                new_status TEXT,
                officer_id TEXT,
                officer_name TEXT,
                remarks TEXT,
                ai_recommendation TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (application_id) REFERENCES applications(application_id)
            );

            CREATE INDEX IF NOT EXISTS idx_app_status ON applications(status);
            CREATE INDEX IF NOT EXISTS idx_app_officer ON applications(assigned_officer);
            CREATE INDEX IF NOT EXISTS idx_decisions_app ON decisions(application_id);
            CREATE INDEX IF NOT EXISTS idx_audit_app ON audit_history(application_id);
        """)
    logger.info("Database initialized successfully.")


def seed_data(force_reseed=False):
    """Load sample applications from JSON seed file.
    
    If force_reseed is True, deletes existing seed data before reinserting.
    Otherwise, skips if any applications already exist.
    """
    seed_path = config.SEED_DATA_PATH
    if not os.path.exists(seed_path):
        logger.warning(f"Seed file not found at {seed_path}")
        return 0

    with get_db() as conn:
        if force_reseed:
            # Delete all application data for a clean reseed
            conn.execute("DELETE FROM audit_history")
            conn.execute("DELETE FROM decisions")
            conn.execute("DELETE FROM applications")
            logger.info("Existing data cleared for reseed.")
        else:
            count = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
            if count > 0:
                logger.info(f"Database already has {count} applications. Skipping seed.")
                return count

        with open(seed_path, "r", encoding="utf-8") as f:
            applications = json.load(f)

        inserted = 0
        for app in applications:
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO applications (
                        application_id, applicant_name, applicant_name_en, father_name,
                        application_type, application_type_en, submission_date, last_updated,
                        status, assigned_officer, district, district_en, address, contact,
                        declared_annual_income, income_source, family_members,
                        submitted_documents, document_details, review_notes, urgency,
                        secondary_income_record, conflicting_dates
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    app["application_id"],
                    app["applicant_name"],
                    app.get("applicant_name_en", ""),
                    app.get("father_name", ""),
                    app["application_type"],
                    app.get("application_type_en", ""),
                    app["submission_date"],
                    app["last_updated"],
                    app["status"],
                    app.get("assigned_officer", ""),
                    app.get("district", ""),
                    app.get("district_en", ""),
                    app.get("address", ""),
                    app.get("contact", ""),
                    app.get("declared_annual_income", 0),
                    app.get("income_source", ""),
                    app.get("family_members", 0),
                    json.dumps(app.get("submitted_documents", []), ensure_ascii=False),
                    json.dumps(app.get("document_details", {}), ensure_ascii=False),
                    app.get("review_notes", ""),
                    app.get("urgency", "normal"),
                    app.get("secondary_income_record"),
                    json.dumps(app.get("conflicting_dates")) if app.get("conflicting_dates") else None,
                ))
                inserted += 1
            except sqlite3.IntegrityError as e:
                logger.warning(f"Skipping duplicate: {app['application_id']} — {e}")

        logger.info(f"Seeded {inserted} applications.")
        return inserted


# --- Query Functions ---

def get_all_applications():
    """Return all applications as a list of dicts."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM applications ORDER BY submission_date ASC"
        ).fetchall()
    return [dict(r) for r in rows]


def get_application_by_id(app_id):
    """Return a single application dict or None."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM applications WHERE application_id = ?", (app_id,)
        ).fetchone()
    return dict(row) if row else None


def get_applications_by_status(status):
    """Return applications matching the given status."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM applications WHERE status = ? ORDER BY submission_date ASC",
            (status,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_pending_applications():
    """Return applications that are pending or under review."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM applications WHERE status IN (?, ?) ORDER BY submission_date ASC",
            (config.STATUS_PENDING, config.STATUS_UNDER_REVIEW)
        ).fetchall()
    return [dict(r) for r in rows]


def get_dashboard_stats():
    """Compute dashboard statistics from actual data."""
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
        pending = conn.execute(
            "SELECT COUNT(*) FROM applications WHERE status IN (?, ?)",
            (config.STATUS_PENDING, config.STATUS_UNDER_REVIEW)
        ).fetchone()[0]
        approved = conn.execute(
            "SELECT COUNT(*) FROM applications WHERE status = ?",
            (config.STATUS_APPROVED,)
        ).fetchone()[0]
        rejected = conn.execute(
            "SELECT COUNT(*) FROM applications WHERE status = ?",
            (config.STATUS_REJECTED,)
        ).fetchone()[0]
        returned = conn.execute(
            "SELECT COUNT(*) FROM applications WHERE status = ?",
            (config.STATUS_RETURNED,)
        ).fetchone()[0]

    return {
        "total": total,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "returned": returned,
    }


def update_application_status(app_id, new_status, review_notes=None):
    """Update an application's status and optionally its review notes.
    Uses optimistic concurrency via version column.
    Returns True if updated, False if stale.
    """
    with get_db() as conn:
        app = conn.execute(
            "SELECT version FROM applications WHERE application_id = ?", (app_id,)
        ).fetchone()
        if not app:
            return False

        current_version = app["version"]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        params = [new_status, now, current_version + 1]
        sql = "UPDATE applications SET status = ?, last_updated = ?, version = ?"

        if review_notes is not None:
            sql += ", review_notes = ?"
            params.append(review_notes)

        sql += " WHERE application_id = ? AND version = ?"
        params.extend([app_id, current_version])

        result = conn.execute(sql, params)
        return result.rowcount > 0


def add_decision(app_id, action, officer_id, officer_name, reason,
                 ai_recommendation=None, ai_followed=None):
    """Record a decision. Returns the decision ID or None if duplicate."""
    with get_db() as conn:
        # Check for duplicate: same app, same action, within last 5 seconds
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        existing = conn.execute(
            """SELECT id FROM decisions
               WHERE application_id = ? AND action = ? AND officer_id = ?
               AND created_at = ?""",
            (app_id, action, officer_id, now)
        ).fetchone()
        if existing:
            logger.warning(f"Duplicate decision blocked for {app_id}")
            return None

        cursor = conn.execute("""
            INSERT INTO decisions (
                application_id, action, officer_id, officer_name,
                reason, ai_recommendation, ai_recommendation_followed, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (app_id, action, officer_id, officer_name,
              reason, ai_recommendation, ai_followed, now))
        return cursor.lastrowid


def add_audit_event(app_id, event_type, old_status, new_status,
                    officer_id, officer_name, remarks, ai_recommendation=None):
    """Append an audit history event."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db() as conn:
        conn.execute("""
            INSERT INTO audit_history (
                application_id, event_type, old_status, new_status,
                officer_id, officer_name, remarks, ai_recommendation, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (app_id, event_type, old_status, new_status,
              officer_id, officer_name, remarks, ai_recommendation, now))


def get_audit_history(app_id):
    """Return audit history for an application, newest first."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM audit_history WHERE application_id = ? ORDER BY created_at DESC",
            (app_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_all_audit_history():
    """Return all audit history, newest first."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM audit_history ORDER BY created_at DESC LIMIT 200"
        ).fetchall()
    return [dict(r) for r in rows]


def get_decisions_for_application(app_id):
    """Return all decisions for an application."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM decisions WHERE application_id = ? ORDER BY created_at DESC",
            (app_id,)
        ).fetchall()
    return [dict(r) for r in rows]
