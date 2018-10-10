OVH API converter to OpenAPI3

[![Build Status](https://travis-ci.org/ticapix/ovh-api.svg?branch=master)](https://travis-ci.org/ticapix/ovh-api)

**alpha state**

**Not an official OVH project**

## Local execution

```shell
make run
```

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

Memcached is configuration can be tuned with `MEMCACHED_PORT` and `MEMCACHED_HOST` environment variables.

