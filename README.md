# cgp-convert-counts

tools for converting RNAseq count data

### how to run genelength calculations... 

python gtfools.py -l gene_length.tsv ensembl.gtf

### output columns (e.g.,): 
#ensid	gene	biotype	chr	mean median longest_isoform	merged
#ENSG00000255274	TMPRSS4-AS1	antisense	11	313	304	382	453
### how to run fpkm calculations...

python get_tpm_fpkm.py -c htseq_count.txt -g gene_length.tsv

### refere ```get_tpm_fpkm.py -h``` for more options

### additional script addd for user to merge samples into a single file...

python merge_samples.py -g gene_length.tsv -merge_ext _count_fpkm_tpm.tsv
