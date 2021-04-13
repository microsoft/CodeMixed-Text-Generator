#!/bin/bash

inputdir=$1
outdir=$2
lang1=$3
lang2=$4
echo $1
echo $2
echo $3
echo $4

mkdir -p $outdir
# rm -rf $outdir/*

time ./run.sh $inputdir/input-cm-${lang1}-${lang2}.txt $outdir/out-cm-${lang1}-${lang2}.txt ${lang1} ${lang2}