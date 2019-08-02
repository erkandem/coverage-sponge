# coverage-sponge

save your test coverage statstics for later

## The Case
Coverage offers a great summary inside ``index.html`` after generating
html reports. This script takes the records of the html table and
inserts each row to a sqlite database.

Later on you could (e.g.) create (timestamp, coverage rate) plots.
(Query tool is under construction)

## Usage
The idea is to run the script after each successful test run
with coverage and report generation.

assuming ``src`` is your main module and your tests are in ``tests/``

```bash
$ pytest --cov=src --cov-branch  tests/
$ coverage html
$ python coverage_sponge.py
```

assumes that
 - branch coverage is enabled
 - html report was created

things to set:
 1. path to coverage_report
 2. path to database
 4. table naming pattern ``coverage_20190802_0028``


"""
