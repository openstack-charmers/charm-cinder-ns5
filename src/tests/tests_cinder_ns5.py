#!/usr/bin/env python3

# Copyright 2019 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Encapsulate cinder-ns5 testing."""

import logging
import uuid

import zaza.model
import zaza.charm_tests.test_utils as test_utils
import zaza.utilities.openstack as openstack_utils
import zaza.charm_tests.nova.utils as nova_utils


class CinderNS5Test(test_utils.OpenStackBaseTest):
    """Encapsulate NS5 tests."""

    @classmethod
    def setUpClass(cls):
        """Run class setup for running tests."""
        super(CinderNS5Test, cls).setUpClass()
        cls.keystone_session = openstack_utils.get_overcloud_keystone_session()
        cls.model_name = zaza.model.get_juju_model()
        cls.cinder_client = openstack_utils.get_cinder_session_client(
            cls.keystone_session)
        cls.nova_client = openstack_utils.get_nova_session_client(
            cls.keystone_session)

    def test_cinder_config(self):
        logging.info('ns5')
        expected_contents = {
            'cinder-ns5': {
                'volume_driver': [
                    'cinder.volume.drivers.nexenta.ns5.nfs.NexentaNfsDriver'],
                'volume_backend_name': ['cinder-ns5'],
                'nexenta_rest_port': ['0'],
                'nexenta_user': ['admin'],
                'nas_share_path': ['tank/data']}}

        zaza.model.run_on_leader(
            'cinder',
            'sudo cp /etc/cinder/cinder.conf /tmp/',
            model_name=self.model_name)
        zaza.model.block_until_oslo_config_entries_match(
            'cinder',
            '/tmp/cinder.conf',
            expected_contents,
            model_name=self.model_name,
            timeout=2)

    def create_volume(self):
        test_vol_name = "zaza{}".format(uuid.uuid1().fields[0])
        vol_new = self.cinder_client.volumes.create(
            name=test_vol_name,
            size=2)
        openstack_utils.resource_reaches_status(
            self.cinder_client.volumes,
            vol_new.id,
            expected_status='available')
        test_vol = self.cinder_client.volumes.find(name=test_vol_name)
        self.assertEqual(
            getattr(test_vol, 'os-vol-host-attr:host').split('#')[0],
            'cinder@cinder-ns5')
        return test_vol_name

    def test_create_volume(self):
        volume_name = self.create_volume()
        volume = self.cinder_client.volumes.find(name=volume_name)
        self.cinder_client.volumes.delete(volume)

    def test_attatch_volume_to_guest(self):
        volume_name = self.create_volume()
        volume = self.cinder_client.volumes.find(name=volume_name)
        servers = self.nova_client.servers.findall()
        assert len(servers) > 0, "No server found to run attach test"
        server = servers[0]
        self.nova_client.volumes.create_server_volume(server.id, volume.id)
        attached_volumes = self.nova_client.volumes.get_server_volumes(
            server.id)
        assert len(attached_volumes) > 0, "No attached volumes found"
        assert attached_volumes[0].id == volume.id, ("Error matching attached "
                                                     "volume")
        print(openstack_utils.get_private_key(nova_utils.KEYPAIR_NAME))
