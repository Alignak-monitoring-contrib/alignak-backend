# Alignak-bckend


# Install

*NOTE*: This project is Python > 3.2 only.

*TOBEDONE* You can install it directly from Pypi:

```
pip install alignak_backend
```

You can install it from source once you cloned successfully the
repository:

```
pip install .
```

If you want to hack into the codebase (e.g for future contribution),
just install like this:

```
pip install -e .
```

## DEBIAN Jessie

* prerequisites

```
apt-get -y install python3 python3-dev python3-pip git
```

* get the project sources

```
git clone https://github.com/ddurieux/alignak-backend
```

* python prerequisites

```
pip3 install -r alignak-backend/requirements.txt
```

* install 

```
cd alignak-backend
python3 setup.py install
```

* run
```
alignak_backend run
```

# Use API
Alignak-backend run on port 5000, so use http://ip:5000/

# API documentation
Use browser to url of alignak-backend http://127.0.0.1:5000/docs

# examples to add data

## Add new Host

```
curl -X POST -H 'Content-Type: application/json' -d '{"name": "serverC001", "host_name": "serverC001", "address": "10.0.0.40"}' 127.0.0.1:5000/hosts
```