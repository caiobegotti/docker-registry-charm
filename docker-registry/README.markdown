# docker-registry-charm
Docker registry charm for Juju, to be used with the Canonical Distribution of Kubernetes (CDK) on Ubuntu Xenial:

Build the charm (until it is published to the charm store) with:

```
charm build
```

Deploy it locally with:

```
juju deploy ./builds/docker-registry
```

If you cannot pull upstream images to install the registry, you can use a resource:

```
docker pull registry:2.6.0
docker save -o /tmp/registry.tar registry:2.6.0
juju deploy ./builds/docker-registry --resource registry=/tmp/registry.tar
```

Verify the Docker registry responds after deploying it:

```
juju expose docker-registry
curl -X GET http://<docker_registry_ip_address>:5000/v2/_catalog
```

Optionally, hook your Docker registry to HAProxy and Apache units so you have a front-end:

```
juju deploy cs:haproxy
juju deploy cs:apache2
juju add-relation docker-registry:website haproxy:reverseproxy
juju add-relation haproxy:website apache2:balancer
juju unexpose docker-registry
juju expose apache2 # plus other standard apache settings like templates, servername etc
```

Verify the proxying is now working:

```
curl -X GET http://<apache_ip_address>/v2/_catalog
```
