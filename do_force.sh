cd /root/website
git fetch --all
git reset --hard origin/master

cd /root
pkill -f uwsgi -9
uwsgi --ini ./website/uwsgi.ini
/etc/init.d/nginx restart
