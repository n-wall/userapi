## 简介
本目录包含用户、管理相关的API。
可能包含如下URL
```
GET,POST /me/token  获取，生成token
GET,POST,DELETE /me/ 获取，更改，删除meta
PUT /me/password 更改password

GET /admin/db 获取数据中的table名称
GET,POST,DELETE /admin/db/{tablename} 获取、更改、删除table中的内容

GET,POST /admin/user/ 获取、生成用户
GET,PUT,DELETE /admin/user/{email} 获取、更改、删除用户meta
GET /admin/user/token 列出所有用户的token
PUT /admin/user/{email}/meta 更改用户email的meta信息
PUT /admin/user/{email}/password 更改用户email的密码
```
