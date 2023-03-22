#!/bin/bash
# *very* basic script to output *only* the number of words in an essay
# for counting purposes
# depends upon the 'texcount' perl script
echo $(printf "%'d" $(texcount -brief -merge -sum=1,0,1,0,1,1,1 2>/dev/null "$1" | cut -d ':' -f1 | awk '{print $1}' ) | sed 's/,/, /g') > words.txt
