uwsgi -s /tmp/uwsgi.sock -w app2:app --socket 10.0.20.11:5001 --protocol=http --enable-threads
