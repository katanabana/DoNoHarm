from sqlalchemy import create_engine, select
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker


class DB:
    server = "(localdb)\\server"
    password = ''
    login = ''
    driver = 'ODBC+Driver+17+for+SQL+Server'
    name = 'DB'
    url = 'mssql://@' + server + '/' + name + '?driver=' + driver + '&trusted_connection=yes'
    engine = create_engine(url)
    get_session = sessionmaker(engine)
    base = automap_base()
    base.prepare(engine)
    tables = base.classes

