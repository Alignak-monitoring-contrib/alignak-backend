uwsgi --plugin python --wsgi-file bin/alignak_backend.py --callable app --socket 0.0.0.0:5000 --protocol=http --enable-threads -p 4
