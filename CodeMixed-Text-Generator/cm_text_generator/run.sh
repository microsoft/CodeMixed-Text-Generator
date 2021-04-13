#!/bin/bash

inpfile=$1
outfile=$2
source_lang=$3
target_lang=$4
errfile=$1.err
# echo $inpfile
rm -f one_tweet-${source_lang}-${target_lang}.txt
rm -f $outfile
count=0

echo $inpfile
echo $outfile
while read -r line || [[ -n $line ]]; do
	# echo $line
	if [ "$line" != "" ]; then
		echo "$line" >> one_tweet-${source_lang}-${target_lang}.txt
	else
		count=$[count+1]
		if [[ $(($count % 500)) -eq 0 ]]
			then
				echo "Generating: "$count
		fi
		# cat one_tweet.txt
		# echo ""
		cat one_tweet-${source_lang}-${target_lang}.txt >> $outfile
		timeout -k 1s 1s python -m cm_text_generator.generator.bench one_tweet-${source_lang}-${target_lang}.txt $outfile 2>> $errfile
		# python bench.py one_tweet-${source_lang}-${target_lang}.txt >> $outfile 2>> $errfile
		echo '' >> $outfile
		rm one_tweet-${source_lang}-${target_lang}.txt
	fi

done < $inpfile

cat one_tweet-${source_lang}-${target_lang}.txt >> $outfile
timeout -k 1s 1s python -m cm_text_generator.generator.bench one_tweet-${source_lang}-${target_lang}.txt $outfile 2>> $errfile
# python bench.py one_tweet-${source_lang}-${target_lang}.txt >> $outfile 2>> $errfile
echo '' >> $outfile
rm one_tweet-${source_lang}-${target_lang}.txt