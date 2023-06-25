# 依赖项
#   将需要一些在应用程序的好几个地方所使用的依赖项。
#   放在它们自己的 dependence 模块（app/dependence.py）中。


from fastapi import Header, HTTPException

from .auth import model as user

_g={"me": None}

# 用token header来得到有效用户
async def get_token_user(token: str = Header()):
    #me = user.User.get_or_none(user.User.email==token)
    #if me:
    #    _g['me']=me
    #    return True
    #else:
    #    raise HTTPException(status_code=400, detail="Token invalid")
    tokens=token.split(",", 2)
    if len(tokens) != 3:
        raise HTTPException(status_code=400, detail="Token format invalid")
    me = user.get_user_from_token(tokens[0], tokens[1], tokens[2])
    if me:
        _g['me'] = me
    else:
        raise HTTPException(status_code=400, detail="Token invalid")


# 用token header来得到有效超级用户
async def get_token_admin(token: str = Header()):
    #me = user.User.get_or_none(1)
    #_g['me']=me
    #return True
    tokens=token.split(",")
    if len(tokens) != 3:
        raise HTTPException(status_code=400, detail="Token format invalid")
    me = user.get_user_from_token(tokens[0], tokens[1], tokens[2])
    if me:
        _g['me'] = me
    else:
        raise HTTPException(status_code=400, detail="Token invalid")

    # if use is admin, or in admin group
    if me.email=='Admin': # admin
        return True
    if me.group == 'admin': # in admin group
        return True
    for g in me.groups:
        if g.group.group == 'admin': # in admin group
            return True
    # else not admin
    raise HTTPException(status_code=400, detail="Not admin user")
