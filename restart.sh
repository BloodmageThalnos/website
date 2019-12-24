pkill -f uwsgi -9
uwsgi --ini ./uwsgi.ini
/etc/init.d/nginx restart