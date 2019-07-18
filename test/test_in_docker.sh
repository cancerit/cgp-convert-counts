#! /bin/bash

set -xe

gtftools.py -l test.len Data/test.gtf && diff -q test.len Data/test.len

get_tpm_fpkm.py -c Data/test.count -g test.len && diff -q <(grep -v '#' test_count_fpkm_tpm.tsv) <(grep -v '#' Data/test_count_fpkm_tpm.tsv)
get_tpm_fpkm.py -c Data/test2.count -g test.len && diff -q <(grep -v '#' test2_count_fpkm_tpm.tsv) <(grep -v '#' Data/test2_count_fpkm_tpm.tsv)

merge_samples.py -g test.len -merge_ext _count_fpkm_tpm.tsv
diff -q merged_count.tsv Data/merged_count.tsv
diff -q merged_fpkm.tsv Data/merged_fpkm.tsv
diff -q merged_fpkm_uq.tsv Data/merged_fpkm_uq.tsv
diff -q merged_tpm.tsv Data/merged_tpm.tsv
diff -q merged_unfiltered_count.tsv Data/merged_unfiltered_count.tsv
