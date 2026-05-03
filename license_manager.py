"""
License Manager Module
Handles admin approval, expiry date, and hardware-locked licensing.
Prevents profile creation/run if license is invalid.
"""

import os
import json
import hashlib
import platform
import subprocess
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Tuple


class HardwareID:
    """Generates a unique hardware identifier for the current machine."""

    @staticmethod
    def get_machine_id() -> str:
        """Get a unique machine identifier."""
        parts = []

        # CPU info
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["wmic", "cpu", "get", "ProcessorId"],
                    capture_output=True, text=True, timeout=5
                )
                cpu_id = result.stdout.strip().split("\n")[-1].strip()
                parts.append(cpu_id)
            elif platform.system() == "Linux":
                with open("/etc/machine-id", "r") as f:
                    parts.append(f.read().strip())
            elif platform.system() == "Darwin":
                result = subprocess.run(
                    ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                    capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.split("\n"):
                    if "IOPlatformUUID" in line:
                        parts.append(line.split('"')[-2])
                        break
        except Exception:
            pass

        # Motherboard / system UUID
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["wmic", "baseboard", "get", "SerialNumber"],
                    capture_output=True, text=True, timeout=5
                )
                mb_serial = result.stdout.strip().split("\n")[-1].strip()
                if mb_serial and mb_serial != "To Be Filled By O.E.M.":
                    parts.append(mb_serial)
        except Exception:
            pass

        # Disk serial
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["wmic", "diskdrive", "get", "SerialNumber"],
                    capture_output=True, text=True, timeout=5
                )
                disk_serial = result.stdout.strip().split("\n")[-1].strip()
                if disk_serial:
                    parts.append(disk_serial)
        except Exception:
            pass

        # Fallback
        if not parts:
            parts.append(platform.node())
            parts.append(str(uuid.getnode()))

        combined = "|".join(parts)
        return hashlib.sha256(combined.encode()).hexdigest()[:32]


