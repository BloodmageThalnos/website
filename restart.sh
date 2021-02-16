pkill -f uwsgi -9
cd /root/website
uwsgi --ini ./uwsgi.ini
cd /root/dvachat
uwsgi --ini ./uwsgi.conf
/etc/init.d/nginx restart
