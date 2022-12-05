#!/usr/bin/env python3
# Copyright 2022 pjds
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Charm the service.

Refer to the following post for a quick-start guide that will help you
develop a new k8s charm using the Operator Framework:

    https://discourse.charmhub.io/t/4208
"""

import logging
import subprocess
from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus, ModelError, BlockedStatus

logger = logging.getLogger(__name__)


class UFWRule(object):
    def __init__(self, proto: str, port: str, to_cidr: str, from_cidr: str) -> None:
        super().__init__()
        self._proto = proto
        self._port = port
        self._to_cidr = "any" if to_cidr == "" else to_cidr
        self._from_cidr = "any" if from_cidr == "" else from_cidr

    def __str__(self) -> str:
        return f"allow from {self._from_cidr} to \
{self._to_cidr} proto {self._proto} port {self._port}"


class PushgatewayCharm(CharmBase):
    """Charm the service."""

    _stored = StoredState()
    resources = {
        "pushgateway": {
            "filename": "pushgateway.snap",
            "resource-name": "pushgateway-snap"
        }
    }

    firewall_rules = [
        UFWRule("tcp", "22", "any", "any"),
        UFWRule("tcp", "9091", "any", "any")
    ]

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.install, self._on_install)

    def cli(self, command):
        components = command.split(" ")
        try:
            output = subprocess.check_call(components)
        except subprocess.CalledProcessError as ex:
            logging.debug(f"Command failed: {ex}")
        return output

    def handle_resources(self, resource):
        try:
            pushgateway_snap = self.model.resources.fetch(resource.get('resource-name'))
        except ModelError as e:
            self.unit.status = BlockedStatus("Failed to get pushgateway snap resource.")
            logger.error(e)
            return
        except NameError as e:
            self.unit.status = BlockedStatus(
                f"Resource {resource.get('resource-name')} not found."
            )
            logger.error(e)
            return
        self.snap_install(pushgateway_snap)
        self.model.unit.status = ActiveStatus()

    def _on_install(self, event):
        # Handle resources
        self.handle_resources(self.resources.get("pushgateway"))

    def write_config(self):
        self.handle_resources(self.resources.get("pushgateway"))

    def snap_install(self, snap_location):
        logger.debug(f"Installing snap using devmode. Snap {snap_location}")
        output = self.cli(f"snap install --devmode {snap_location}")

        logger.debug(f"Ran snap install. result: {output}")

    def handle_firewall(self):
        for rule in self.firewall_rules:
            self.cli(f"ufw {rule}")
        self.cli("ufw enable")

    def _on_config_changed(self, _):
        """Config changed"""

        self.write_config()
        self.handle_firewall()


if __name__ == "__main__":
    main(PushgatewayCharm)
