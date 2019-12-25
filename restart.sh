#!/bin/sh

sh stop.sh $1
echo "stop success..."
sleep 2
sh start.sh $1
echo "start success"