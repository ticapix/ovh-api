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
