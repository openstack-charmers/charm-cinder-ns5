import os
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
    release = 'queens'
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
                ('nas_share_path', self.config.get('pool')),
                ('nas_mount_options', 'vers=4')])
        elif driver_type == 'iscsi':
            driver_options.extend([
                ('nexenta_host', self.config.get('host-address')),
                ('nexenta_volume', self.config.get('pool')),
                ('nexenta_volume_group', self.config.get('iscsi-group'))])

        return driver_options

    @property
    def cinder_volume_dir(self):
        return '/usr/lib/python2.7/dist-packages/cinder/volume/drivers'

    def set_git_proxy(self):
        http_proxy = os.environ.get('JUJU_CHARM_HTTP_PROXY')
        http_proxy = http_proxy or os.environ.get('JUJU_CHARM_HTTPS_PROXY')
        # Specify git file explicitly as $HOME is not always set which causes
        # git config to fail with a 128 exit code.
        cmd = ['git', 'config', '--file', '/home/ubuntu/.gitconfig']
        if http_proxy:
            ch_hookenv.log("Setting git http.proxy to {}".format(http_proxy))
            cmd.extend(['http.proxy', http_proxy])
        else:
            ch_hookenv.log("Unsetting git http.proxy")
            cmd.extend(['--unset', 'http.proxy'])
        subprocess.check_call(cmd)

    def apply_poc_driver_overwrite(self):
        self.set_git_proxy()
        os_release = ch_os_utils.get_os_codename_package('cinder-common')
        ch_hookenv.log(
            "Cloning and overwriting with stable/{}".format(os_release))
        with tempfile.TemporaryDirectory() as tmpdirname:
            git_dir = '{}/nexenta-cinder'.format(tmpdirname)
            subprocess.check_call([
                'git', 'clone', '-b', 'stable/{}'.format(os_release),
                'https://github.com/Nexenta/cinder', git_dir])
            subprocess.check_call([
                'cp', '-rf',
                '{}/cinder/volume/drivers/nexenta'.format(git_dir),
                self.cinder_volume_dir])

    # XXX THIS IS A TEMPORARY WORKAROUND AND SHOULD NOT BE INCLUDED IN
    # ANY DEPLOYMENTS OTHER THAN POCs
    def install(self):
        super(CinderNS5Charm, self).install()
        if self.config.get('poc-enable-driver-copy', False):
            ch_hookenv.log(
                "Overwriting nexenta driver. THIS IS FOR PoC DEPLOYS ONLY")
            self.apply_poc_driver_overwrite()
        else:
            ch_hookenv.log("Skipping driver overwrite")


class CinderNS5CharmRocky(CinderNS5Charm):

    # Rocky needs py3 packages.
    release = 'rocky'
    version_package = 'cinder-common'
    packages = [version_package]

    @property
    def cinder_volume_dir(self):
        return '/usr/lib/python3.6/dist-packages/cinder/volume/drivers'
