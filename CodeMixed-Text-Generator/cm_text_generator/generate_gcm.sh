#!/bin/bash

inputdir=$1
sourcefile=$2
outdir=$3
source_lang=$4
target_lang=$5
value=1
block=999
echo $1
echo $2
echo $3
end=$(wc -l $sourcefile | cut -d " " -f 1)
echo $end

mkdir -p $outdir

until [[ $value -gt $end ]]; do
	if [ ! -f $outdir/out-cm-$source_lang-$target_lang-$value.txt ]
		then
			echo $value
			while [ ! -f $inputdir/flag-cm-$source_lang-$target_lang-$value.txt ]
			do
				echo "$inputdir/flag-cm-$source_lang-$target_lang-$value.txt does not exist"
				sleep 30
			done
			./cm_text_generator/generator/run.sh $inputdir/input-cm-$source_lang-$target_lang-$value.txt $outdir/out-cm-$source_lang-$target_lang-$value.txt ${source_lang} ${target_lang}
	fi
	value=$(($value + $block))
	value=$(($value + 1))
done
