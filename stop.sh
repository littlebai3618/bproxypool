module="$1"
if [ -f ./status/pid.${module} ] ; then
    if [ "$module" == "scheduler" ] || [ "$module" == "service" ] ; then
        pid=$(cat status/pid.${module})
        kill -9 ${pid}
        rm ./status/pid.${module}
        exit 255
    fi
fi

echo "please use: "
echo "'sh start.sh scheduler' start ProxyGetter"
echo "'sh start.sh service' start APIService"
echo "'sh stop.sh scheduler' stop ProxyGetter"
echo "'sh stop.sh service' stop APIService"