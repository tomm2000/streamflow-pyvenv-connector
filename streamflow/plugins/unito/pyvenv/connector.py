from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import MutableMapping, MutableSequence
from importlib.resources import files
from typing import Any
import uuid


from streamflow.core.deployment import ExecutionLocation
from streamflow.deployment.wrapper import ConnectorWrapper
from streamflow.log_handler import logger
from streamflow.core.exception import WorkflowDefinitionException


EXCLUDED_CONNECTOR_PARAMETERS = [
    "path",
    "requirements",
    "random-suffix",
    "keep-venv",
    "force-install",
]

class PyVenvConnector(ConnectorWrapper):
    @classmethod
    def get_schema(cls) -> str:
        return (
            files(__package__)
            .joinpath("schemas")
            .joinpath("pyvenv.json")
            .read_text("utf-8")
        )

    def __init__(self, **kwargs: Any):
        super().__init__(
            **{
                k: v
                for k, v in kwargs.items()
                if k not in EXCLUDED_CONNECTOR_PARAMETERS
            }
        )

        self.random_suffix = kwargs.get("random-suffix", True)

        path = kwargs.get("path", f"/tmp/streamflow-venv")
        if self.random_suffix:
            self.venv_path: str = os.path.join(path, uuid.uuid4().hex)
        else:
            self.venv_path: str = path

        self.keep_venv = kwargs.get("keep-venv", False)
        self.force_install = kwargs.get("force-install", False)
        self.requirements = kwargs.get("requirements", [])

    async def deploy(self, external: bool) -> None:
        locations = await self.connector.get_available_locations(service=self.service)


        if len(locations) != 1:
            raise WorkflowDefinitionException(
                f"{self.__class__.__name__} connectors support only nested connectors with a single location. "
                f"{self.connector.deployment_name} returned {len(locations)} available locations."
            )

        location = next(iter(locations.values()))

        # run command to check if the venv already exists
        out = await self.connector.run(
            location=location.location,
            command=["test", "-d", self.venv_path, "&&", "test", "-f", os.path.join(self.venv_path, "bin", "activate")],
            capture_output=True,
        )

        assert out is not None, "Expected output from command, got None"
        _, code = out

        self.venv_available = code == 0

        # only create the venv if it doesn't exist
        if not self.venv_available:
            await self._create_venv(location.location)
        else:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"PyVenvConnector: Virtual environment already exists at {self.venv_path}")

        # only install requirements if the venv was just created or if force_install is True
        if not self.venv_available or self.force_install:
            await self._install_requirements(location.location)

        self._inner_location = location

    async def undeploy(self, external: bool) -> None:
        if not self.keep_venv:
            locations = await self.connector.get_available_locations(service=self.service)

            if len(locations) != 1:
                raise WorkflowDefinitionException(
                    f"{self.__class__.__name__} connectors support only nested connectors with a single location. "
                    f"{self.connector.deployment_name} returned {len(locations)} available locations."
                )
            else:
                location = next(iter(locations.values()))
                await self._remove_venv(location.location)

    async def _create_venv(self, location: ExecutionLocation) -> None:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"PyVenvConnector: Creating virtual environment at {self.venv_path}")
        out = await self.connector.run(
            location=location,
            command=[
                "python3",
                "-m",
                "venv",
                self.venv_path,
            ],
            capture_output=True,
        )

        assert out is not None, "Expected output from command, got None"
        stderr, code = out

        if code != 0:
            raise WorkflowDefinitionException(
                f"Failed to create virtual environment at {self.venv_path}. "
                f"Command exited with code {code}. {stderr}"
            )

        # test if the venv was created successfully
        out = await self.connector.run(
            location=location,
            command=["test", "-d", self.venv_path, "&&", "test", "-f", os.path.join(self.venv_path, "bin", "activate")],
            capture_output=True,
        )

        assert out is not None, "Expected output from command, got None"
        _, code = out

        if code != 0:
            raise WorkflowDefinitionException(
                f"Failed to create virtual environment at {self.venv_path}. "
                f"Command exited with code {code}."
            )

    async def _install_requirements(self, location: ExecutionLocation) -> None:
        for requirement in self.requirements:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"PyVenvConnector: Installing requirement: {requirement}")
            await self.connector.run(
                location=location,
                command=[
                    os.path.join(self.venv_path, "bin", "pip"),
                    "install",
                    requirement,
                ],
            )

    async def _remove_venv(self, location: ExecutionLocation) -> None:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"PyVenvConnector: Removing virtual environment at {self.venv_path}")
        await self.connector.run(
            location=location,
            command=[
                "rm",
                "-rf",
                self.venv_path,
            ],
        )

    async def run(
        self,
        location: ExecutionLocation,
        command: MutableSequence[str],
        environment: MutableMapping[str, str] | None = None,
        workdir: str | None = None,
        stdin: int | str | None = None,
        stdout: int | str = asyncio.subprocess.STDOUT,
        stderr: int | str = asyncio.subprocess.STDOUT,
        capture_output: bool = False,
        timeout: int | None = None,
        job_name: str | None = None,
    ) -> tuple[str, int] | None:

        if environment is None:
            environment = {}

        path = [
            os.path.join(self.venv_path, "bin"),
            "$PATH",
        ]

        if environment.get("PATH", None) is not None:
            path.append(environment["PATH"])

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"PyVenvConnector: Running command with PATH: {os.pathsep.join(path)}")

        environment["PATH"] = os.pathsep.join(path)

        return await super().run(
            location=location,
            command=command,
            environment=environment,
            workdir=workdir,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            job_name=job_name,
            timeout=timeout,
            capture_output=capture_output,
        )