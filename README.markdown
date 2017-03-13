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
```

Once deployed, set up Apache configs before adding relations and exposing it:

```
juju config apache2 servername=<apache_ip_address>
juju config apache2 "enable_modules=proxy rewrite proxy_http proxy_balancer lbmethod_byrequests ssl headers"
juju config apache2 "vhost_https_template=$(cat example/server.https | base64 -w 0)"
juju config apache2 "vhost_http_template=$(cat example/server.http | base64 -w 0)"
juju config apache2 "ssl_key=$(cat example/server.key | base64 -w 0)"
juju config apache2 "ssl_cert=$(cat example/server.crt | base64 -w 0)"
juju config apache2 "ssl_keylocation=server.key"
juju config apache2 "ssl_certlocation=server.crt"

```

Finally, wrap it up:

```
juju add-relation docker-registry:website haproxy:reverseproxy
juju add-relation haproxy:website apache2:balancer
juju unexpose docker-registry
juju expose apache2
```

Verify the whole proxying is now working with TLS termination:

```
curl -X GET https://<apache_ip_address>/v2/_catalog
```

Push a test image to the new Docker registry using HTTPS:

```
docker pull busybox:latest
docker tag busybox:latest <apache_ip_address>:443/busybox:latest
docker push <apache_ip_address>:443/busybox:latest
```

Please note that you will need an actual signed certificate for this to work properly. The files inside the example/ directory are, well, an example of the settings only.
