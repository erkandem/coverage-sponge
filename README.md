# coverage-sponge

save your test coverage statstics for later

## The Case
``Coverage`` offers a simple but great summary inside ``index.html``
after generating html reports. This script takes these records and
inserts them into a sqlite database.

Later on you could  create (timestamp, coverage rate) plots.
(Query tool is under construction)

## Usage
The idea is to run the script after each successful test run
with coverage and report generation.

assuming ``src`` is your main module and your tests are in ``tests/``

```bash
$ pytest --cov=pym --cov-branch  tests/
$ coverage html
$ python coverage_sponge.py
$ firefox "$(pwd)/htmlcov/index.html"
```

assumes that
 - branch coverage is enabled
 - html report was created

things to set:
 1. path to coverage_report
 2. path to database

Different project: https://github.com/openstack/coverage2sql
