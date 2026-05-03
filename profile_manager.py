"""
Profile Manager Module
Handles profile CRUD operations with SQLite storage.
Supports search by profile name or number.
"""

import os
import json
import sqlite3
import time
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from fingerprint_generator import generate_fingerprint


# ══════════════════════════════════════════════════════════════
#  Database Schema
# ══════════════════════════════════════════════════════════════

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_number INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    mode TEXT NOT NULL DEFAULT 'desktop',
    fingerprint_seed TEXT NOT NULL,
    fingerprint_data TEXT NOT NULL,
    proxy TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    status TEXT DEFAULT 'stopped',
    last_launched TEXT DEFAULT '',
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_profiles_name ON profiles(name);
CREATE INDEX IF NOT EXISTS idx_profiles_number ON profiles(profile_number);
CREATE INDEX IF NOT EXISTS idx_profiles_status ON profiles(status);
"""


class ProfileManager:
    """Manages browser profiles with SQLite persistence."""

    def __init__(self, db_path: Optional[str] = None, profiles_dir: Optional[str] = None):
        if db_path is None:
            app_dir = self._get_app_dir()
            db_path = os.path.join(app_dir, "profiles.db")

        if profiles_dir is None:
            app_dir = self._get_app_dir()
            profiles_dir = os.path.join(app_dir, "browser_profiles")

        self.db_path = db_path
        self.profiles_dir = profiles_dir
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        os.makedirs(profiles_dir, exist_ok=True)

        self._init_db()

    @staticmethod
    def _get_app_dir() -> str:
        """Get application data directory."""
        if os.name == "nt":
            base = os.environ.get("APPDATA", os.path.expanduser("~"))
        else:
            base = os.path.expanduser("~")
        app_dir = os.path.join(base, ".xonomo_browser")
        os.makedirs(app_dir, exist_ok=True)
        return app_dir

    def _init_db(self):
        """Initialize database and create tables."""
        conn = sqlite3.connect(self.db_path)
        conn.executescript(CREATE_TABLE_SQL)
        conn.commit()
        conn.close()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _next_profile_number(self) -> int:
        """Get the next available profile number."""
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT MAX(profile_number) as max_num FROM profiles"
            ).fetchone()
            return (row["max_num"] or 0) + 1
        finally:
            conn.close()

    # ── CRUD ──────────────────────────────────────────────

    def create_profile(self, name: str, mode: str = "desktop",
                       proxy: str = "", notes: str = "",
                       seed: Optional[str] = None) -> Dict[str, Any]:
        """Create a new browser profile."""
        fp = generate_fingerprint(seed=seed, mode=mode)
        profile_number = self._next_profile_number()
        now = time.time()

        profile_dir = os.path.join(self.profiles_dir, f"profile_{profile_number}")
        os.makedirs(profile_dir, exist_ok=True)

        conn = self._get_conn()
        try:
            conn.execute(
                """INSERT INTO profiles
                   (profile_number, name, mode, fingerprint_seed, fingerprint_data,
                    proxy, notes, status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 'stopped', ?, ?)""",
                (profile_number, name, mode, fp["seed"],
                 json.dumps(fp), proxy, notes, now, now)
            )
            conn.commit()

            profile_id = conn.execute(
                "SELECT id FROM profiles WHERE profile_number = ?",
                (profile_number,)
            ).fetchone()["id"]

            return {
                "id": profile_id,
                "profile_number": profile_number,
                "name": name,
                "mode": mode,
                "fingerprint_seed": fp["seed"],
                "proxy": proxy,
                "notes": notes,
                "status": "stopped",
                "profile_dir": profile_dir,
                "created_at": now,
            }
        finally:
            conn.close()

    def get_profile(self, profile_id: int) -> Optional[Dict[str, Any]]:
        """Get a profile by database ID."""
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM profiles WHERE id = ?", (profile_id,)
            ).fetchone()
            if row:
                return self._row_to_dict(row)
            return None
        finally:
            conn.close()

    def get_profile_by_number(self, number: int) -> Optional[Dict[str, Any]]:
        """Get a profile by its profile number."""
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM profiles WHERE profile_number = ?", (number,)
            ).fetchone()
            if row:
                return self._row_to_dict(row)
            return None
        finally:
            conn.close()

    def get_all_profiles(self) -> List[Dict[str, Any]]:
        """Get all profiles ordered by profile number."""
        conn = self._get_conn()
        try:
            rows = conn.execute(
                "SELECT * FROM profiles ORDER BY profile_number ASC"
            ).fetchall()
            return [self._row_to_dict(r) for r in rows]
        finally:
            conn.close()

    def update_profile(self, profile_id: int, **kwargs) -> bool:
        """Update profile fields."""
        allowed_fields = {"name", "mode", "proxy", "notes", "status", "last_launched"}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False

        updates["updated_at"] = time.time()

        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [profile_id]

        conn = self._get_conn()
        try:
            conn.execute(
                f"UPDATE profiles SET {set_clause} WHERE id = ?",
                values
            )
            conn.commit()
            return conn.total_changes > 0
        finally:
            conn.close()

    def delete_profile(self, profile_id: int) -> bool:
        """Delete a profile and its browser data."""
        profile = self.get_profile(profile_id)
        if not profile:
            return False

        profile_dir = os.path.join(
            self.profiles_dir,
            f"profile_{profile['profile_number']}"
        )
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir, ignore_errors=True)

        conn = self._get_conn()
        try:
            conn.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
            conn.commit()
            return True
        finally:
            conn.close()

    # ── Search ────────────────────────────────────────────

    def search_profiles(self, query: str) -> List[Dict[str, Any]]:
        """
        Search profiles by name or profile number.
        If query is numeric, searches by profile number.
        Otherwise searches by name (case-insensitive partial match).
        """
        conn = self._get_conn()
        try:
            if query.strip().isdigit():
                number = int(query.strip())
                rows = conn.execute(
                    "SELECT * FROM profiles WHERE profile_number = ? "
                    "ORDER BY profile_number ASC",
                    (number,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM profiles WHERE name LIKE ? "
                    "ORDER BY profile_number ASC",
                    (f"%{query}%",)
                ).fetchall()
            return [self._row_to_dict(r) for r in rows]
        finally:
            conn.close()

    def get_profile_count(self) -> int:
        """Get total number of profiles."""
        conn = self._get_conn()
        try:
            row = conn.execute("SELECT COUNT(*) as cnt FROM profiles").fetchone()
            return row["cnt"]
        finally:
            conn.close()

    def get_running_profiles(self) -> List[Dict[str, Any]]:
        """Get all currently running profiles."""
        conn = self._get_conn()
        try:
            rows = conn.execute(
                "SELECT * FROM profiles WHERE status = 'running' "
                "ORDER BY profile_number ASC"
            ).fetchall()
            return [self._row_to_dict(r) for r in rows]
        finally:
            conn.close()

    def set_profile_status(self, profile_id: int, status: str):
        """Update profile running status."""
        self.update_profile(profile_id, status=status)

    def get_profile_dir(self, profile_number: int) -> str:
        """Get the browser profile directory path."""
        return os.path.join(self.profiles_dir, f"profile_{profile_number}")

    def regenerate_fingerprint(self, profile_id: int,
                               seed: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Regenerate fingerprint for a profile."""
        profile = self.get_profile(profile_id)
        if not profile:
            return None

        fp = generate_fingerprint(seed=seed, mode=profile["mode"])

        conn = self._get_conn()
        try:
            conn.execute(
                """UPDATE profiles
                   SET fingerprint_seed = ?, fingerprint_data = ?, updated_at = ?
                   WHERE id = ?""",
                (fp["seed"], json.dumps(fp), time.time(), profile_id)
            )
            conn.commit()
            return fp
        finally:
            conn.close()

    # ── Helper ────────────────────────────────────────────

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        """Convert a database row to a dictionary."""
        d = dict(row)
        if "fingerprint_data" in d and isinstance(d["fingerprint_data"], str):
            try:
                d["fingerprint_data"] = json.loads(d["fingerprint_data"])
            except json.JSONDecodeError:
                pass
        return d

    def export_profile(self, profile_id: int, export_path: str) -> bool:
        """Export a profile to a JSON file."""
        profile = self.get_profile(profile_id)
        if not profile:
            return False

        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2, ensure_ascii=False, default=str)
        return True

    def import_profile(self, import_path: str) -> Optional[Dict[str, Any]]:
        """Import a profile from a JSON file."""
        with open(import_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return self.create_profile(
            name=data.get("name", "Imported Profile"),
            mode=data.get("mode", "desktop"),
            proxy=data.get("proxy", ""),
            notes=data.get("notes", ""),
            seed=data.get("fingerprint_seed"),
        )
