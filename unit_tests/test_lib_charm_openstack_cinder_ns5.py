# Copyright 2016 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import print_function

import charmhelpers

import charm.openstack.cinder_ns5 as cinder_ns5

import charms_openstack.test_utils as test_utils


class TestCinderNS5Charm(test_utils.PatchHelper):

    def _patch_config_and_charm(self, config):
        self.patch_object(charmhelpers.core.hookenv, 'config')

        def cf(key=None):
            if key is not None:
                return config[key]
            return config

        self.config.side_effect = cf
        c = cinder_ns5.CinderNS5Charm()
        return c

    def test_cinder_base(self):
        charm = self._patch_config_and_charm({})
        self.assertEqual(charm.name, 'cinder_ns5')
        self.assertEqual(charm.version_package, 'cinder-common')
        self.assertEqual(charm.packages, ['cinder-common'])

    def test_cinder_configuration_iscsi(self):
        charm = self._patch_config_and_charm({
            'driver-type': 'iscsi',
            'backend-name': 'special-iscsi',
            'rest-address': '10.0.0.20',
            'rest-port': '0',
            'rest-user': 'super-admin',
            'rest-password': 'password',
            'host-address': '192.168.2.1',
            'pool': 'vol1',
            'iscsi-group': 'special-group'})
        config = charm.cinder_configuration()
        self.assertEqual(
            config,
            [
                ('volume_driver', ('cinder.volume.drivers.nexenta.ns5.iscsi.'
                                   'NexentaISCSIDriver')),
                ('volume_backend_name', 'special-iscsi'),
                ('nexenta_rest_address', '10.0.0.20'),
                ('nexenta_rest_port', '0'),
                ('nexenta_user', 'super-admin'),
                ('nexenta_password', 'password'),
                ('nexenta_host', '192.168.2.1'),
                ('nexenta_volume', 'vol1'),
                ('nexenta_volume_group', 'special-group')])

    def test_cinder_configuration_nfs(self):
        charm = self._patch_config_and_charm({
            'driver-type': 'nfs',
            'backend-name': 'special-iscsi',
            'rest-address': '10.0.0.20',
            'rest-port': '0',
            'rest-user': 'super-admin',
            'rest-password': 'password',
            'host-address': '192.168.2.1',
            'pool': 'vol1',
            'iscsi-group': 'special-group'})
        config = charm.cinder_configuration() # noqa
        self.assertEqual(
            config,
            [
                ('volume_driver', ('cinder.volume.drivers.nexenta.ns5.nfs.'
                                   'NexentaNfsDriver')),
                ('volume_backend_name', 'special-iscsi'),
                ('nexenta_rest_address', '10.0.0.20'),
                ('nexenta_rest_port', '0'),
                ('nexenta_user', 'super-admin'),
                ('nexenta_password', 'password'),
                ('nas_host', '192.168.2.1'),
                ('nas_share_path', 'vol1')])
