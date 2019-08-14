# cgp-convert-counts

[![Quay Badge][quay-status]][quay-repo]

| Master                                        | Develop                                         |
| --------------------------------------------- | ----------------------------------------------- |
| [![Master Badge][travis-master]][travis-base] | [![Develop Badge][travis-develop]][travis-base] |

This project contain tools for converting RNAseq count data.

## Contained tools

* ### gtfools.py

    The script is based on [GTFtools](http://www.genemine.org/gtftools.php) and can be used to calculate gene length from GTF files. If you use this script please cite:
    
    Hong-Dong Li, GTFtools: a Python package for analyzing various modes of gene models, bioRxiv, 263517, doi: https://doi.org/10.1101/263517

    Please refer to `gtfools.py -h` for its usage.

    Below is an example output:

    ```bash
    #ensid	gene	biotype	chr	mean median longest_isoform	merged
    #ENSG00000255274	TMPRSS4-AS1	antisense	11	313	304	382	453
    ```

* ### get_tpm_fpkm.py

    The script calculates FPKM from raw HT-Seq counts

    Please refer to `get_tpm_fpkm.py -h` for its usage.

* ### merge_samples.py

    The script merges single sample results of *get_tpm_fpkm.py* into one file.

    Please refer to `merge_samples.py -h` for its usage.

## LICENSE

Copyright (c) 2019 Genome Research Ltd.

Author: CancerIT <cgpit@sanger.ac.uk>

This file is part of cgp-convert-counts.

cgp-convert-counts is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.


<!-- Travis -->
[travis-base]: https://travis-ci.org/cancerit/cgp-convert-counts
[travis-master]: https://travis-ci.org/cancerit/cgp-convert-counts.svg?branch=master
[travis-develop]: https://travis-ci.org/cancerit/cgp-convert-counts.svg?branch=develop

<!-- Quay.io -->
[quay-status]: https://quay.io/repository/wtsicgp/cgp-convert-counts/status
[quay-repo]: https://quay.io/repository/wtsicgp/cgp-convert-counts
[quay-builds]: https://quay.io/repository/wtsicgp/cgp-convert-counts?tab=builds
