# apirouter , same as blueprint in flask

from pydantic import BaseModel

class Msg(BaseModel):
    msg: str
    price: float

from fastapi import APIRouter

router = APIRouter(
    prefix="/city",
)

from . import model

@router.get("/")
@router.get("/{page}")
async def get_cities(page:int=1): # get /3 和 get /?page=3 都可以
    per_page = 10
    query = model.City.select().paginate(page, per_page)
    data = [i.serialize for i in query]

    if data:
            res = {
                'cities': data,
                'meta': {'page': page, 'per_page': per_page,}# 'page_url': request.url}
                }
            return res
            res.status_code = 200
    else:
            # if no results are found.
            output = {
                "error": "No results found. Check url again",
                #"url": request.url,
            }
            res = output
            return res
            res.status_code = 404
    return res


@router.post("/path")
async def demo_post(inp: Msg):
    return {"message": inp.msg.upper(), "msg": inp}

