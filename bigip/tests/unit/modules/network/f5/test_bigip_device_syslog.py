# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, F5 Networks Inc.
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
    from library.modules.bigip_device_syslog import ApiParameters
    from library.modules.bigip_device_syslog import ModuleParameters
    from library.modules.bigip_device_syslog import ModuleManager
    from library.modules.bigip_device_syslog import ArgumentSpec

    # In Ansible 2.8, Ansible changed import paths.
    from test.units.compat import unittest
    from test.units.compat.mock import Mock

    from test.units.modules.utils import set_module_args
except ImportError:
    from ansible.modules.network.f5.bigip_device_syslog import ApiParameters
    from ansible.modules.network.f5.bigip_device_syslog import ModuleParameters
    from ansible.modules.network.f5.bigip_device_syslog import ModuleManager
    from ansible.modules.network.f5.bigip_device_syslog import ArgumentSpec

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
    def test_module_parameters(self):
        args = dict(
            kern_from='err',
            kern_to='info',
        )
        p = ModuleParameters(params=args)
        assert p.kern_from == 'err'
        assert p.kern_to == 'info'

    def test_api_parameters(self):
        p = ApiParameters(params=load_fixture('load_sys_syslog_1.json'))
        assert p.kern_from == 'debug'
        assert p.kern_to == 'emerg'


class TestUntypedManager(unittest.TestCase):

    def setUp(self):
        self.spec = ArgumentSpec()

    def test_update(self, *args):
        set_module_args(dict(
            kern_from='emerg',
            kern_to='debug',
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

        current = ApiParameters(params=load_fixture('load_sys_syslog_1.json'))

        # Override methods to force specific logic in the module to happen
        mm = ModuleManager(module=module)
        mm.update_on_device = Mock(return_value=True)
        mm.read_current_from_device = Mock(return_value=current)

        results = mm.exec_module()

        assert results['changed'] is True
