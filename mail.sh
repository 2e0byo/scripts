#!/bin/sh
function die () {
  echo $1 > /tmp/email-fail.msg
  exit 1
}

offlineimap || die "Offlineimap Failed"
pkill -2 -u $UID -x mu || echo 'no need to kill mu'
sleep 0.1
mu index || die "mu index failed"
rm /tmp/email-fail.msg || exit 0
