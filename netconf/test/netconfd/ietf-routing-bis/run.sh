#!/bin/bash -e

rm -rf tmp || true
mkdir tmp
cd tmp
wget https://tools.ietf.org/id/draft-ietf-netmod-rfc7223bis-00.txt
wget https://tools.ietf.org/id/draft-ietf-netmod-rfc7277bis-00.txt
wget https://tools.ietf.org/id/draft-ietf-netmod-rfc8022bis-05.txt
wget http://www.yang-central.org/twiki/pub/Main/YangTools/rfcstrip
sh rfcstrip draft-ietf-netmod-rfc7223bis-00.txt
sh rfcstrip draft-ietf-netmod-rfc7277bis-00.txt
sh rfcstrip draft-ietf-netmod-rfc8022bis-05.txt
pyang --ietf -f tree --path ./:../../../../modules/ietf-draft/:../../../../modules/ietf/ ietf-interfaces@2017-08-17.yang
pyang -f tree --path ./:../../../../modules/ietf-draft/:../../../../modules/ietf/ ex-ethernet-bonding.yang
pyang -f tree --path ./:../../../../modules/ietf-draft/:../../../../modules/ietf/ ex-ethernet.yang
pyang -f tree --path ./:../../../../modules/ietf-draft/:../../../../modules/ietf/ ex-vlan.yang
pyang --ietf -f tree --path ./:../../../../modules/ietf-draft/:../../../../modules/ietf/ ietf-ip@2017-08-21.yang
pyang --ietf -f tree --path ./:../../../../modules/ietf-draft/:../../../../modules/ietf/ ietf-routing@2017-12-11.yang
pyang --ietf -f tree --path ./:../../../../modules/ietf-draft/:../../../../modules/ietf/ ietf-ipv4-unicast-routing@2017-12-11.yang
pyang --ietf -f tree --path ./:../../../../modules/ietf-draft/:../../../../modules/ietf/ ietf-ipv6-unicast-routing@2017-12-11.yang

if [ "$RUN_WITH_CONFD" != "" ] ; then
  killall -KILL confd || true
  echo "Starting confd: $RUN_WITH_CONFD"
  source $RUN_WITH_CONFD/confdrc
  cd tmp
  for module in ietf-interfaces@2017-08-17 iana-if-type ietf-ip ex-ethernet-bonding.yang ex-ethernet.yang ex-vlan.yang ; do
    cp ../../../../modules/ietf/${module}.yang .
    confdc -c ${module}.yang --yangpath ../../../../
  done
  NCPORT=2022
  NCUSER=admin
  NCPASSWORD=admin
  confd --verbose --foreground --addloadpath ${RUN_WITH_CONFD}/src/confd --addloadpath ${RUN_WITH_CONFD}/src/confd/yang --addloadpath ${RUN_WITH_CONFD}/src/confd/aaa --addloadpath ${RUN_WITH_CONFD}/etc/confd --addloadpath .
  SERVER_PID=$!
  cd ..
else
  killall -KILL netconfd || true
  rm /tmp/ncxserver.sock || true

  /usr/sbin/netconfd --modpath=.:/usr/share/yuma/modules --module=iana-if-type --module=ietf-routing --module=ietf-ipv4-unicast-routing --module=ietf-ipv6-unicast-routing --no-startup --validate-config-only --superuser=$USER
  /usr/sbin/netconfd --modpath=.:/usr/share/yuma/modules --module=iana-if-type --module=ietf-routing --module=ietf-ipv4-unicast-routing --module=ietf-ipv6-unicast-routing --no-startup --superuser=$USER 2>&1 1>server.log &
   SERVER_PID=$!
  cd ..
fi

sleep 3
python session.litenc.py --server=$NCSERVER --port=$NCPORT --user=$NCUSER --password=$NCPASSWORD
#python session.yangcli.py --server=$NCSERVER --port=$NCPORT --user=$NCUSER --password=$NCPASSWORD
#kill -KILL $SERVER_PID
cat tmp/server.log
sleep 1
