#! /bin/bash
# 包含 生成 auth token 需要的函数

#! /bin/bash

# a api for test with user authorization
host="http://localhost:8000"
proxy=""
#"--socks5 192.168.2.10:7880"

# -f --fail, no output on server errors
# -s , do not show progress and errors
# --show-error , will show errors even with -s option
curlopt="-s --fail-with-body"

tokenstr=`cat client.token`
#echo $tokenstr
tokens=(${tokenstr//,/ })
token=${tokens[0]}
pass=${tokens[1]}
echo ${token} ' -- ' ${pass}
# a signature , sig timestamp token sec
sig() {
  #timestamp=`date +%s.%N`
  sig="$2","$1","$3"
  #echo $sig
  signature=`echo -n $sig | md5sum |cut -d" " -f1`
  echo "$2,$1,$signature"
}

# post path params..
get() {
  timestamp=`date +%s.%N`
  sig=$(sig $timestamp $token $pass)
  #echo $sig
  path=$1
  shift;
  #echo $@
  params=""
  for learn in $@
  do  
    params="$params --data-urlencode $learn  "
  done
  # curl --get -d "tool=curl" -d "age=old" https://example.com
  # --get 把 -d 的内容编码后作为 querystring
  result=`curl $curlopt $proxy -H 'Token: '${sig} \
    --get $params ${host}$path
`
  #echo "$host/$path"
  # 利用 jq 解析得到的 JSON 结果中的id
  echo $result
}


# post path params..
post() {
  timestamp=`date +%s.%N`
  sig=$(sig $timestamp $token $pass)
  #echo $sig
  path=$1
  shift;
  #echo $@
  params=""
  for learn in $@
  do  
    params="$params --data $learn  "
  done
  result=`curl  $curlopt $proxy \
    -H 'Token: '${sig} \
    -X POST \
    $params ${host}$path
`
  #echo "$host/$path"
  # 利用 jq 解析得到的 JSON 结果中的id
  echo $result
}

put() {
  timestamp=`date +%s.%N`
  sig=$(sig $timestamp $token $pass)
  #echo $sig
  path=$1
  shift;
  #echo $@
  params=""
  for learn in $@
  do  
    params="$params --data $learn  "
  done 
  result=`curl  $curlopt  $proxy \
    -H 'Token: '${sig} \
    -X PUT \
    $params ${host}$path
`
  # 利用 jq 解析得到的 JSON 结果中的id
  echo $result
}

patch() {
  timestamp=`date +%s.%N`
  sig=$(sig $timestamp $token $pass)
  #echo $sig
  path=$1
  shift;
  #echo $@
  params=""
  for learn in $@
  do  
    params="$params --data $learn  "
  done 
  result=`curl  $curlopt  $proxy \
    -H 'Token: '${sig} \
    -X PATCH \
    $params ${host}$path
`
  # 利用 jq 解析得到的 JSON 结果中的id
  echo $result
}

delete() {
  timestamp=`date +%s.%N`
  sig=$(sig $timestamp $token $pass)
  #echo $sig
  path=$1
  shift;
  #echo $@
  params=""
  for learn in $@
  do  
    params="$params --data $learn  "
  done 
  result=`curl  $curlopt  $proxy \
    -H 'Token: '${sig} \
    -X DELETE \
    ${host}$path
`
  # 利用 jq 解析得到的 JSON 结果中的id
  echo $result
}

postjson() {
  timestamp=`date +%s.%N`
  sig=$(sig $timestamp $token $pass)
  #echo $sig
  path=$1
  shift;
  #echo $@
  params=("$@")
  #echo $params
  #for learn in $@
  #do  
  #  params="$params --data $learn  "
  #done
  result=`
  curl  $curlopt $proxy -X 'POST'\
    -H 'Token: '${sig} \
    -H 'Content-Type: application/json' \
    ${host}$path \
    -d "${params[*]}"
`
  #echo "$host/$path"
  # 利用 jq 解析得到的 JSON 结果中的id
  echo $result
}

putjson() {
  timestamp=`date +%s.%N`
  sig=$(sig $timestamp $token $pass)
  #echo $sig
  path=$1
  shift;
  #echo $@
  params=("$@")
  #echo $params
  #for learn in $@
  #do  
  #  params="$params --data $learn  "
  #done
  result=`
  curl  $curlopt $proxy -X 'PUT'\
    -H 'Token: '${sig} \
    -H 'Content-Type: application/json' \
    ${host}$path \
    -d "${params[*]}"
`
  #echo "$host/$path"
  # 利用 jq 解析得到的 JSON 结果中的id
  echo $result
}


patchjson() {
  timestamp=`date +%s.%N`
  sig=$(sig $timestamp $token $pass)
  #echo $sig
  path=$1
  shift;
  #echo $@
  params=("$@")
  #echo $params
  #for learn in $@
  #do  
  #  params="$params --data $learn  "
  #done
  result=`
  curl  $curlopt $proxy -X 'PATCH'\
    -H 'Token: '${sig} \
    -H 'Content-Type: application/json' \
    ${host}$path \
    -d "${params[*]}"
`
  #echo "$host/$path"
  # 利用 jq 解析得到的 JSON 结果中的id
  echo $result
}

decodejson(){
  echo $1 | \
    python3 -c '
import json, sys
try:
  obj=json.load(sys.stdin)
  print(json.dumps(obj, indent=2, ensure_ascii=False))
except Exception as e:
  print("Not a json data, ", e)
'
}

#recs=`get //api/v1/admin/db/a/b/c/d/e`
#echo $recs
#decodejson $recs

#post /api/v1/admin/db/aToken?newkind=true @token.json
#put user/a@b.com/info 'a=3' 'b=4' 'b=6'
#patch user/a@b.com/info 'a=3' 'b=4' 'b=6'


