#! /bin/bash

set -xe

mkdir test && cd test
gtftools.py -l test.len ../data/test.gtf && diff test.len ../data/test.len
get_tpm_fpkm.py -c ../data/test.count -g test.len && diff <(grep -v '#' test_count_fpkm_tpm.tsv) <(grep -v '#' ../data/test_count_fpkm_tpm.tsv)
get_tpm_fpkm.py -c ../data/test2.count -g test.len && diff <(grep -v '#' test2_count_fpkm_tpm.tsv) <(grep -v '#' ../data/test2_count_fpkm_tpm.tsv)
merge_samples.py -g test.len -merge_ext _count_fpkm_tpm.tsv
