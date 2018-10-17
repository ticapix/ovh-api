#!/bin/sh

set -e
set -x
remote="ssh -t -i $HOME/.ssh/ovh_public_cloud root@vps381417.ovh.net"

set +e
which jq
check=$?
set -e
if [ $check -ne 0 ]; then
    sudo apt-get update
    sudo apt-get install --no-install-recommends -y jq
fi

$remote hostname

set +e
$remote which curl
check=$?
set -e
if [ $check -ne 0 ]; then
    $remote apt-get update
    $remote apt-get install -y curl
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
$remote which minikube
check=$?
set -e
if [ $check -ne 0 ]; then
    echo Install Minikube v0.30.0
    $remote curl --location --output /usr/local/bin/minikube https://github.com/kubernetes/minikube/releases/download/v0.30.0/minikube-linux-amd64
    $remote chmod +x /usr/local/bin/minikube
fi

set +e
$remote minikube status
check=$?
set -e
if [ $check -ne 0 ]; then
    $remote minikube start --vm-driver=none
fi

$remote kubectl get nodes -o json | jq '.items | length' | grep -v '0'

cat setup/memcached-deployment.yaml | $remote kubectl apply -f -
$remote kubectl get pod -l pod=memcached -o json | jq '.items | length' | grep -v '0'
$remote kubectl get deployment -l deployment=memcached -o json | jq '.items | length' | grep -v '0'

cat setup/memcached-service.yaml | $remote kubectl apply -f -
$remote kubectl get service -l service=memcached -o json | jq '.items | length' | grep -v '0'

cat setup/ovh-api-deployment.yaml | $remote kubectl apply -f -
$remote kubectl get pod -l pod=ovh-api -o json | jq '.items | length' | grep -v '0'
$remote kubectl get deployment -l deployment=ovh-api -o json | jq '.items | length' | grep -v '0'



kube_mgnt_ip=`$remote kubectl get service --namespace kube-system -l app=kubernetes-dashboard -o json | jq -r '.items[0].spec.clusterIP'`
kube_mgnt_port=`$remote kubectl get service --namespace kube-system -l app=kubernetes-dashboard -o json | jq -r '.items[0].spec.ports[0].port'`

echo $remote -L 8080:$kube_mgnt_ip:$kube_mgnt_port 

echo "OK"
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
