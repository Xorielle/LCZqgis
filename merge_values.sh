#!/usr/bin/env bash

input="Data1.csv"
original="Data2.csv"
output="Data2_generated.csv"

cp $original $output
increment=0

while IFS= read -r line; do
    increment=$((increment+1))
    if [[ $increment -eq 1 ]]; then
        continue
    fi
    sed -i -e "$((increment))s/,,/,$(echo $line | cut -d',' -f8),/" $output
done < $input

echo Done