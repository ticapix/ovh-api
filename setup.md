# OVH OpenAPI wrapper setup

The following applies to [k3s](https://k3s.io/) and should seamlessly work with k8s too.

## Run in a separate namespace (optional)

```shell
kubectl create namespace ovh-api
kubectl config set-context --current --namespace=ovh-api
```

## Install Memcached

The following will create a memcached deployment and service.

```shell
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: memcached
spec:
  replicas: 1
  selector:
    matchLabels:
      app: memcached
  template:
    metadata:
      labels:
        app: memcached
    spec:
      containers:
      - name: memcached
        image: memcached:1.5-alpine
        ports:
        - containerPort: 11211
---
apiVersion: v1
kind: Service
metadata:
  name: memcached
spec:
  ports:
  - port: 11211
    protocol: TCP
    targetPort: 11211
  selector:
    app: memcached
EOF
```

## Install the API converter

The following will create a converter deployment and service.


```shell
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ovh-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ovh-api
  template:
    metadata:
      labels:
        app: ovh-api
    spec:
      containers:
      - name: ovh-api
        image: ticapix/ovh-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: MEMCACHED_PORT
          value: "11211"
        - name: MEMCACHED_HOST
          value: "memcached"
---
apiVersion: v1
kind: Service
metadata:
  name: ovh-api
spec:
  ports:
  - port: 80
    protocol: TCP
    targetPort: 8000
  selector:
    app: ovh-api
EOF
```

## Ingress configuration

If you have a domain, you can add an `A` record to your DNS zone.
Since I have the `apis.ovh` domain, I'm adding the following entry to my DNS zone: `sandbox         IN A      <IPv4>`

### HTTPS Support

Install [acme.sh](https://github.com/Neilpang/acme.sh/wiki/How-to-install) and add additional configuration in `$HOME/.acme.sh/account.conf` (except if you specified another configuration file)

```shell
# for OVH, check https://github.com/Neilpang/acme.sh/wiki/How-to-use-OVH-domain-api#security
OVH_AK="XXX"
OVH_AS="XXX"
OVH_CK="XXX"
```

Generate the certificate for the first time. (renewal will be done automatically by the cron job installed by acme.sh installer)

```shell
acme.sh --issue --dns dns_ovh -d '*.apis.ovh'
```

Create a shell script name `$HOME/update-secret-sandbox-tls.sh`

```shell
#!/bin/sh
kubectl create secret tls sandbox-tls \
  --key '/home/debian/.acme.sh/*.apis.ovh/*.apis.ovh.key' \
  --cert '/home/debian/.acme.sh/*.apis.ovh/fullchain.cer' \
  --save-config --dry-run -o yaml | kubectl apply -f -
```

Create a crontab job to update the kubernetes secret **after** acme.sh. `crontab -l` should output something like that:

```shell
38 0 * * * "/home/debian/.acme.sh"/acme.sh --cron --home "/home/debian/.acme.sh" > /dev/null
40 0 * * * "/home/debian/update-secret-sandbox-tls.sh" > /dev/null
```

### Ingress

Create the ingress rule.

```shell
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /  # default ingress for k8s
    traefik.ingress.kubernetes.io/rewrite-target: / # default ingress for k3s
spec:
  tls:
  - hosts:
    - sandbox.apis.ovh
    secretName: sandbox-tls
  rules:
  - host: sandbox.apis.ovh
    http:
      paths:
      - path: /ovh-api
        backend:
          serviceName: ovh-api
          servicePort: 80
EOF
```

## Update a running deployment

Simply kill the pod and kubernetes will recreate a pod using `latest` tag.

```shell
kubectl delete pod -l app=ovh-api
```
