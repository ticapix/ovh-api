OVH API converter to OpenAPI3

[![Build Status](https://travis-ci.org/ticapix/ovh-api.svg?branch=master)](https://travis-ci.org/ticapix/ovh-api)

**alpha state**

**Not an official OVH project**

## Quick test

An **unmonitored** non-production ready **demo** service is hosted at http://sandbox.apis.ovh/ovh-api/

The url syntax is `http://sandbox.apis.ovh/ovh-api/<region>/<endpoint>`

The available regions are listed here https://github.com/ovh/python-ovh/blob/6e9835d205bb322e3357bebdbef3e1f74cb629da/ovh/client.py#L74

## Local execution

```shell
make run
```

And nagivate to http://localhost:8000/ovh-eu/me

## Local testing

```shell
make test
```

## Docker deployement

```shell
docker pull ticapix/ovh-api
```

The exposed port is `8000`

## Configuration

Default cache TTL is `3600` seconds. This value can be changed with the environment variable `CACHE_TTL`

### Memcached

If available, [Memcached](https://memcached.org/) is used to cache intermediate convertion results.

Memcached configuration can be tuned with `MEMCACHED_PORT` and `MEMCACHED_HOST` environment variables. Default is 127.0.0.1:11211

## Deployement on K8s or K3s

Check the [setup](setup.md) guide.