class LicenseManager:
    """
    Manages software licensing with:
    - Admin approval check
    - Expiry date enforcement
    - Hardware-locked single-machine licensing
    """

    # Default admin API endpoint (configure for your server)
    DEFAULT_API_URL = "https://api.xonomo.site/license"

    def __init__(self, license_file: Optional[str] = None,
                 api_url: Optional[str] = None):
        if license_file is None:
            app_dir = self._get_app_dir()
            license_file = os.path.join(app_dir, "license.json")

        self.license_file = license_file
        self.api_url = api_url or self.DEFAULT_API_URL
        self.hardware_id = HardwareID.get_machine_id()
        self._license_data = self._load_license()

    @staticmethod
    def _get_app_dir() -> str:
        if os.name == "nt":
            base = os.environ.get("APPDATA", os.path.expanduser("~"))
        else:
            base = os.path.expanduser("~")
        app_dir = os.path.join(base, ".xonomo_browser")
        os.makedirs(app_dir, exist_ok=True)
        return app_dir

    def _load_license(self) -> Dict[str, Any]:
        """Load license data from file."""
        if os.path.exists(self.license_file):
            try:
                with open(self.license_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def _save_license(self, data: Dict[str, Any]):
        """Save license data to file."""
        os.makedirs(os.path.dirname(self.license_file), exist_ok=True)
        with open(self.license_file, "w") as f:
            json.dump(data, f, indent=2)
        self._license_data = data

    # ── License Activation ────────────────────────────────

    def activate_license(self, license_key: str) -> Dict[str, Any]:
        """
        Activate a license key.
        In production, this would call the admin API.
        For offline use, validates the key format and stores locally.
        """
        result = self._validate_with_server(license_key)

        if result.get("success"):
            license_data = {
                "license_key": license_key,
                "hardware_id": self.hardware_id,
                "activated_at": time.time(),
                "expiry_date": result.get("expiry_date", ""),
                "approved": result.get("approved", False),
                "max_profiles": result.get("max_profiles", 10),
                "user_name": result.get("user_name", ""),
                "user_email": result.get("user_email", ""),
                "last_verified": time.time(),
            }
            self._save_license(license_data)
            return {"success": True, "message": "License activated successfully", "data": license_data}

        return result

    def _validate_with_server(self, license_key: str) -> Dict[str, Any]:
        """
        Validate license key with the admin server.
        Falls back to offline validation if server unreachable.
        """
        try:
            import urllib.request

            payload = json.dumps({
                "license_key": license_key,
                "hardware_id": self.hardware_id,
                "platform": platform.system(),
                "machine_name": platform.node(),
            }).encode()

            req = urllib.request.Request(
                f"{self.api_url}/activate",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            resp = urllib.request.urlopen(req, timeout=10)
            return json.loads(resp.read().decode())

        except Exception:
            # Offline validation fallback
            return self._offline_validate(license_key)

    def _offline_validate(self, license_key: str) -> Dict[str, Any]:
        """
        Offline license validation.
        Accepts keys in format: XONOMO-XXXXX-XXXXX-XXXXX
        For demo/development purposes.
        """
        if not license_key or len(license_key) < 10:
            return {"success": False, "error": "Invalid license key format"}

        parts = license_key.split("-")
        if len(parts) != 4 or parts[0] != "XONOMO":
            return {"success": False, "error": "Invalid license key format. Expected: XONOMO-XXXXX-XXXXX-XXXXX"}

        # Generate a 30-day expiry for offline activation
        expiry = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        return {
            "success": True,
            "approved": True,
            "expiry_date": expiry,
            "max_profiles": 50,
            "user_name": "Offline User",
            "offline_mode": True,
        }

    # ── License Checks ────────────────────────────────────

    def is_licensed(self) -> Tuple[bool, str]:
        """
        Check if the current machine has a valid license.
        Returns (is_valid, reason_if_invalid).
        """
        if not self._license_data:
            return False, "No license found. Please activate a license key."

        # Check 1: Admin approval
        if not self._license_data.get("approved", False):
            return False, "License not approved by admin. Contact administrator."

        # Check 2: Expiry date
        expiry_str = self._license_data.get("expiry_date", "")
        if expiry_str:
            try:
                expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
                if datetime.now() > expiry_date:
                    return False, f"License expired on {expiry_str}. Please renew."
            except ValueError:
                pass

        # Check 3: Hardware ID match
        stored_hw_id = self._license_data.get("hardware_id", "")
        if stored_hw_id and stored_hw_id != self.hardware_id:
            return False, (
                "License is registered to a different computer. "
                "Please contact administrator to transfer license."
            )

        return True, "License valid"

    def can_create_profile(self) -> Tuple[bool, str]:
        """Check if user can create a new profile."""
        valid, reason = self.is_licensed()
        if not valid:
            return False, reason

        max_profiles = self._license_data.get("max_profiles", 10)
        return True, f"Can create profiles (max: {max_profiles})"

    def can_run_profile(self) -> Tuple[bool, str]:
        """Check if user can run/launch a profile."""
        return self.is_licensed()

    def get_license_info(self) -> Dict[str, Any]:
        """Get current license information."""
        if not self._license_data:
            return {
                "status": "unlicensed",
                "hardware_id": self.hardware_id,
            }

        valid, reason = self.is_licensed()

        return {
            "status": "valid" if valid else "invalid",
            "reason": reason,
            "license_key": self._license_data.get("license_key", "")[:10] + "...",
            "hardware_id": self.hardware_id,
            "stored_hardware_id": self._license_data.get("hardware_id", ""),
            "hardware_match": self.hardware_id == self._license_data.get("hardware_id", ""),
            "approved": self._license_data.get("approved", False),
            "expiry_date": self._license_data.get("expiry_date", ""),
            "max_profiles": self._license_data.get("max_profiles", 0),
            "user_name": self._license_data.get("user_name", ""),
            "activated_at": self._license_data.get("activated_at", 0),
        }

    def deactivate(self):
        """Deactivate current license."""
        if os.path.exists(self.license_file):
            os.remove(self.license_file)
        self._license_data = {}

    # ── Server Sync ───────────────────────────────────────

    def verify_with_server(self) -> Dict[str, Any]:
        """
        Periodically verify license with admin server.
        Call this on app startup and periodically.
        """
        if not self._license_data:
            return {"valid": False, "reason": "No license"}

        license_key = self._license_data.get("license_key", "")

        try:
            import urllib.request

            payload = json.dumps({
                "license_key": license_key,
                "hardware_id": self.hardware_id,
                "action": "verify",
            }).encode()

            req = urllib.request.Request(
                f"{self.api_url}/verify",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            resp = urllib.request.urlopen(req, timeout=10)
            result = json.loads(resp.read().decode())

            if result.get("success"):
                self._license_data["approved"] = result.get("approved", False)
                self._license_data["expiry_date"] = result.get("expiry_date", "")
                self._license_data["max_profiles"] = result.get("max_profiles", 10)
                self._license_data["last_verified"] = time.time()
                self._save_license(self._license_data)

            return result

        except Exception as e:
            # Offline — use cached data
            last_verified = self._license_data.get("last_verified", 0)
            days_since = (time.time() - last_verified) / 86400

            if days_since > 7:
                return {
                    "valid": False,
                    "reason": "Cannot verify license. No server connection for 7+ days."
                }

            return {"valid": True, "reason": "Using cached verification", "offline": True}
