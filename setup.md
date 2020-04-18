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

EOF
```

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

Adding DNS record <local public ip> sandbox.apis.ovh

kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /  # default ingress for k8s is nginx
    traefik.ingress.kubernetes.io/rewrite-target: / # default ingress for k3s is traefik
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
