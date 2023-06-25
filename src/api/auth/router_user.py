# a router for user support
#GET,POST /me/token  获取，生成token
#GET,POST,DELETE /me/ 获取，更改，删除meta
#PUT /me/password 更改password

from fastapi import APIRouter, Depends, HTTPException

from ..dependence import get_token_user, _g

router = APIRouter(
    #prefix="/me",
    tags=["用户"],
    dependencies=[Depends(get_token_user)],
    responses={404: {"description": "Not found."}},
)

from pydantic import BaseModel
from typing import List

from . import model as user

@router.get("/me"
            )
async def my_account():
    " 获取帐号信息 "
    if not _g['me']:
        return {"error": "非授权用户"}
    return {"data": _g['me'].serialize}

class UserMeta(BaseModel):
    name: str
    value: str

class Information(BaseModel):
    info: List[UserMeta]=[]
    meta: List[UserMeta]=[]
    
@router.post("/me"
            )
async def update_account(inp: Information):
    """ 更新帐号信息。
输入如：
{
  "info": [{"name": "nickname", "value": "我最牛"}],
  "meta": [{"name": "QQ", "value": "456890"}]
}
 """
    if not _g['me']:
        return {"error": "非授权用户"}
    for info in inp.info:
        binsert=True
        for i in _g['me'].info:
            if i.name==info.name:
                #print('found key: ', i.name)
                if i.value != info.value:
                    #print(f"{__name__}: ", " update key")
                    i.value=info.value
                    i.save()
                binsert=False
                break
        if binsert: # not found key, insert
            #print(f"{__name__}: ", "insert new info")
            i=user.UserInfo.create(
                name=info.name,
                value=info.value,
                user=_g['me']
                )
    for info in inp.meta:
        meta=user.UserMeta.get_or_none(
            user.UserMeta.name==info.name,
            user.UserMeta.value==info.value)
        if meta:
            #print(f"{__name__}: meta alread in", meta)
            continue
        #print(f"{__name__}: ", "insert new meta")
        i=user.UserMeta.create(
            name=info.name,
            value=info.value,
            user=_g['me']
        )
        #print(info)
    return {"data": _g['me'].serialize}

@router.delete("/me"
            )
async def delete_myself():
    " 注销自己 "
    #query=user.UserInfo.delete().where(
    #    user.UserInfo.user==_g['me'])
    #rows=query.execute()
    #query=user.UserMeta.delete().where(
    #    user.UserMeta.user==_g['me'])
    #rows=query.execute()
    #query=user.UserToken.delete().where(
    #    user.UserToken.user==_g['me'])
    #rows=query.execute()
    #query=user.UserGroup.delete().where(
    #    user.UserGroup.user==_g['me'])
    #rows=query.execute()
    #_g['me'].delete_instance()
    #_g['me'].delete_myself
    return {"OK": True, "message": "代码生成中..."}


@router.get("/me/token"
            )
async def my_token():
    " 获取所有 tokens "
    #if not _g['me']:
    #    return {"error": "非授权用户"}
    tokens=[]
    for tt in _g['me'].token:
        tokens.append(tt.serialize)
        #print(tt.serialize)
    return {"data": tokens}

class UserToken(BaseModel):
    token: str
    secret: str

#import time
@router.post("/me/token"
            )
async def update_token(inp: UserToken):
    " 更改token的secret，或者增加一个 token "
    token=user.UserToken.get_or_none(
        user.UserToken.token==inp.token)
    if token:
        if token.user != _g['me']:
            return {"error": "token owned by other user"}
            #print(f"{__name__}: meta alread in", meta)
        if token.secret!= inp.secret.strip():
            token.secret= inp.secret.strip()
            token.save()
        return {"data": token.serialize}
    # need to insert new token
    token=user.UserToken.create(
        token=inp.token, secret=inp.secret,
        timestamp=0, #time.time(),
        user=_g['me']
    )
    return {"data": token.serialize}


@router.delete("/me/token/{tokenkey}"
            )
async def delete_token(tokenkey: str):
    " 删除token的secret，或者增加一个 token "
    tt=user.UserToken.get_or_none(
        user.UserToken.token==tokenkey)
    #print(f"{__name__}: ", "token key, ", tokenkey)
    if tt:
        if tt.user != _g['me']:
            return {"error": "token owned by other user"}
            #print(f"{__name__}: meta alread in", meta)
        tt.delete_instance()
        return {"OK": True}
    return {"error": "无效token"}

class UserPasswd(BaseModel):
    passwd: str

@router.put("/me/password"
            )
async def change_password(inp: UserPasswd):
    " 改变密码 "
    i=None
    if inp.passwd.strip():
        _g['me'].password=user.encrypted_passwd(inp.passwd.strip())
        i=_g['me'].save() # i是影响的行数。1:表示改变了密码，0:密码相同
        print(f"{__name__}: ", "changed passwd: ", i)
    return {"data": _g['me'].serialize, "flag": i}



#@router.patch(
#    "/me/{item_id}",
#    tags=["custom"],
#    responses={403: {"description": "Operation forbidden"}},
#)
#async def update_item(item_id: str):
#    if item_id != "plumbus":
#        raise HTTPException(
#            status_code=403, detail="You can only update the item: plumbus"
#        )
#    return {"item_id": item_id, "name": "The great Plumbus"}
