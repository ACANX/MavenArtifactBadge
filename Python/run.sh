#!/bin/bash
cd `dirname $0`
PATH=$PATH:/usr/local/bin
# 休眠随机时间0-99s
#sleep $[$RANDOM%100]
python3 PythonExec.py
echo "PythonExec.py script finished！"
