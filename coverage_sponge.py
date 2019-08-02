"""
# coverage sponge

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
$ python post_coverage_script.py
```

assumes that
 - branch coverage is enabled
 - html report was created

things to set:
 1. path to coverage_report
 2. path to database
 4. table naming pattern ``coverage_20190802_0028``


"""
import bs4
import sqlite3
from datetime import datetime as dt

COVERAGE_REPORT_PATH = 'htmlcov/index.html'
DATABASE_PATH = 'coverage_db.db'


def read_coverage_report(path) -> str:
    with open(path, 'r') as f:
        data = f.read()
    return data


def parse_coverage_report(data: str):
    soup = bs4.BeautifulSoup(data, 'lxml')
    header = tuple(th.text for th in soup.select('th'))
    rows = [tuple(td.text for td in tr.select('td')) for tr in soup.select('tr')]
    rows.pop(0)  # first row is empty
    return header, rows


def create_table(table: str):
    return f'''
    CREATE TABLE {table}
    (
        module      text,
        statements  INTEGER, 
        missing     INTEGER, 
        excluded    INTEGER, 
        branches    INTEGER, -- may need your attention if turned off in .coveragec
        partial     INTEGER, 
        coverage    text
    );
    '''


def execute_create_table(con: sqlite3.Connection, table: str):
    sql = create_table(table)
    c = con.cursor()
    c.execute(sql)
    con.commit()
    c.close()
    return


def feed_report_to_db(con: sqlite3.Connection, table: str, rows):
    """ seven columns hard coded for simplicity """
    c = con.cursor()
    c.executemany(f'INSERT INTO {table} VALUES (?,?,?,?,?,?,?)', rows)
    con.commit()
    c.close()
    return


def main():
    time_stamp = dt.now().strftime('%Y%m%d_%H%M')
    table_name = f'coverage_{time_stamp}'
    data = read_coverage_report(COVERAGE_REPORT_PATH)
    header, rows = parse_coverage_report(data)
    with sqlite3.connect(DATABASE_PATH) as con:
        execute_create_table(con, table_name)
        feed_report_to_db(con, table_name, rows)
    return


if __name__ == '__main__':
    main()
