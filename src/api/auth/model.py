# a model for User
#import os
from peewee import *

from .. import db
sql_db = db.connector

class BaseModel(Model):

    class Meta:
        database = sql_db
        #db_table = 'city'
        #table_alias = 'c'


class User(BaseModel):
    class Meta:
        table_name = 'auth_user'
    id = PrimaryKeyField(null=False)
    email = CharField(max_length=10, unique=True) # 用户名
    password = CharField(max_length=150) # 加密后的密码
    sex = CharField(max_length=15) # 性别
    kind = CharField(max_length=15) # 用户类型
    group = CharField(max_length=150) # 所属群组
    # groups - map to UserGroup
    # meta - map to UserMeta
    # info - map to UserInfo
    # token - map to UserToken

    @property
    def serialize(self):
        data = dict(
            #'id': self.id,
            email = self.email.strip(),
            #password = self.password.strip(),
            sex = self.sex.strip(),
            kind = self.kind.strip(),
            group = self.group.strip(), #split(','),
        )
        data['groups']=[]
        #print(dir(self.groups))
        for g in self.groups:
            data['groups'].append(g.group.group)
        data['info']={}
        for g in self.info:
            data['info'].update({g.name: g.value})
        data['meta']={}
        for g in self.meta:
            if g.name in data['meta']:
                data['meta'][g.name].append(g.value)
            else:
                data['meta'][g.name]=[g.value]

        return data

    def delete_myself(self):
        query=UserInfo.delete().where(
            UserInfo.user==self)
        rows1=query.execute()
        query=UserMeta.delete().where(
            UserMeta.user==self)
        rows2=query.execute()
        query=UserToken.delete().where(
            UserToken.user==self)
        rows3=query.execute()
        query=UserGroup.delete().where(
            UserGroup.user==self)
        rows4=query.execute()
        self.delete_instance()
        return [rows1,rows2,rows3,rows4]

class UserToken(BaseModel):
    class Meta:
        table_name = 'auth_token'
        #indexes=(
        #    (('user', 'name'), True), # a unique on lei+season
        #)
    id = PrimaryKeyField(null=False)
    token = CharField(max_length=150, unique=True)
    secret = CharField(max_length=150)
    timestamp = DoubleField() # TimestampField() #DateTimeField()
    user = ForeignKeyField(User, backref='token')
    # 重构 save 方法
    #def save(self, *args, **kwargs):
    #    self.timestamp = datetime.datetime.now()
    #    super(UserToken, self).save(*args, **kwargs)
    @property
    def serialize(self):
        data = dict(
            #'id': self.id,
            email = self.user.email.strip(),
            #password = self.password.strip(),
            token = self.token.strip(),
            secret = self.secret.strip(),
        )
        return data

# info 中，每个用户只有一个。
#  如： 一个用户有一个nickname, First Name, Last Name等
class UserInfo(BaseModel):
    class Meta:
        table_name = 'user_info'
        indexes=(
            (('user', 'name'), True), # a unique on lei+season
        )
    id = PrimaryKeyField(null=False)
    name = CharField(max_length=10)
    value = CharField(max_length=150)
    user = ForeignKeyField(User, backref='info')
    

# meta 中，每个用户可以有多个。
#   如： 一个用户可以有多个 Email
class UserMeta(BaseModel):
    class Meta:
        table_name = 'user_meta'
        indexes=(
            (('name', 'value'), True), # a unique on lei+season
        )
    id = PrimaryKeyField(null=False)
    name = CharField(max_length=10)
    value = CharField(max_length=150)
    user = ForeignKeyField(User, backref='meta')
    

class Group(BaseModel):
    class Meta:
        table_name = 'group_info'
    id = PrimaryKeyField(null=False)
    group = CharField(max_length=10, unique=True) # 组名
    info = TextField() # 描述
    #priv = TextField # 权限
    @property
    def serialize(self):
        data = dict(
            group = self.group.strip(),
            info = self.info,
        )
        return data
    
    def delete_myself(self):
        query=UserGroup.delete().where(
            UserGroup.group==self)
        rows=query.execute()
        self.delete_instance()
        return [rows]

class UserGroup(BaseModel):
    class Meta:
        table_name = 'user_group'
        indexes=(
            (('user', 'group'), True), # a unique on lei+season
        )
    id = PrimaryKeyField(null=False)
    user = ForeignKeyField(User, backref='groups')
    group = ForeignKeyField(Group, backref='users')

#====================================================================
# 辅助函数
# return encryed password
import hashlib
def encrypted_passwd(password):
    m = hashlib.md5()
    m.update(password.encode("utf-8"))
    #print("---- encrypted password: "+password+" to: "+m.hexdigest())
    return m.hexdigest()
def _sig(token, timestamp, sec):
    m = hashlib.md5()
    mstr = "%s,%s,%s"%(token, timestamp, sec)
    m.update(mstr.encode('utf-8'))
    return m.hexdigest()
    
# get user model from token
#   return user model or False
def get_user_from_token(token, timestamp, signature):
    " get user by token "
    if not token:
        print (f"{__name__}: token为空")
        return False
    data = UserToken.get_or_none(UserToken.token==token)
    #print(data)
    if not data:
        print (f"{__name__}: 无效token ")
        return False
    print(data.timestamp, '-', timestamp)
    #data=data.dict()
    try:
        if data.timestamp >= float(timestamp):
            print (f"::::{__name__} ---- : 过期的 timestamp")
            return False
    except Exception as e:
        print (f":::::{__name__} ------: timestamp error", e)
        return False
    # signature
    if _sig(token, timestamp, data.secret) == signature:
        data.timestamp = float(timestamp)
        data.save()
        #dbclient.put(data) # update time_stamp of this token
        user = data.user
        print (f"=============={__name__}: found user with email '{user.email}' ",
               type(user),
               #user.groups,
               user.serialize,
               )
        # convert user into dict
        return user
    print (f"----{__name__}:", " bad signature")
    return False



# 初始化数据表格，加入admin用户
def _setup_db():
    import time
    sql_db.create_tables([User, UserInfo, UserMeta, UserToken, Group, UserGroup], safe=True)

    print("-- table created")
    admin = User.create(
        email="Admin@hello.world",
        password=encrypted_passwd('I.love.China'),
        sex='God',
        kind='admin',
        group='admin',
        )
    UserInfo.create(
        user=admin,
        name='nickname',
        value='管理员',
        )
    UserMeta.create(
        user=admin,
        name='QQ',
        value='12345',
        )
    print("-- admin user created")
    tt=UserToken.create(
        user=admin,
        token='admin',
        secret='ustc.is.the.best',
        timestamp= time.time(), #datetime.datetime.now(),
        )
    print("-- admin token created")
    leader=Group.create(
        group='admin',
        info='管理员，有一切权限'
        )
    Group.create(
        group='user',
        info='普通用户'
        )
    Group.create(
        group='guest',
        info='访客'
        )
    Group.create(
        group='teacher',
        info='教师',
        )
    UserGroup.create(
        user=admin,
        group=leader
        )
    print("-- groups: user, admin, teacher created")
    return {"admin": admin.serialize, "token": tt.serialize}
