Cryptoalarm
===

Instalace
===
Závislosti:

* python3
* postgresql
* composer
* PHP >= 7.0.0, extensions: OpenSSL, PDO, Mbstring, Tokenizer, XML, pgsql

Webapp
====
```
webapp/$ composer install
webapp/$ cp .env.example .env
webapp/$ php artisan key:generate
```
Vytvořit databázi např: ```createdb cryptoalarm```, nastavit připojení v ```webapp/.env```

```
webapp/$ php artisan migrate
webapp/$ php artisan db:seed
webapp/$ php artisan serve
```
Výsledkem je aplikace běžící na adrese: [http://localhost:8000](http://localhost:8000)
s několika uživateli:

* alice@cryptoalarm.tld:alice
* bob@cryptoalarm.tld:bob
* carol@cryptoalarm.tld:carol
* dave@cryptoalarm.tld:dave

Každý z uživatelů má definovanou alespoň jednu adresu, kterou systém monitoruje.
Pokud bude webapp spuštěna jinak je nutné změnit url v db: settings(key=notification_url).

Monitor
====
Nastavit připojení k db a rpc api v ```cryptoalarm/config.py```
```
cryptoalarm/$ pip install -r requirements.txt
cryptoalarm/$ ./cryptoalarm.py --init
cryptoalarm/$ ./cryptoalarm.py 
```

Docker
=====
```
docker build -t cryptoalarm .
docker run -v config.py/config.py cryptoalarm
```