#!/bin/sh
start=`date +%s`
python core.py /Users/js/dev/prh-document-parser/temp/
end=`date +%s`

runtime=$((end-start))
echo "That took $runtime sec"
