#!/bin/sh

set -e
set -x
remote="ssh -t -i $HOME/.ssh/ovh_public_cloud root@vps381417.ovh.net"

$remote hostname

set +e
$remote which curl jq
check=$?
set -e
if [ $check -ne 0 ]; then
    $remote apt-get update
    $remote apt-get install -y jq curl
fi

set +e
$remote which kubectl
check=$?
set -e
if [ $check -ne 0 ]; then
    echo Install kubectl binary using native package management
    $remote apt-get update
    $remote apt-get install -y apt-transport-https
    $remote 'curl --silent https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -'
    $remote 'echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" > /etc/apt/sources.list.d/kubernetes.list'
    $remote apt-get update
    $remote apt-get install -y kubectl
fi

set +e
$remote which minicube
check=$?
set -e
if [ $check -ne 0 ]; then
    echo Install Minikube v0.30.0
    $remote curl --location --output /usr/local/bin/minicube https://github.com/kubernetes/minikube/releases/download/v0.30.0/minikube-linux-amd64
    $remote chmod +x /usr/local/bin/minicube
fi

set +e
$remote minicube status
check=$?
set -e
if [ $check -ne 0 ]; then
    $remote minicube start --vm-driver=none
fi

$remote "curl --insecure https://127.0.0.1:8443 | jq '.'"

exit

$remote 'echo deb http://deb.debian.org/debian/ buster non-free contrib main > /etc/apt/sources.list.d/buster.list'

$remote 'cat > /etc/apt/preferences' <<EOF 
Package: *
Pin: release a=stable
Pin-Priority: 900
EOF

$remote apt-get update

$remote apt-get install --no-install-recommends -y memcached git make

$remote 'DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y -t buster python3-venv'

echo "Checking it's listening on local interface"
$remote cat /etc/memcached.conf | grep -- '^-l' | grep '127.0.0.1'

echo "Checking it's listening on default port 11211"
$remote cat /etc/memcached.conf | grep -- '^-p' | grep '11211'

$remote test -d '$HOME/ovh-api' || $remote git clone https://github.com/ticapix/ovh-api.git
$remote 'cd ovh-api && git pull'

$remote 'cd ovh-api && make test'

echo "OK"
