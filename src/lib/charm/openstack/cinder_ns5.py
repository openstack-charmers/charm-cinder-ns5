import charms_openstack.charm
import charmhelpers.core.hookenv as ch_hookenv # noqa 

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


class CinderNS5CharmRocky(CinderNS5Charm):

    # Rocky needs py3 packages.
    release = 'rocky'
    version_package = 'cinder-common'
    packages = [version_package]
