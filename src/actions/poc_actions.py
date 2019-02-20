#!/usr/bin/env python3
# Copyright 2019 Canonical Ltd
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

import os
import sys

# Load modules from $CHARM_DIR/lib
sys.path.append('lib')

from charms.layer import basic
basic.bootstrap_charm_deps()

import charmhelpers.contrib.openstack.utils as os_utils
import charmhelpers.core.hookenv as hookenv
import charms_openstack.bus
import charms_openstack.charm

charms_openstack.bus.discover()


def install_action(*args):
    """Run the pause action."""
    with charms_openstack.charm.provide_charm_instance() as charm_instance:
        charm_instance.install()
    # XXX Cinder charm should control these services but since this action
    #     is only needed for a PoC this is ok.
    services = ['cinder-volume', 'cinder-scheduler']
    os_utils.manage_payload_services('stop', services)
    os_utils.manage_payload_services('start', services)


ACTIONS = {
    "poc-reinstall": install_action,
}


def main(args):
    action_name = os.path.basename(args[0])
    try:
        action = ACTIONS[action_name]
    except KeyError:
        return "Action %s undefined" % action_name
    else:
        try:
            action(args)
        except Exception as e:
            hookenv.action_fail(str(e))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
