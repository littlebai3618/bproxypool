module="$1"
if [ -f ./status/pid.${module} ] ; then
    echo "${module} maybe running now. check it or remove status/pid.${module}"
    exit 255
fi

if [ "$module" == "scheduler" ] ; then
  nohup python run.py ${module} >./log/shell_run_${module}.log 2>&1 &
  echo $! > ./status/pid.${module}
  exit 255
fi

if [ "$module" == "service" ] ; then
  nohup gunicorn -c ./config/gunicorn.py run:app >./log/shell_run_${module}.log 2>&1 &
  echo $! > ./status/pid.${module}
  exit 255
fi

echo "please use: "
echo "'sh start.sh scheduler' start ProxyGetter"
echo "'sh start.sh service' start APIService"
echo "'sh stop.sh scheduler' stop ProxyGetter"
echo "'sh stop.sh service' stop APIService"


