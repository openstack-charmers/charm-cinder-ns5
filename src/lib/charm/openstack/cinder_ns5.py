import subprocess
import tempfile

import charms_openstack.charm
import charmhelpers.core.hookenv as ch_hookenv # noqa 
import charmhelpers.contrib.openstack.utils as ch_os_utils

charms_openstack.charm.use_defaults('charm.default-select-release')


class CinderNS5Charm(
        charms_openstack.charm.CinderStoragePluginCharm):

    DRIVERS = {
        'nfs': 'cinder.volume.drivers.nexenta.ns5.nfs.NexentaNfsDriver',
        'iscsi': 'cinder.volume.drivers.nexenta.ns5.iscsi.NexentaISCSIDriver'}

    name = 'cinder_ns5'
    version_package = 'cinder-common'
    release = 'ocata'
    packages = [version_package]
    stateless = True
    # Specify any config that the user *must* set.
    mandatory_config = ['rest-address', 'host-address', 'pool']

    def cinder_configuration(self):
        driver_type = self.config.get('driver-type')
        driver_options = [
            ('volume_driver', self.DRIVERS[driver_type]),
            ('volume_backend_name', self.config.get('backend-name')),
            ('nexenta_rest_address', self.config.get('rest-address')),
            ('nexenta_rest_port', self.config.get('rest-port')),
            ('nexenta_user', self.config.get('rest-user')),
            ('nexenta_password', self.config.get('rest-password'))]

        if driver_type == 'nfs':
            driver_options.extend([
                ('nas_host', self.config.get('host-address')),
                ('nas_share_path', self.config.get('pool'))])
        elif driver_type == 'iscsi':
            driver_options.extend([
                ('nexenta_host', self.config.get('host-address')),
                ('nexenta_volume', self.config.get('pool')),
                ('nexenta_volume_group', self.config.get('iscsi-group'))])

        return driver_options

    @property
    def cinder_volume_dir(self):
        return '/usr/lib/python2.7/dist-packages/cinder/volume/drivers'

    # XXX THIS IS A TEMPORARY WORKAROUND AND SHOULD NOT BE INCLUDED IN
    # ANY DEPLOYMENTS OTHER THAN POCs
    def install(self):
        super(CinderNS5Charm, self).install()
        os_release = ch_os_utils.get_os_codename_package('cinder-common')
        with tempfile.TemporaryDirectory() as tmpdirname:
            git_dir = '{}/nexenta-cinder'.format(tmpdirname)
            subprocess.check_output([
                'git', 'clone', '-b', 'stable/{}'.format(os_release),
                'https://github.com/Nexenta/cinder', git_dir])
            subprocess.check_output([
                'cp', '-rf',
                '{}/cinder/volume/drivers/nexenta'.format(git_dir),
                self.cinder_volume_dir])


class CinderNS5CharmRocky(CinderNS5Charm):

    # Rocky needs py3 packages.
    release = 'rocky'
    version_package = 'cinder-common'
    packages = [version_package]

    @property
    def cinder_volume_dir(self):
        return '/usr/lib/python3.6/dist-packages/cinder/volume/drivers'
