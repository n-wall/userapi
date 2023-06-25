# a router for user support
#GET,POST /admin/user/ 获取、生成用户
#GET,PUT,DELETE /admin/user/{email} 获取、更改、删除用户meta
#GET /admin/user/token 列出所有用户的token
#PUT /admin/user/{email}/meta 更改用户email的meta信息
#PUT /admin/user/{email}/password 更改用户email的密码

from fastapi import APIRouter, Depends, HTTPException

from ..dependence import get_token_admin, _g

router = APIRouter(
    #prefix="/admin",
    tags=["用户管理"],
    dependencies=[Depends(get_token_admin)],
    responses={404: {"description": "Not found."}},
)

from pydantic import BaseModel
from typing import List

from . import model as user
from playhouse.shortcuts import model_to_dict, dict_to_model

@router.get("/user"
            )
async def list_user(start: int=0, limit: int=10):
    " 获取所有用户信息 "
    users=user.User.select().limit(limit).offset(start)
    data=[]
    for u in users:
        data.append(model_to_dict(u)) #.serialize)
    return {"data": data}

class User(BaseModel):
    email: str
    sex: str = 'M'
    kind: str = 'web'
    group: str = 'user'
    password: str
    token: str=''
    secret: str=''

@router.post('/user'
             )
async def create_user(inp: User):
    " 注册用户 "
    try:
        a=user.User.create(
            email=inp.email,
            sex=inp.sex,
            kind=inp.kind,
            group=inp.group,
            password=user.encrypted_passwd(inp.password),
        )
        if inp.token:
            tt=user.UserToken.create(
                token=inp.token,
                secret=inp.secret,
                timestamp=0,
                user=a
            )
    except Exception as e:
        return {"error": f"{e}"}
    return {"data": a.serialize}

@router.get("/user/{email}"
            )
async def get_user(email: str):
    "get user"
    me=user.User.get_or_none(user.User.email==email)
    if not me:
        return {"error": "User not found"}
    return {"data": me.serialize}

@router.delete("/user/{email}"
            )
async def delete_user(email: str):
    " 注销用户 "
    me=user.User.get_or_none(user.User.email==email)
    if me:
        me.delete_myself()
        #_g['me'].delete_myself()
        return {"OK": True}
    return {"error": "User not found"}


class UserPasswd(BaseModel):
    passwd: str

@router.put("/user/{email}/password"
            )
async def change_password(inp: UserPasswd, email: str):
    " 改变密码 "
    i=None
    if inp.passwd.strip():
        me=user.User.get_or_none(
            user.User.email==email)
        if me:
            me.password=user.encrypted_passwd(inp.passwd.strip())
            i=me.save() # i是影响的行数。1:表示改变了密码，0:密码相同
            #print(f"{__name__}: ", "changed passwd: ", i)
            return {"data": me.serialize, "flag": i}
        return {"error": "user not found"}
    return {"error": "empty password"}


class UserToken(BaseModel):
    token: str
    secret: str

@router.post("/user/{email}/token"
            )
async def create_usertoken(inp: UserToken, email: str):
    " 为用户 email 添加token "
    i=None
    me=user.User.get_or_none(
        user.User.email==email)
    if not me:
        return {"error": "user not found"}
    try:
        tt=user.UserToken.create(
            token=inp.token,
            secret=inp.secret,
            timestamp=0, #time.time(),
            user=me
        )
    except Exception as e:
        return {"error": f"{e}"}
    return {"data": tt.serialize}

#class UserGroup(BaseModel):
#    group: str
@router.post("/user/{email}/group/{group}"
            )
async def in_group(group: str, email: str):
    " 添加用户进组 "
    i=None
    me=user.User.get_or_none(
        user.User.email==email)
    if not me:
        return {"error": "invalid user"}
    gg=user.Group.get_or_none(
        user.Group.group==group)
    if not gg:
        return {"error": "invalid group"}
    a=user.UserGroup.get_or_none(
        user.UserGroup.group==gg,
        user.UserGroup.user==me
        )
    if a: # already in group
        return {"data": me.serialize}
    a=user.UserGroup.create(
        user=me, group=gg)
    return {"data": me.serialize}

@router.delete("/user/{email}/group/{group}"
            )
async def out_group(group: str, email: str):
    " 从组中删除用户 "
    i=None
    me=user.User.get_or_none(
        user.User.email==email)
    if not me:
        return {"error": "invalid user"}
    gg=user.Group.get_or_none(
        user.Group.group==group)
    if not gg:
        return {"error": "invalid group"}
    a=user.UserGroup.get_or_none(
        user.UserGroup.group==gg,
        user.UserGroup.user==me
        )
    if a: # already in group
        a.delete_instance()
        return {"OK": True}
    return {"error": "user group removed already"}


@router.get("/token"
            )
async def list_token(start: int=0, limit: int=10):
    " 获取所有 tokens "
    #if not _g['me']:
    #    return {"error": "非授权用户"}
    tokens=[]
    for tt in user.UserToken.select().offset(start).limit(limit):
        tokens.append(tt.serialize)
        #print(tt.serialize)
    return {"data": tokens}

@router.delete("/token/{tokenkey}"
            )
async def delete_token(tokenkey: str):
    " 删除token "
    tt = user.UserToken.get_or_none(
        user.UserToken.token==tokenkey)
    if not tt:
        return {"error": "token not exist"}
    tt.delete_instance()
    return {"OK": True}


    
@router.get("/group"
            )
async def list_group(start: int=0, limit: int=10):
    " 删除group "
    data=[]
    for tt in user.Group.select().offset(start).limit(limit):
        data.append(tt.serialize)
    return {"data": data}

class Group(BaseModel):
    group: str
    info: str
@router.post("/group"
             )
async def create_group(inp: Group):
    " create new group "
    tt = user.Group.get_or_none(
        user.Group.group==inp.group)
    if tt:
        #tt.info=inp.info
        #tt.save()
        return {"error": "group already exist"}
    tt=user.Group.create(
        group=inp.group,
        info=inp.info
        )
    return {"data": tt.serialize}
    
@router.get("/group/{group}"
            )
async def get_group(group: str):
    " 删除group "
    tt = user.Group.get_or_none(
        user.Group.group==group)
    if not tt:
        return {"error": "group not exist"}
    return {"data": tt.serialize}

@router.delete("/group/{group}"
            )
async def delete_group(group: str):
    " 删除group "
    tt = user.Group.get_or_none(
        user.Group.group==group)
    if not tt:
        return {"error": "group not exist"}
    rows=tt.delete_myself()
    return {"OK": True, 'rows': rows,
            'message': "'rows'中是同时删除的其它表中的数据"}

    
@router.get("/group/{group}/user"
            )
async def get_group_user(group: str):
    " 获取group中的用户 "
    tt = user.Group.get_or_none(
        user.Group.group==group)
    if not tt:
        return {"error": "group not exist"}
    data=[]
    for uu in tt.users:
        # type(uu) : UserGroup
        #print(uu.user, type(uu))
        data.append(model_to_dict(uu.user))
    return {"data": data}
