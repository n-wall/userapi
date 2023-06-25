#import os
from peewee import *

from .. import db
sql_db = db.connector
#MySQLDatabase(
#    #'postgres',
#    host=os.getenv('MYSQLHOST', '192.168.2.10'),
#    port=int(os.getenv('MYSQLPORT', '3306')),
#    database=os.getenv('MYSQLDATABASE', 'test'),
#    user=os.getenv('MYSQLUSER', 'test'),
#    password=os.getenv('MYSQLPASSWORD', 'test1234')
#)

class BaseModel(Model):

    class Meta:
        database = sql_db
        #db_table = 'city'
        #table_alias = 'c'


class City(BaseModel):
    id = PrimaryKeyField(null=False)
    name = CharField(max_length=35)
    countrycode = CharField(max_length=3)
    district = CharField(max_length=20)
    population = BigIntegerField()

    @property
    def serialize(self):
        data = {
            'id': self.id,
            'name': str(self.name).strip(),
            'countrycode': str(self.countrycode).strip(),
            'district': str(self.district).strip(),
            'population': self.population,
        }

        return data

    def __repr__(self):
        return "{}, {}, {}, {}, {}".format(
            self.id,
            self.name,
            self.countrycode,
            self.district,
            self.population
        )
