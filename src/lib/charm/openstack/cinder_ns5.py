import charms_openstack.charm
import charmhelpers.core.hookenv as ch_hookenv # noqa 

charms_openstack.charm.use_defaults('charm.default-select-release')

class CinderNS5Charm(
        charms_openstack.charm.CinderStoragePluginCharm):

    name = 'cinder_ns5'
    version_package = ''
    release = 'ocata'
    packages = [version_package]
    stateless = True
    # Specify any config that the user *must* set.
    mandatory_config = []

    def cinder_configuration(self):
        volume_driver = ''
        driver_options = [
            ('volume_driver', volume_driver),
            # Add config options that needs setting on cinder.conf
        ]
        return driver_options

class CinderNS5CharmRocky(CinderNS5Charm):

    # Rocky needs py3 packages.
    release = 'rocky'
    version_package = ''
    packages = [version_package]
