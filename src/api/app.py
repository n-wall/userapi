
import importlib
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 要关闭 /docs , /redoc 的测试api
app = FastAPI(
    title="南墙",
    #docs_url=None, redoc_url=None,
)

# CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#============== 静态文件 ==============
try:
    print("------------ static: ", __file__[0:-6]+"static")
    app.mount("/static", StaticFiles(directory=__file__[0:-6]+"static"), name="static")
except Exception as e:
    print(__name__, "load staticfile error: ", e)


#from fastapi.responses import FileResponse
#@app.get('/favicon.ico', include_in_schema=False)
#async def favicon():
#    return FileResponse(__file__[0:-6]+"static/favicon.png")

# =============== 用户模块 =============
mod=importlib.import_module (f"..auth.router_user", __name__)
app.include_router(
    mod.router,
    prefix='/api/v1/user'
)
mod=importlib.import_module (f"..auth.router_admin", __name__)
app.include_router(
    mod.router,
    prefix='/api/v1/admin'
)

# -------------------- 其它模块 -----
from . import urls

for modname, urlpath in urls.modules:
    # from .{modname} import router as mod
    mod=importlib.import_module (f"..{modname}.router", __name__)
    app.include_router(
        mod.router,
        prefix=urlpath
    )
    # 还可以有参数 , tags=["items"]



@app.get("/", tags=['帮助'])
async def root():
    import sys
    return {
        "message": "你好. Welcome to FastAPI!",
        "sponsor": "supported by railway",
        "module":__name__,
        "version": sys.version,
        "routers": [
            '/api/v1/city/<int:page>'+" 显示城市",
            '/api/v1/stock/<str:code or name>'+" 查询股票代码，名称信息",
        ]
    }

@app.get("/the/first/step/is/setup/database",
         include_in_schema=False,
         tags=['设置'])
async def setup_database():
    user=importlib.import_module (f"..auth.model", __name__)
    try:
        a=user._setup_db()
        return {"data": a}
    except Exception as e:
        return {"error": f"{e}"}
