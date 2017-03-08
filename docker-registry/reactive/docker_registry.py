from charmhelpers.core.hookenv import config
from charmhelpers.core.hookenv import open_port
from charmhelpers.core.hookenv import close_port
from charmhelpers.core.hookenv import status_set
from charmhelpers.core.hookenv import resource_get

from charms.docker import Compose

from charms.reactive import when, when_not, set_state
from charms.reactive import when_any
from charms.reactive import remove_state

from charms.templating.jinja2 import render
from subprocess import check_call


@when('docker.available')
@when_not('docker-registry.standalone.running')
@when_not('block_standalone')
def launch_standalone_formation():
    path = resource_get('registry')
    if path:
        check_call(['docker', 'load', '-i', path])

    render('docker-compose.yml',
           'files/docker-registry/docker-compose.yml',
           config())

    start_application()
    set_state('docker-registry.standalone.running')
    status_set('active', 'Docker registry ready.')


@when_any('config.changed.registry_port', 'config.changed.registry_tag')
def recycle_networking_and_app():
    cfg = config()
    # guard on first run, no previous values, so do nothing
    if not cfg.previous('registry_port') or not cfg.previous('registry_tag'):
        return

    status_set('maintenance', 'Re-configuring port bindings.')
    close_port(cfg.previous('registry_port'))

    status_set('maintenance', 'Re-generating Docker compose YAML.')
    render('docker-compose.yml',
           'files/docker-registry/docker-compose.yml',
           config())

    remove_state('docker-registry.standalone.running')
    remove_state('docker-registry.running')


def start_application():
    compose = Compose('files/docker-registry')
    compose.up()

    open_port(config('registry_port'))

@when('website.available')
def configure_website(website):
    website.configure(port=config('registry_port'))
