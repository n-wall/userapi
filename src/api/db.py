# base  config for database
import os

from peewee import *

if os.getenv('PLATFORM_NAME', '')=='RailWay':
    print("---------RailWay mysql: ", os.getenv('MYSQLHOST', '192.168.2.10'))
    #connector = MySQLDatabase(
    dbserver=dict(
        #'postgres',
        host=os.getenv('MYSQLHOST', '192.168.2.10'),
        port=int(os.getenv('MYSQLPORT', '3306')),
        database=os.getenv('MYSQLDATABASE', 'test'),
        user=os.getenv('MYSQLUSER', 'test'),
        password=os.getenv('MYSQLPASSWORD', 'test1234')
    )
else:
    try:
        from . import config
        print("-------config.py mysql: ", config.db['host'])
        #connector = MySQLDatabase(
        dbserver=dict(
            host=config.db['host'],
            port=config.db['port'],
            database=config.db['database'],
            user=config.db['user'],
            password=config.db['password'],
        )
    except Exception as e:
        print("----------- mysql: ", os.getenv('MYSQLHOST', '192.168.2.10'))
        #connector = MySQLDatabase(
        dbserver=dict(
            #'postgres',
            host=os.getenv('MYSQLHOST', '192.168.2.10'),
            port=int(os.getenv('MYSQLPORT', '3306')),
            database=os.getenv('MYSQLDATABASE', 'test'),
            user=os.getenv('MYSQLUSER', 'test'),
            password=os.getenv('MYSQLPASSWORD', 'test1234')
        )

#connector = MySQLDatabase(**dbserver)

# 也可以使用 url 形式的连接，
#    mysql://user:passwd@ip:port/my_db
#    postgresql://postgres:my_password@localhost:5432/my_database
# db = connect(os.environ.get('DATABASE') or 'sqlite:///default.db')

# MySQL服务器会自动踢掉idle的连接，因此可能在 web 型应用中造成错误
# http://docs.peewee-orm.com/en/latest/peewee/database.html#framework-integration

# 或者可以使用， https://github.com/coleifer/peewee/issues/1992#issuecomment-522322068
#from peewee import *
from playhouse.shortcuts import ReconnectMixin
class ReconnectMySQLDatabase(ReconnectMixin, MySQLDatabase):
    pass

connector = ReconnectMySQLDatabase(**dbserver)
