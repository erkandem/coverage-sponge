"""
# coverage sponge

document your test coverage progress

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
"""
import bs4
from datetime import datetime as dt
import re
from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


COVERAGE_REPORT_PATH = 'htmlcov/index.html'
DATABASE_PATH = 'coverage_db.db'
Base = declarative_base()
footer_key = re.compile(r'created at ([0-9]{4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{2}:[0-9]{2})')


def select_where_module(module:str) -> str:
    return f'''
    SELECT * 
    FROM coverage_data 
    WHERE module = {module};
    '''


def select_modules() -> str:
    return '''SELECT DISTINCT module FROM coverage_data;'''


class CoverageRow(Base):
    __tablename__ = 'coverage_data'
    pk = Column(Integer, primary_key=True, autoincrement=True)
    dt = Column(String)
    module = Column(String)
    statements = Column(Integer)
    missing = Column(Integer)
    excluded = Column(Integer)
    branches = Column(Integer)
    partial = Column(Integer)
    coverage = Column(String)


def engine_factory():
    engine = create_engine(f'sqlite:///{DATABASE_PATH}')
    return engine


def session_factory(engine):
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    return session


def read_coverage_report(path) -> str:
    with open(path, 'r') as f:
        data = f.read()
    return data


def parse_coverage_report(data: str):
    soup = bs4.BeautifulSoup(data, 'lxml')
    footer = soup.find('div', {'id': 'footer'})
    ts = re.findall(footer_key, footer.text)[0]
    ts = dt.strptime(ts, '%Y-%m-%d %H:%M').isoformat()
    header = [th.text for th in soup.select('th')]
    rows = [[ts] + [td.text for td in tr.select('td')] for tr in soup.select('tr')]
    rows.pop(0)
    return header, rows, ts


def cast_new_data_to_dict(row):
    return dict(
        dt=row[0], module=row[1],
        statements=row[2], missing=row[3],
        excluded=row[4], branches=row[5],
        partial=row[6], coverage=row[7]
    )


def feed_report_to_db(session, rows):
    for row in rows:
        row_ = cast_new_data_to_dict(row)
        session.add(CoverageRow(**row_))
        session.commit()
    return


def main():
    data = read_coverage_report(COVERAGE_REPORT_PATH)
    header, rows, ts = parse_coverage_report(data)
    engine = engine_factory()
    session = session_factory(engine)
    Base.metadata.create_all(engine)
    feed_report_to_db(session, rows)
    session.close()
    engine.dispose()
    print(f'{dt.now()} | processed coverage data for {ts}')
    return


if __name__ == '__main__':
    main()
