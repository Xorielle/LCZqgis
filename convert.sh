#!/usr/bin/env bash

input="ete.txt"
output="ete.csv"

cp $input $output

#sed -i -e "s/,/./g" -e "s/;/,/g" -e "s/,$/,0/g" $output
sed -i -e "s/,/./g" -e "s/;/,/g" $output

echo Done