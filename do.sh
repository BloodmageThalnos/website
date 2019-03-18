cd /root/website
git pull
cd /root
pkill -f uwsgi -9
uwsgi --ini ./website/uwsgi.ini
/etc/init.d/nginx restart
