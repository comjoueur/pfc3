# PFC3

## Set-up

```sh
$ pip install -r requirements.txt
$ python manage.py migrate
$ python manage.py runserver
```

## Remote Test deployment

```sh
$ pip install -r requirements.txt
$ python manage.py migrate
$ python manage.py runserver 0.0.0.0:8000
```

## Connect Instance EC2

```sh
$ chmod 400 pfc2-keys.pem
$ ssh -i "pfc2-keys.pem" ubuntu@ec2-18-212-60-187.compute-1.amazonaws.com
```
