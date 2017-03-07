# docker-registry-charm
Docker registry charm for Juju, to be used with the Canonical Distribution of Kubernetes (CDK):

```
charm build --series trusty
docker pull registry:latest
docker save -o /tmp/registry.tar registry:latest
juju deploy ./trusty/docker-registry --series trusty --resource registry=/tmp/registry.tar
```
