#!/usr/bin/env bash
input="Data2.txt"
output="Data2.csv"

cp $input $output

#sed -i -e "s/,/./g" -e "s/;/,/g" -e "s/,$/,0/g" $output
sed -i -e "s/,/./g" -e "s/;/,/g" $output