#! /bin/bash

/etc/init.d/cron start
jupyter notebook --no-browser --allow-root --ip=0.0.0.0 --port=8888 --NotebookApp.token=''
