# Cryptoalarm
## Installation
### Dependencies:

* python3
* postgresql
* composer
* npm
* Java
* selenium standalone server [https://www.seleniumhq.org/download/](https://www.seleniumhq.org/download/)
* PHP >= 7.0.0, extensions: OpenSSL, PDO, Mbstring, Tokenizer, XML, pgsql

### Webapp

```
webapp/$ composer install
webapp/$ npm install
webapp/$ cp .env.example .env
webapp/$ php artisan key:generate
```
Create databse: ```createdb cryptoalarm```, set-up a connection in ```webapp/.env```

```
webapp/$ php artisan migrate
webapp/$ php artisan db:seed
webapp/$ npm run dev
```

### Monitor

Configure database, rpc url of nodes and SMTP server in ```cryptoalarm/config.json```
```
cryptoalarm/$ pip install -r requirements.txt
```

## Usage
```
webapp/$ php artisan serve
```

Application is now running on [http://localhost:8000](http://localhost:8000) with the following users:

* alice@cryptoalarm.tld:alice
* bob@cryptoalarm.tld:bob
* carol@cryptoalarm.tld:carol
* dave@cryptoalarm.tld:dave

Each user has atleast one watchlist created.

```
cryptoalarm/$ ./run.py --init # set last block as last processed 
cryptoalarm/$ ./run.py # launch application
```

## [Bitcointalk.org](https://bitcointalk.org/)

```
webapp/$ php artisan command:bitcointalk /path/to/selenium-standalone-server.jar [port=4444]
```

## Docker
```
# docker build -t cryptoalarm .
# docker run -v docker run -v cryptoalarm cryptoalarm
```