# cgp-convert-counts

This project contain tools for converting RNAseq count data.

## Contained tools

* ### gtfools.py

    The script is based on [GTFtools](http://www.genemine.org/gtftools.php) and can be used to calculate gene length from GTF files. If you use this script please cite:
    
    Hong-Dong Li, GTFtools: a Python package for analyzing various modes of gene models, bioRxiv, 263517, doi: https://doi.org/10.1101/263517

    Please refer to `gtfools.py -h` for its usage.

* ### get_tpm_fpkm.py

    The script calculates FPKM from raw HT-Seq counts

    Please refer to `get_tpm_fpkm.py -h` for its usage.

    Below is an example output:

    ```bash
    $ gunzip -c PR13323c.count_count_fpkm_tpm.tsv.gz | head
    ##count_file=/home/yaobo/Downloads/PR13323c.count.gz
    ##gene_len=/home/yaobo/Downloads/ensembl.gene_length.tsv
    ##minimum_read_count=0
    ##gene_length_column=longest_isoform
    ##transcript_biotype=['protein_coding']
    ##Upper_Quartile_Val=3412
    #ensid  gene    biotype chr     longest_isoform count   unfiltered_count        fpkm    fpkm_uq tpm
    ENSG00000000003 TSPAN6  protein_coding  X       3796    6748    6748    18.24   521002.55       43.18
    ENSG00000000005 TNMD    protein_coding  X       1339    0       0       0.0     0.0     0.0
    ENSG00000000419 DPM1    protein_coding  20      1161    4022    4022    35.54   1015315.05      84.16
    ```

* ### merge_samples.py

    The script merges single sample results of *get_tpm_fpkm.py* into one file.

    Please refer to `merge_samples.py -h` for its usage.

        Below is an example output:

    ```bash
    $ head -n 5 merged_*
    ==> merged_count.tsv <==
    ensid   gene    biotype chr     longest_isoform test2_count_fpkm_tpm    test_count_fpkm_tpm
    ENSG00000177757 FAM87B  lincRNA 1       1944    2       6
    ENSG00000185097 OR4F16  protein_coding  1       995     0       0
    ENSG00000186092 OR4F5   protein_coding  1       918     0       0
    ENSG00000187583 PLEKHN1 protein_coding  1       2455    96      213

    ==> merged_fpkm.tsv <==
    ensid   gene    biotype chr     longest_isoform test2_count_fpkm_tpm    test_count_fpkm_tpm
    ENSG00000177757 FAM87B  lincRNA 1       1944    44.21   82.3
    ENSG00000185097 OR4F16  protein_coding  1       995     0.0     0.0
    ENSG00000186092 OR4F5   protein_coding  1       918     0.0     0.0
    ENSG00000187583 PLEKHN1 protein_coding  1       2455    1680.37 2313.4

    ==> merged_fpkm_uq.tsv <==
    ensid   gene    biotype chr     longest_isoform test2_count_fpkm_tpm    test_count_fpkm_tpm
    ENSG00000177757 FAM87B  lincRNA 1       1944    10716.74        14490.23
    ENSG00000185097 OR4F16  protein_coding  1       995     0.0     0.0
    ENSG00000186092 OR4F5   protein_coding  1       918     0.0     0.0
    ENSG00000187583 PLEKHN1 protein_coding  1       2455    407331.98       407331.98

    ==> merged_tpm.tsv <==
    ensid   gene    biotype chr     longest_isoform test2_count_fpkm_tpm    test_count_fpkm_tpm
    ENSG00000177757 FAM87B  lincRNA 1       1944    38.82   63.87
    ENSG00000185097 OR4F16  protein_coding  1       995     0.0     0.0
    ENSG00000186092 OR4F5   protein_coding  1       918     0.0     0.0
    ENSG00000187583 PLEKHN1 protein_coding  1       2455    1475.67 1795.54

    ==> merged_unfiltered_count.tsv <==
    ensid   gene    biotype chr     longest_isoform test2_count_fpkm_tpm    test_count_fpkm_tpm
    ENSG00000177757 FAM87B  lincRNA 1       1944    2       6
    ENSG00000185097 OR4F16  protein_coding  1       995     0       0
    ENSG00000186092 OR4F5   protein_coding  1       918     0       0
    ENSG00000187583 PLEKHN1 protein_coding  1       2455    96      213
    ```

## LICENSE

Copyright (c) 2019 Genome Research Ltd.

Author: CancerIT <cgpit@sanger.ac.uk>

This file is part of cgp-convert-counts.

cgp-convert-counts is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.
