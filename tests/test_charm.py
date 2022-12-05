# Copyright 2022 pjds
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

import unittest
from unittest.mock import Mock

from pushgateway import PushgatewayCharm, UFWRule
from ops.testing import Harness


class TestUFWRule(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test___str__(self):
        rule = UFWRule("tcp", "22", "any", "any")
        self.assertEqual(str(rule), "allow from any to any proto tcp port 22")


class TestPushgateway(unittest.TestCase):
    def setUp(self):
        self.harness = Harness(PushgatewayCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()

    # def test_config_changed(self):
    #     self.assertEqual(list(self.harness.charm._stored.things), [])
    #     self.harness.update_config({"thing": "foo"})
    #     self.assertEqual(list(self.harness.charm._stored.things), ["foo"])

    def test_handle_resources(self):
        self.harness.charm.snap_install = Mock()
        self.harness.model.resources.fetch = Mock()
        self.harness.charm.handle_resources({
            "pushgateway": {
                "filename": "pushgateway.snap",
                "resource-name": "pushgateway-snap"
            }
        })

        self.harness.charm.snap_install.assert_called_once()

    def test__on_install(self):
        self.harness.charm.handle_resources = Mock()

        self.harness.charm._on_install("")

        self.harness.charm.handle_resources.assert_called_once()

    def test_write_config(self):
        self.harness.charm.handle_resources = Mock()

        self.harness.charm.write_config()

        self.harness.charm.handle_resources.assert_called_once()

    def test_snap_install(self):
        self.harness.charm.cli = Mock()

        self.harness.charm.snap_install("test.file")

        self.harness.charm.cli.assert_called_once_with("snap install --devmode test.file")
