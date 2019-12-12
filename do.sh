cd /root/website
git pull
if [ $? != 0 ];then
    echo '================================='
    echo 'GIT PULL FAILED, try force pull or fix error manually.'
    exit 1
fi
echo 'GIT PULL SUCCESS.'
cd /root
pkill -f uwsgi -9
uwsgi --ini ./website/uwsgi.ini
/etc/init.d/nginx restart
