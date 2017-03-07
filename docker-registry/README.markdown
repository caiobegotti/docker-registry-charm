# docker-registry-charm
Docker registry charm for Juju, to be used with the Canonical Distribution of Kubernetes (CDK):

Build the charm (until it is published to the charm store) with:

```
charm build --series xenial
```

Deploy it locally with:

```
juju deploy ./xenial/docker-registry --series xenial
```

If you cannot pull upstream images to install the registry, you can use a resource:

```
docker pull registry:latest
docker save -o /tmp/registry.tar registry:latest
juju deploy ./xenial/docker-registry --series xenial --resource registry=/tmp/registry.tar
```

Verify the Docker registry responds after deploying it:

```
juju expose docker-registry
curl -X GET http://<docker_registry_ip_address>:5000/v2/_catalog
```
