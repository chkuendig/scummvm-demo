"""Helpers for building SSH/SCP commands with persistent control sockets."""
from __future__ import annotations

import os
import subprocess
from typing import Dict, List, Optional, Tuple

CONTROL_PATH = "/tmp/scummvm-ssh-%r@%h:%p"


class SSHHelper:
    """Build ssh/scp commands and manage a persistent control socket."""

    def __init__(self, server: Optional[str], port: Optional[int]):
        self.server = server
        self.port = port

    def build_persistent_command(self, base_command: str = "ssh") -> Tuple[List[str], Dict[str, str]]:
        """Return (command, environment) preconfigured for ControlMaster."""
        cmd: List[str] = []
        env = os.environ.copy()
        ssh_password = os.environ.get("SSH_PASSWORD")

        if ssh_password:
            cmd.extend(["sshpass", "-e", base_command])
            env["SSHPASS"] = ssh_password
        else:
            cmd.append(base_command)

        ssh_key = os.environ.get("SSH_KEY_PATH")
        if ssh_key and not ssh_password:
            cmd.extend(["-i", ssh_key])

        if self.port:
            port_value = str(self.port)
            if base_command == "scp":
                cmd.extend(["-P", port_value])
            else:
                cmd.extend(["-p", port_value])

        cmd.extend(
            [
                "-o",
                "ControlMaster=auto",
                "-o",
                f"ControlPath={CONTROL_PATH}",
                "-o",
                "ControlPersist=600",
            ]
        )

        if ssh_password:
            cmd.extend(["-o", "StrictHostKeyChecking=no"])
        else:
            cmd.extend(["-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no"])

        return cmd, env

    def build_controlpath_command(self, base_command: str = "ssh") -> List[str]:
        """Return a command that reuses the persistent connection."""
        cmd = [base_command]
        if self.port:
            port_value = str(self.port)
            if base_command == "scp":
                cmd.extend(["-P", port_value])
            else:
                cmd.extend(["-p", port_value])
        cmd.extend(["-o", f"ControlPath={CONTROL_PATH}"])
        return cmd

    def open_persistent_connection(self) -> None:
        """Open the ControlMaster socket if a server is configured."""
        if not self.server:
            return
        cmd, env = self.build_persistent_command()
        for index, argument in enumerate(cmd):
            if argument in {"ssh", "scp"}:
                cmd.insert(index + 1, "-MNf")
                break
        cmd.append(self.server)
        subprocess.run(cmd, check=True, env=env)

    def close_persistent_connection(self) -> Optional[subprocess.CompletedProcess]:
        """Close the ControlMaster socket if it exists."""
        if not self.server:
            return None
        cmd = [
            "ssh",
            "-O",
            "exit",
            "-o",
            f"ControlPath={CONTROL_PATH}",
            self.server,
        ]
        return subprocess.run(cmd, check=False, capture_output=True)
