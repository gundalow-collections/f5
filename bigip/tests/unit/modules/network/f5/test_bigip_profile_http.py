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
    from library.modules.bigip_profile_http import ApiParameters
    from library.modules.bigip_profile_http import ModuleParameters
    from library.modules.bigip_profile_http import ModuleManager
    from library.modules.bigip_profile_http import ArgumentSpec

    # In Ansible 2.8, Ansible changed import paths.
    from test.units.compat import unittest
    from test.units.compat.mock import Mock

    from test.units.modules.utils import set_module_args
except ImportError:
    from ansible.modules.network.f5.bigip_profile_http import ApiParameters
    from ansible.modules.network.f5.bigip_profile_http import ModuleParameters
    from ansible.modules.network.f5.bigip_profile_http import ModuleManager
    from ansible.modules.network.f5.bigip_profile_http import ArgumentSpec

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
            name='foo',
            parent='bar',
            description='This is a Test',
            proxy_type='transparent',
            insert_xforwarded_for=True,
            redirect_rewrite='all',
            encrypt_cookies=['FooCookie'],
            encrypt_cookie_secret='12345'
        )

        p = ModuleParameters(params=args)
        assert p.name == 'foo'
        assert p.parent == '/Common/bar'
        assert p.description == 'This is a Test'
        assert p.proxy_type == 'transparent'
        assert p.insert_xforwarded_for == 'enabled'
        assert p.redirect_rewrite == 'all'
        assert p.encrypt_cookies == ['FooCookie']
        assert p.encrypt_cookie_secret == '12345'

    def test_api_parameters(self):
        args = load_fixture('load_ltm_http_profile_1.json')
        p = ApiParameters(params=args)
        assert p.name == 'http'
        assert p.insert_xforwarded_for == 'disabled'
        assert p.description == 'none'


class TestManager(unittest.TestCase):

    def setUp(self):
        self.spec = ArgumentSpec()

    def test_create(self, *args):
        # Configure the arguments that would be sent to the Ansible module
        set_module_args(dict(
            name='foo',
            insert_xforwarded_for='yes',
            parent='bar',
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
        mm = ModuleManager(module=module)

        # Override methods to force specific logic in the module to happen
        mm.exists = Mock(return_value=False)
        mm.create_on_device = Mock(return_value=True)

        results = mm.exec_module()

        assert results['changed'] is True
        assert results['insert_xforwarded_for'] == 'yes'
