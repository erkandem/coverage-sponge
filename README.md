# coverage-sponge

save your test coverage statstics for later and plot them.

## The Case
``Coverage`` offers a simple but great summary inside ``index.html``
after generating html reports. This script takes these records and
inserts them into a sqlite database.

Later on you could  create (timestamp, coverage rate) plots.

## Usage
The idea is to run the script after each successful test run
with coverage and report generation.

assuming ``src`` is your main module and your tests are in ``tests/``
### run your tests
```bash
$ pytest --cov=pym --cov-branch  tests/
```
### create the coverage report
```bash
$ coverage html
$ firefox "$(pwd)/htmlcov/index.html"
```
### run the parser
```bash
$ python coverage_sponge.py
```

### plot your results
Run the viz module if you collected some history of coverage data 
```bash
$ python coverage_plotting.py
```

![sample](sample.png)
> Is he? Is he trying to gamify testing? No! You must not enjoy testing!


Different project: https://github.com/openstack/coverage2sql
