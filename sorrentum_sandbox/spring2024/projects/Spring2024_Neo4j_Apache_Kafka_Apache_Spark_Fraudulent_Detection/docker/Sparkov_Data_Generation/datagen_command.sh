#!/bin/bash
cd /app/Sparkov_Data_Generation
first_month=$(expr $(cat month.txt) + 0)
if [ $first_month -eq 12 ]; then
	first_month=1
fi
second_month=$(expr $first_month + 1)
echo Running from $first_month-01-2024 to $second_month-01-2024
/usr/local/bin/python3 datagen.py -o output -c output/customers.csv $first_month-01-2024 $second_month-01-2024
echo $second_month > month.txt
