#!/bin/bash

script_path=$(realpath "$0")
script_dir=$(dirname "$script_path")
parent_dir=$(dirname "$script_dir")

script_name="rongxing_server.py"
# kill掉之前的进程
server_id=`ps -ef | grep  $script_name | grep  "$port"  | grep -v "grep" | awk '{print $2}'`
echo $server_id

for id in $server_id
do
    kill -9 $id
    echo "killed $id"
done

python -u $script_name "$port" >> "${script_dir}/log.log" 2>&1 &