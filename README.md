# Currency-API

## Table of Contents
1. [Setup](#setup)
   - [Migrate Database](#migrate-database)
   - [Run Project](#run-project)
   - [Populate Database with Example Data](#populate-database-with-example-data)
2. [URLs](#urls)
   - [View All Currencies](#view-all-currencies)
   - [View Latest Exchange Rate](#view-latest-exchange-rate)
   - [Admin Interface](#admin-interface)

## Setup
### Migrate Database
To migrate database.
```
rav run makemigrations
rav run migrate
```

### Run Project
To run project.
```
rav run server
```

### Populate Database with Example Data
To populate database with example data from [yfinance](https://github.com/ranaroussi/yfinance) API.
```
rav run fetch_data
```

## URLs
All API urls start with "/api".
### View All Currencies
To view all currencies navigate to:
```
http://127.0.0.1:8000/api/currency/
```
### View Latest Exchange Rate
To view latest exchange rate in database navigate to:
```
http://127.0.0.1:8000/api/currency/EUR/USD/
```
### Admin Interface
Admin interface available on:
```
http://127.0.0.1:8000/admin/
```
