Code structure
==============
Used https://docs.python-guide.org/writing/structure/

Code conventions
================
Used [PEP-08](https://www.python.org/dev/peps/pep-0008/) and pylint


Instructions
============
Python version used: 3.8

1. __Recommended:__ create a virtual environment
    ```bash
    python3 -m venv ~/venv 
    ```
    Activate it
    ```bash
     source ~/venv/bin/activate 
    ```
2. Install dependencies
    ```bash
    python setup.py develop
    ```
3. Run tests
    ```bash
    python -m unittest discover
    ```
4. Run test coverage
    ```bash
    coverage run -m unittest discover
    ```
5. Run report
    ```bash
    coverage report -m
    ```
6. Run each step independently
    ```bash
    python sequra/app.py
    ```

 7 Go to http://localhost:8888/

Exercises assumptions
=================
* __disbursements per merchant per week__ is calculated adding up all the purchases for the given week plus all the 
fees of the mentioned purchases
* __Rounding__ in currency operations is set to ROUND_HALF_UP
* > Create the necessary data structures and a way to persist __them__ for the provided data. You don't have to follow our schema if you think another one suits better.

  The word *Them* refers to data structures, data structures can not be persisted, only data. I think it refers to "The merchant data" mentioned later so I loaded them as a database seed
* > calculations can take some time it should be isolated and be able to run independently of a regular web request
  
  Why the concept of calculation and request are in the same paragraph?, are they linked?. I understand so, therefore I created a end point to initialize the calculation and another to retrieve the data
  

 
Technical choices
=================
* __Web framework__: Flask 
    * _Pros_: 
        * Fine grain tune of modularity, _"use what only you need"_
        * Reduce development time
    * _Cons_:
        * Requires WSGI to [run in production](https://flask.palletsprojects.com/en/1.1.x/deploying/#deployment)
        * Manual wiring with modules
        * Async functionality not built-in
* __Database__: Sqlite 
    * _Pros_:
        * No require external dependencies
        * Allows isolation transaction
        * Faster development time
    * _Cons_:
        * Primitive syntax and formatting limitations
        * Harder to monitor performance
* __Currency__: Decimal
    * _Pros_:
        * Built-in implementation
        * Exactness carries over into arithmetic
    * _Cons_:
        * sqlLite does not support Decimal
        * Does not contains currency information as [money external package](https://pypi.org/project/money/)
* __Async event__: [sqlalchemy event](https://docs.sqlalchemy.org/en/13/core/event.html)
    * _Pros_:
        * Built-in in SQLAlchemy package it doesn't require to create a new db session
        * Does not require external dependency as [Celery](https://flask.palletsprojects.com/en/1.1.x/patterns/celery/)
    * _Cons_:
        * Maintainability to keep sync consistency
        * Harder to test and debug than a Celery task
* __Scheduling__: [flask-crontab](https://pypi.org/project/flask-crontab/)
    * _Pros_:
        * Easier to test
    * _Cons_:
        * Crontab is not aware of SQLAlchemy context, it requires to initialize it.
        
TODO
----
* Scheduling: Using mentioned package to traverse all `Merchant` rows and calculate the _disbursed amount_ as calling endpoint `/calculate_disbursement`
_____
_____

# Feedback
* Not require to load the seed data
* Event system does not notify inconsistency in data, :| *why should I require consistency if data is loaded correctly?*
* __disbursements per merchant per week__ only needs to calculate the Fees, not requires the purchase amount

# Backend coding challenge
This is the coding challenge for people who applied to a backend developer position at SeQura. It's been designed to be a simplified version of the same problems we deal with.

## The challenge
SeQura provides ecommerce shops (merchants) a flexible payment method so their customers (shoppers) can purchase and receive goods without paying upfront. SeQura earns a small fee per purchase and pays out (disburse) the merchant once the order is marked as completed.

The operations manager is now asking you to make a system to calculate how much money should be disbursed to each merchant based on the following rules:

* Disbursements are done weekly on Monday.
* We disburse only orders which status is completed.
* The disbursed amount has the following fee per order:
  * 1% fee for amounts smaller than 50 €
  * 0.95% for amounts between 50€ - 300€
  * 0.85% for amounts over 300€

We expect you to:

* Create the necessary data structures and a way to persist them for the provided data. You don't have to follow our schema if you think another one suits better.
* Calculate and persist the disbursements per merchant on a given week. As the calculations can take some time it should be isolated and be able to run independently of a regular web request, for instance by running a background job.
* Create an API endpoint to expose the disbursements for a given merchant on a given week. If no merchant is provided return for all of them.

Find attached the merchants (https://www.dropbox.com/s/wms8dlqzs6bqkul/backend%20challenge%20dataset.zip?dl=0), shoppers and orders data on both json and csv files, use whatever it's easier for you. They follow this structure:

### MERCHANTS

```
ID | NAME                      | EMAIL                             | CIF
1  | Treutel, Schumm and Fadel | info@treutel-schumm-and-fadel.com | B611111111
2  | Windler and Sons          | info@windler-and-sons.com         | B611111112
3  | Mraz and Sons             | info@mraz-and-sons.com            | B611111113
4  | Cummerata LLC             | info@cummerata-llc.com            | B611111114
```

### SHOPPERS

```
ID | NAME                 | EMAIL                              | NIF
1  | Olive Thompson       | olive.thompson@not_gmail.com       | 411111111Z
2  | Virgen Anderson      | virgen.anderson@not_gmail.com      | 411111112Z
3  | Reagan Auer          | reagan.auer@not_gmail.com          | 411111113Z
4  | Shanelle Satterfield | shanelle.satterfield@not_gmail.com | 411111114Z
```

### ORDERS

```
ID | MERCHANT ID | SHOPPER ID | AMOUNT | CREATED AT           | COMPLETED AT
1  | 25          | 3351       | 61.74  | 01/01/2017 00:00:00  | 01/07/2017 14:24:01
2  | 13          | 2090       | 293.08 | 01/01/2017 12:00:00  | nil
3  | 18          | 2980       | 373.33 | 01/01/2017 16:00:00  | nil
4  | 10          | 3545       | 60.48  | 01/01/2017 18:00:00  | 01/08/2017 15:51:26
5  | 8           | 1683       | 213.97 | 01/01/2017 19:12:00  | 01/08/2017 14:12:43
```

## Instructions
* Please read carefully the challenge and if you have any doubt or need extra info please don't hesitate to ask us before starting.
* You shouldn't spend more than 3h on the challenge.
* Design, test, develop and document the code. It should be a performant, clean and well structured solution. Then send us a link or a zip with a git repo.
* You should consider this code ready for production as it were a PR to be reviewed by a colleague. Also commit as if it were a real assignment.
* Remember you're dealing with money, so you should be careful with related operations.
* Create a README explaining how to setup and run your solution and a short explanation of your technical choices, tradeoffs, ...
* You don't need to finish. We value quality over feature-completeness. If you have to leave things aside you can mention them on the README explaining why and how you would resolve them.
* You can code the solution in a language of your choice, here are some technologies we are more familiar with (no particular order): JavaScript, Ruby, Python, Go, Elixir, Java, Scala, PHP.
* Your experience level will be taken into consideration when evaluating.

**HAPPY CODING!!**
