# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 F5 Networks Inc.
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json
import pytest
import sys

if sys.version_info < (2, 7):
    pytestmark = pytest.mark.skip("F5 Ansible modules require Python >= 2.7")

from ansible.module_utils.basic import AnsibleModule

try:
    from library.modules.bigip_policy_rule import ModuleParameters
    from library.modules.bigip_policy_rule import ApiParameters
    from library.modules.bigip_policy_rule import ModuleManager
    from library.modules.bigip_policy_rule import ArgumentSpec

    # In Ansible 2.8, Ansible changed import paths.
    from test.units.compat import unittest
    from test.units.compat.mock import Mock

    from test.units.modules.utils import set_module_args
except ImportError:
    from ansible.modules.network.f5.bigip_policy_rule import ModuleParameters
    from ansible.modules.network.f5.bigip_policy_rule import ApiParameters
    from ansible.modules.network.f5.bigip_policy_rule import ModuleManager
    from ansible.modules.network.f5.bigip_policy_rule import ArgumentSpec

    # Ansible 2.8 imports
    from ansible_collections.f5.bigip.tests.unit.compat import unittest
    from ansible_collections.f5.bigip.tests.unit.compat.mock import Mock

    from ansible_collections.f5.bigip.tests.unit.modules.utils import set_module_args


fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')
fixture_data = {}


def load_fixture(name):
    path = os.path.join(fixture_path, name)

    if path in fixture_data:
        return fixture_data[path]

    with open(path) as f:
        data = f.read()

    try:
        data = json.loads(data)
    except Exception:
        pass

    fixture_data[path] = data
    return data


class TestParameters(unittest.TestCase):
    def test_module_parameters_policy(self):
        args = dict(
            policy='Policy - Foo'
        )
        p = ModuleParameters(params=args)
        assert p.policy == 'Policy - Foo'

    def test_module_parameters_actions(self):
        args = dict(
            actions=[
                dict(
                    type='forward',
                    pool='pool-svrs'
                )
            ]
        )
        p = ModuleParameters(params=args)
        assert len(p.actions) == 1

    def test_module_parameters_conditions(self):
        args = dict(
            conditions=[
                dict(
                    type='http_uri',
                    path_begins_with_any=['/ABC']
                )
            ]
        )
        p = ModuleParameters(params=args)
        assert len(p.conditions) == 1

    def test_module_parameters_name(self):
        args = dict(
            name='rule1'
        )
        p = ModuleParameters(params=args)
        assert p.name == 'rule1'

    def test_api_parameters(self):
        args = load_fixture('load_ltm_policy_draft_rule_http-uri_forward.json')
        p = ApiParameters(params=args)
        assert len(p.actions) == 1
        assert len(p.conditions) == 1


class TestManager(unittest.TestCase):

    def setUp(self):
        self.spec = ArgumentSpec()

    def test_create_policy_rule_no_existence(self, *args):
        set_module_args(dict(
            name="rule1",
            state='present',
            policy='policy1',
            actions=[
                dict(
                    type='forward',
                    pool='baz'
                )
            ],
            conditions=[
                dict(
                    type='http_uri',
                    path_begins_with_any=['/ABC']
                )
            ],
            provider=dict(
                server='localhost',
                password='password',
                user='admin'
            )
        ))

        module = AnsibleModule(
            argument_spec=self.spec.argument_spec,
            supports_check_mode=self.spec.supports_check_mode
        )

        # Override methods to force specific logic in the module to happen
        mm = ModuleManager(module=module)
        mm.exists = Mock(return_value=False)
        mm.publish_on_device = Mock(return_value=True)
        mm.draft_exists = Mock(return_value=False)
        mm._create_existing_policy_draft_on_device = Mock(return_value=True)
        mm.create_on_device = Mock(return_value=True)

        results = mm.exec_module()

        assert results['changed'] is True

    def test_create_policy_rule_idempotent_check(self, *args):
        set_module_args(dict(
            name="rule1",
            state='present',
            policy='policy1',
            actions=[
                dict(
                    type='forward',
                    pool='baz'
                )
            ],
            conditions=[
                dict(
                    type='http_uri',
                    path_begins_with_any=['/ABC']
                )
            ],
            provider=dict(
                server='localhost',
                password='password',
                user='admin'
            )
        ))

        current = ApiParameters(params=load_fixture('load_ltm_policy_draft_rule_http-uri_forward.json'))
        module = AnsibleModule(
            argument_spec=self.spec.argument_spec,
            supports_check_mode=self.spec.supports_check_mode
        )

        # Override methods to force specific logic in the module to happen
        mm = ModuleManager(module=module)
        mm.exists = Mock(return_value=True)
        mm.read_current_from_device = Mock(return_value=current)
        mm.draft_exists = Mock(return_value=False)
        mm.update_on_device = Mock(return_value=True)
        mm._create_existing_policy_draft_on_device = Mock(return_value=True)
        mm.publish_on_device = Mock(return_value=True)

        results = mm.exec_module()

        assert results['changed'] is True
