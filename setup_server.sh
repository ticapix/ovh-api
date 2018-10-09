#!/bin/sh

set -e
set -x

remote="ssh -i $HOME/.ssh/ovh_public_cloud root@vps381417.ovh.net"

$remote hostname

$remote apt-get update

$remote apt-get install -y memcached git make

echo "Checking it's listening on local interface"
$remote cat /etc/memcached.conf | grep -- '^-l' | grep '127.0.0.1'

echo "Checking it's listening on default port 11211"
$remote cat /etc/memcached.conf | grep -- '^-p' | grep '11211'

$remote test -d '$HOME/ovh-api' || $remote git clone https://github.com/ticapix/ovh-api.git
$remote 'cd ovh-api && git pull'

$remote 'cd ovh-api && make test'

echo "OK"
