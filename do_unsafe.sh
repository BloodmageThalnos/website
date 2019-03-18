cd ./website
cp -f ./db.sqlite3 ../database
git checkout .
git pull
cd ..
pkill -f uwsgi -9
uwsgi --ini ./website/uwsgi.ini
/etc/init.d/nginx restart
