from charmhelpers.core.hookenv import config
from charmhelpers.core.hookenv import open_port
from charmhelpers.core.hookenv import close_port
from charmhelpers.core.hookenv import status_set
from charms.reactive import when, when_not, set_state
from charms.reactive import when_any
from charms.reactive import remove_state


@when('docker.available')
@when_not('docker-registry.standalone.running')
@when_not('block_standalone')
def launch_standalone_formation():
    """ By default we want to execute the stand-alone formation """

    # Start our application, and open the ports
    start_application()
    # Set our idempotency state
    set_state('docker-registry.standalone.running')
    status_set('active', 'Docker registry ready')


@when_any('config.changed.registry_port')
def recycle_networking_and_app():
    cfg = config()
    # guard on first run, no previous values, so do nothing.
    if not cfg.previous('registry_port'):
        return

    # Close previously configured ports
    status_set('maintenance', 'Re-configuring port bindings.')
    close_port(cfg.previous('registry_port'))
    # as the open port and app spinup are in another method, consume
    # that and tell juju to re-execute that method body by removing
    # the idempotency state
    remove_state('docker-registry.standalone.running')
    remove_state('docker-registry.running')


def start_application():
    # Declare ports to Juju - this requires a manual step of juju expose
    # otherwise the public facing ports never actually get exposed for traffic.
    open_port(config('registry_port'))
