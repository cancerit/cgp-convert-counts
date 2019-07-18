# cgp-convert-counts

This project contain tools for converting RNAseq count data.

---
## Contained tools

### Gene length calculation: **gtfools.py**

Please refer to `gtfools.py -h` for its usage.

Below is an example output:

```bash
#ensid	gene	biotype	chr	mean median longest_isoform	merged
#ENSG00000255274	TMPRSS4-AS1	antisense	11	313	304	382	453
```

### FPKM calculation from raw counts: **get_tpm_fpkm.py**

Please refer to `get_tpm_fpkm.py -h` for its usage.

### Merge output of *get_tpm_fpkm.py* into a single file: **merge_samples.py**

Please refer to `merge_samples.py -h` for its usage.

---
## LICENSE

Copyright (c) 2019 Genome Research Ltd.

Author: CancerIT <cgpit@sanger.ac.uk>

This file is part of cgp-convert-counts.

cgp-convert-counts is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.
