"""
db.py  —  SQLite persistence layer for the Student Information System
All reads/writes go through this module; the Dashboard imports it instead
of managing raw lists.
"""

import sqlite3
import hashlib
from pathlib import Path


DB = "students.db"


# ── Schema ────────────────────────────────────────────────────────────────────

def init():
    """Create all tables if they don't exist yet."""
    con = sqlite3.connect(DB)
    con.executescript("""
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS users (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT    UNIQUE NOT NULL,
            password  TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS students (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  TEXT    UNIQUE NOT NULL,
            last_name   TEXT    NOT NULL,
            first_name  TEXT    NOT NULL,
            name        TEXT    NOT NULL,
            course      TEXT    NOT NULL,
            year_level  TEXT    NOT NULL,
            status      TEXT    NOT NULL DEFAULT 'Regular',
            section     TEXT    DEFAULT '',
            email       TEXT    DEFAULT '',
            contact     TEXT    DEFAULT '',
            address     TEXT    DEFAULT '',
            g_math      TEXT    DEFAULT '0.00',
            g_sci       TEXT    DEFAULT '0.00',
            g_eng       TEXT    DEFAULT '0.00',
            g_prog      TEXT    DEFAULT '0.00',
            date_added  TEXT    DEFAULT CURRENT_DATE
        );

        CREATE TABLE IF NOT EXISTS courses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            code        TEXT    UNIQUE NOT NULL,
            name        TEXT    NOT NULL,
            instructor  TEXT    NOT NULL,
            units       INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS activity_log (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            action     TEXT NOT NULL,
            timestamp  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS login_log (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL,
            status     TEXT NOT NULL,
            logged_at  TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    con.commit()
    con.close()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def _rows(con, sql, params=()):
    """Return list of dicts for a SELECT."""
    con.row_factory = sqlite3.Row
    rows = con.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


# ── Users / Auth ──────────────────────────────────────────────────────────────

def user_exists(username: str) -> bool:
    with sqlite3.connect(DB) as con:
        return con.execute(
            "SELECT 1 FROM users WHERE username=?", (username,)
        ).fetchone() is not None


def register_user(username: str, password: str) -> bool:
    """Returns True on success, False if username already taken."""
    try:
        with sqlite3.connect(DB) as con:
            con.execute(
                "INSERT INTO users (username, password) VALUES (?,?)",
                (username, _hash(password))
            )
        return True
    except sqlite3.IntegrityError:
        return False


def verify_login(username: str, password: str) -> bool:
    with sqlite3.connect(DB) as con:
        row = con.execute(
            "SELECT password FROM users WHERE username=?", (username,)
        ).fetchone()
    ok = row is not None and row[0] == _hash(password)
    with sqlite3.connect(DB) as con:
        con.execute(
            "INSERT INTO login_log (username, status) VALUES (?,?)",
            (username, "SUCCESS" if ok else "FAILED")
        )
    return ok


def get_all_users() -> dict[str, str]:
    """Return {username: hashed_password} — used by the Dashboard users dict."""
    with sqlite3.connect(DB) as con:
        rows = con.execute("SELECT username, password FROM users").fetchall()
    return {r[0]: r[1] for r in rows}


def update_credentials(old_username: str, new_username: str,
                        new_password: str | None = None):
    """Rename user and/or change password."""
    with sqlite3.connect(DB) as con:
        if new_password:
            con.execute(
                "UPDATE users SET username=?, password=? WHERE username=?",
                (new_username, _hash(new_password), old_username)
            )
        else:
            con.execute(
                "UPDATE users SET username=? WHERE username=?",
                (new_username, old_username)
            )


# ── Students ──────────────────────────────────────────────────────────────────

STUDENT_COLS = (
    "student_id", "last_name", "first_name", "name",
    "course", "year_level", "status", "section",
    "email", "contact", "address",
    "g_math", "g_sci", "g_eng", "g_prog", "date_added"
)


def load_students() -> list[dict]:
    with sqlite3.connect(DB) as con:
        return _rows(con, "SELECT * FROM students ORDER BY id")


def add_student(rec: dict):
    with sqlite3.connect(DB) as con:
        con.execute(f"""
            INSERT INTO students
                ({', '.join(STUDENT_COLS)})
            VALUES
                ({', '.join('?' for _ in STUDENT_COLS)})
        """, tuple(rec.get(c, "") for c in STUDENT_COLS))


def update_student(student_id: str, rec: dict):
    sets = ", ".join(f"{c}=?" for c in STUDENT_COLS if c != "student_id")
    vals = [rec.get(c, "") for c in STUDENT_COLS if c != "student_id"]
    vals.append(student_id)
    with sqlite3.connect(DB) as con:
        con.execute(f"UPDATE students SET {sets} WHERE student_id=?", vals)


def delete_student(student_id: str):
    with sqlite3.connect(DB) as con:
        con.execute("DELETE FROM students WHERE student_id=?", (student_id,))


def student_id_taken(student_id: str, exclude_id: str | None = None) -> bool:
    with sqlite3.connect(DB) as con:
        if exclude_id:
            row = con.execute(
                "SELECT 1 FROM students WHERE student_id=? AND student_id!=?",
                (student_id, exclude_id)
            ).fetchone()
        else:
            row = con.execute(
                "SELECT 1 FROM students WHERE student_id=?", (student_id,)
            ).fetchone()
    return row is not None


# ── Courses ───────────────────────────────────────────────────────────────────

DEFAULT_COURSES = [
    ("BSIT",   "BS Information Technology",   "Prof. Reyes",     180),
    ("BSCE",   "BS Civil Engineering",         "Prof. Dela Cruz", 192),
    ("BSEd",   "BS Education",                 "Prof. Garcia",    156),
    ("BSBA",   "BS Business Administration",   "Prof. Torres",    168),
    ("BSEE",   "BS Electrical Engineering",    "Prof. Mendoza",   192),
]



def seed_courses():
    """Insert default courses only if the table is empty."""
    with sqlite3.connect(DB) as con:
        if con.execute("SELECT COUNT(*) FROM courses").fetchone()[0] == 0:
            con.executemany(
                "INSERT OR IGNORE INTO courses (code,name,instructor,units) VALUES (?,?,?,?)",
                DEFAULT_COURSES
            )


def load_courses() -> list[dict]:
    with sqlite3.connect(DB) as con:
        return _rows(con, "SELECT * FROM courses ORDER BY code")


def add_course(rec: dict):
    with sqlite3.connect(DB) as con:
        con.execute(
            "INSERT INTO courses (code,name,instructor,units) VALUES (?,?,?,?)",
            (rec["code"], rec["name"], rec["instructor"], rec["units"])
        )


def update_course(old_code: str, rec: dict):
    with sqlite3.connect(DB) as con:
        con.execute(
            "UPDATE courses SET code=?,name=?,instructor=?,units=? WHERE code=?",
            (rec["code"], rec["name"], rec["instructor"], rec["units"], old_code)
        )


def delete_course(code: str):
    with sqlite3.connect(DB) as con:
        con.execute("DELETE FROM courses WHERE code=?", (code,))


def course_code_taken(code: str, exclude_code: str | None = None) -> bool:
    with sqlite3.connect(DB) as con:
        if exclude_code:
            row = con.execute(
                "SELECT 1 FROM courses WHERE code=? AND code!=?",
                (code, exclude_code)
            ).fetchone()
        else:
            row = con.execute(
                "SELECT 1 FROM courses WHERE code=?", (code,)
            ).fetchone()
    return row is not None


# ── Activity log ──────────────────────────────────────────────────────────────

def log_action(action: str, timestamp: str):
    with sqlite3.connect(DB) as con:
        con.execute(
            "INSERT INTO activity_log (action, timestamp) VALUES (?,?)",
            (action, timestamp)
        )


def load_activity_log(limit: int = 300) -> list[dict]:
    with sqlite3.connect(DB) as con:
        return _rows(
            con,
            "SELECT action, timestamp FROM activity_log ORDER BY id DESC LIMIT ?",
            (limit,)
        )


def clear_activity_log():
    with sqlite3.connect(DB) as con:
        con.execute("DELETE FROM activity_log")
