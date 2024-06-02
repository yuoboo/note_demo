#!/bin/bash


pids=`ps -ef | grep gunicorn | grep 127.0.0.1:5000 | grep -v grep | awk '{print$2}'`
for pid in ${pids};
do
  kill -9 ${pid}
  echo "kill pid ${pid}"
done
nohup gunicorn -w 4 -b 127.0.0.1:5000 wsgi --worker-class gevent >> run.log 2>&1 &
sleep 3
echo 'start success'
