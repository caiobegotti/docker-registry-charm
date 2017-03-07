from charmhelpers.core.hookenv import config
from charmhelpers.core.hookenv import open_port
from charmhelpers.core.hookenv import close_port
from charmhelpers.core.hookenv import status_set
from charmhelpers.core.hookenv import resource_get
from charms.reactive import when, when_not, set_state
from charms.reactive import when_any
from charms.reactive import remove_state

from subprocess import check_output, check_call


@when('docker.available')
@when_not('docker-registry.standalone.running')
@when_not('block_standalone')
def launch_standalone_formation():
    path = resource_get('registry')
    if path:
        if not check_call(['docker', 'load', '-i', path]):
            status_set('maintenance', 'Cannot import registry resource.')
            return

    start_application()
    set_state('docker-registry.standalone.running')
    status_set('active', 'Docker registry ready.')


@when_any('config.changed.registry_port')
def recycle_networking_and_app():
    cfg = config()
    # guard on first run, no previous values, so do nothing
    if not cfg.previous('registry_port'):
        return

    status_set('maintenance', 'Re-configuring port bindings.')
    close_port(cfg.previous('registry_port'))
    remove_state('docker-registry.standalone.running')
    remove_state('docker-registry.running')


def start_application():
    open_port(config('registry_port'))
