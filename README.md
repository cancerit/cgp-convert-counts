# cgp-convert-counts

This project contain tools for converting RNAseq count data.

## Contained tools

* ### gtfools.py

    The script can be used to calculate gene length from GTF files. 

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
