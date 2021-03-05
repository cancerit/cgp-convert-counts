# CHANGES

## 0.1.4

* missed updating Dockerfile version number in 0.1.3

## 0.1.3

* `gtftools.py` fix for genes without a gene_name data point in a GTF file, falls back to the gene_id data point instead

## 0.1.2

* cleaned header of `get_tmp_fpkm.py`; It now produce compressed output by default, and has a `--no-compression` option to disable it.
* consistent version number across scripts

## 0.1.1

* `gtftools.py` now uses tempfile for intermidiate output, and tells GTF formate using the first line after headers in a GTF file.
* `get_tmp_fpkm.py` now has an option to specify output folder
* `merge_samples.py` tells number of lines in header to ignore on the fly
