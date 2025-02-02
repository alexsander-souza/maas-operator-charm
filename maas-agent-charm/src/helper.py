# Copyright 2024 Canonical
# See LICENSE file for licensing details.

"""Helper functions for MAAS management."""

import subprocess
from pathlib import Path

from charms.operator_libs_linux.v2.snap import SnapCache, SnapState

MAAS_SNAP_NAME = "maas"
MAAS_SECRET = Path("/var/snap/maas/common/maas/secret")
MAAS_ID = Path("/var/snap/maas/common/maas/maas_id")
MAAS_SERVICE = "pebble"


def _run_local(*args, **kwargs) -> int:
    """Run process in the unit environment.

    Returns:
        int: process exit status
    """
    return subprocess.Popen(*args, **kwargs).wait()


class MaasHelper:
    """MAAS helper."""

    @staticmethod
    def install(channel: str) -> None:
        """Install snap.

        Args:
            channel (str): snapstore channel
        """
        maas = SnapCache()[MAAS_SNAP_NAME]
        if not maas.present:
            maas.ensure(SnapState.Latest, channel=channel)
            maas.hold()

    @staticmethod
    def uninstall() -> None:
        """Uninstall snap."""
        maas = SnapCache()[MAAS_SNAP_NAME]
        if maas.present:
            maas.ensure(SnapState.Absent)

    @staticmethod
    def get_installed_version() -> str | None:
        """Get installed version.

        Returns:
            str | None: version if installed
        """
        maas = SnapCache()[MAAS_SNAP_NAME]
        return maas.revision if maas.present else None

    @staticmethod
    def get_installed_channel() -> str | None:
        """Get installed channel.

        Returns:
            str | None: channel if installed
        """
        maas = SnapCache()[MAAS_SNAP_NAME]
        return maas.channel if maas.present else None

    @staticmethod
    def is_running() -> bool:
        """Check if MAAS is running.

        Returns:
            boot: whether the service is running
        """
        maas = SnapCache()[MAAS_SNAP_NAME]
        service = maas.services.get(MAAS_SERVICE, {})
        return service.get("activate", False)

    @staticmethod
    def set_running(enable: bool) -> None:
        """Set service status.

        Args:
            enable (bool): enable service
        """
        maas = SnapCache()[MAAS_SNAP_NAME]
        if enable:
            maas.start()
        else:
            maas.stop()

    @staticmethod
    def setup_rack(maas_url: str, secret: str) -> bool:
        """Initialize a Rack/Agent controller.

        Args:
            maas_url (str):  URL that MAAS should use for communicate from the
                nodes to MAAS and other controllers of MAAS.
            secret (str): Enrollement token

        Returns:
            bool: whether the initialisation succeeded
        """
        cmd = [
            "/snap/bin/maas",
            "init",
            "rack",
            "--maas-url",
            maas_url,
            "--secret",
            secret,
            "--force",
        ]
        return _run_local(cmd) == 0
