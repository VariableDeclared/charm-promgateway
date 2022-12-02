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
from nturl2path import pathname2url
import subprocess
import os
import pathlib
import yaml
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
        self._to_cidr = to_cidr
        self._from_cidr = from_cidr


    def __str__(self) -> str:
        return f"allow from {self._from_cidr} to {self._to_cidr} proto {self._proto} port {self._port}"


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
        UFWRule("tcp", "9091", "", "0.0.0.0/0")
    ]
    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.fortune_action, self._on_fortune_action)
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
            self.unit.status = BlockedStatus(f"Resource {resource.get('resource-name')} not found.")
            logger.error(e)
            return

        self.snap_install(pushgateway_snap)


    def _on_install(self, event):
        # Handle resources
        self.handle_resources(self.resources.get("pushgateway"))
    
    def write_config(self):
        self.handle_resources(self.resources.get("pushgateway"))

#         etc_config_path = pathlib.Path("/etc/headscale/config.yaml")

#         if not etc_config_path.exists():
#             self.cli("touch /etc/headscale/config.yaml")
#         # TODO: Config
#         pushgateway_config = {  }

#         systemd_config_location = "/etc/systemd/system/headscale.service"

#         systemd_config = """
# [Unit]
# Description=pushgateway
# After=syslog.target
# After=network.target

# [Service]
# Type=simple
# User=pushgateway
# Group=pushgateway
# ExecStart=/usr/local/bin/pushgateway
# Restart=always
# RestartSec=5

# [Install]
# WantedBy=multi-user.target
# """
#         configs = {
#             etc_config_path: pushgateway_config, 
#             systemd_config_location: systemd_config
#         }

#         for config, contents in configs.items():
#             with open(config, 'w') as fh:
#                 fh.write(yaml.dump(contents))
#         systemd_commands = [
#                 "usermod -a -G headscale current_user",
#                 "systemctl daemon-reload",
#                 "systemctl enable --now headscale",
#                 "systemctl restart headscale"
#             ]10.66.240.223

#         for command in systemd_commands:
#             self.cli(command)


        


    def snap_install(self, snap_location):
        logger.debug(f"Installing snap using devmode. Snap {snap_location}")
        output = self.cli(f"snap install --devmode {snap_location}")

        logger.debug(f"Ran snap install. result: {output}")


    def handle_firewall(self):
        for rule in self.firewall_rules:
            self.cli(f"ufw {rule}")

    def _on_config_changed(self, _):
        """Config changed"""

        self.write_config()
        self.handle_firewall()

    def _on_fortune_action(self, event):
        """Just an example to show how to receive actions.

        TEMPLATE-TODO: change this example to suit your needs.
        If you don't need to handle actions, you can remove this method,
        the hook created in __init__.py for it, the corresponding test,
        and the actions.py file.

        Learn more about actions at https://juju.is/docs/sdk/actions
        """
        fail = event.params["fail"]
        if fail:
            event.fail(fail)
        else:
            event.set_results({"fortune": "A bug in the code is worth two in the documentation."})


if __name__ == "__main__":
    main(PushgatewayCharm)
