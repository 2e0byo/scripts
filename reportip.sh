#!/bin/sh
# basic script to keep a file called hostname.ip in the home directory on mira up to date with current ip
set -e

interface='wlp5s0'

ifconfig > /dev/null 2>&1 $interface || exit 1

echo 'hello'
ip_address=$(/sbin/ifconfig $interface | sed -n 's/.*inet addr:\([^ ]*\).*/\1/p') #> /dev/null 2>&1


if [ ! -f /tmp/current_ip ]
then
    echo ${ip_address} >| /tmp/current_ip
    scp -i /root/.ssh/id_rsa /tmp/current_ip lntq46@mira:$HOSTNAME.ip > /dev/null    
fi


if [ "${ip_address}" != $(cat /tmp/current_ip) ]
then
    # echo "Your new IP address is ${ip_address}" |
    # 	mail -s "IP address change" you@your.mail
    echo ${ip_address} >| /tmp/current_ip
    scp -i /root/.ssh/id_rsa /tmp/current_ip lntq46@mira:$HOSTNAME.ip > /dev/null
fi
