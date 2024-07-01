#!/usr/bin/bash

cd /home/hadoop/data
chmod 744 mapper.py reducer.py
hadoop fs -mkdir -p input
hdfs dfs -put Train.csv input

hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.1.jar -D mapreduce.job.reduces=5 -file mapper.py -mapper "python3 mapper.py" -file reducer.py -reducer "python3 reducer.py" -input input -output output

