from charms.docker import Compose
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
    status_set('active', 'Ready to vote!')


@when_any('config.changed.vote_port', 'config.changed.result_port')
def recycle_networking_and_app():
    cfg = config()
    # guard on first run, no previous values, so do nothing.
    if not cfg.previous('vote_port') or not cfg.previous('result_port'):
        return

    # Close previously configured ports
    status_set('maintenance', 'Re-configuring port bindings.')
    close_port(cfg.previous('vote_port'))
    close_port(cfg.previous('result_port'))
    # as the open port and app spinup are in another method, consume
    # that and tell juju to re-execute that method body by removing
    # the idempotency state
    remove_state('docker-registry.standalone.running')
    remove_state('docker-registry.running')


@when('docker.available', 'redis.available')
@when_not('postgres.connected', 'docker-registry.running')
def replace_redis_container(redis):
    """ Prepare the data for the docker-compose template """
    # Block the stand alone profile
    set_state('block_standalone')
    status_set('maintenance', 'Configuring charm for external Redis.')
    hosts = []
    # iterate over all the connected redis hosts
    for unit in redis.redis_data():
        hosts.append(unit['private_address'])
    redis_host = ','.join(hosts)

    # Create a merged dict with the config values we expect
    context = {}
    context.update(config())
    context.update({'redis_host': redis_host})

    start_application()
    status_set('active', 'Ready to vote!')
    # Set our idempotency state
    set_state('docker-registry.running')


@when('postgres.database.available')
@when_not('redis.connected', 'docker-registry.running')
def replace_postgres_container(postgres):
    """ Prepare the data for the docker-compose template """
    set_state('block_standalone')
    status_set('maintenance', 'Configuring charm for external Postgres.')
    # iterate over all the connected redis hosts
    pgdata = {'pg_host': postgres.host(),
              'pg_user': postgres.user(),
              'pg_pass': postgres.password(),
              'pg_db': postgres.database()}
    context = {}
    context.update(config())
    context.update(pgdata)

    start_application()
    status_set('active', 'Ready to vote!')


@when('docker.available', 'postgres.database.available', 'redis.available')
def run_with_external_services(postgres, redis):
    set_state('block_standalone')
    # Grab redis data
    hosts = []
    # iterate over all the connected redis hosts
    for unit in redis.redis_data():
        hosts.append(unit['private_address'])
    redis_host = ','.join(hosts)
    # grab postgres data
    pgdata = {'pg_host': postgres.host(),
              'pg_user': postgres.user(),
              'pg_pass': postgres.password(),
              'pg_db': postgres.database()}

    # Create a merged dict with the config values we expect
    context = {}
    context.update(config())
    context.update({'redis_host': redis_host})
    context.update(pgdata)

    start_application()
    status_set('active', 'Ready to vote!')


def start_application():
    compose = Compose('files/docker-registry')
    # Launch the workload
    compose.up()
    # Declare ports to Juju - this requires a manual step of juju expose
    # otherwise the public facing ports never actually get exposed for traffic.
    open_port(config('vote_port'))
    open_port(config('result_port'))
