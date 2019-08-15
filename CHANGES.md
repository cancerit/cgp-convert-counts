# CHANGES

## 0.1.1

* cleaned header of `get_tmp_fpkm.py`; It now produce compressed output by default, and has a `--no-compression` option to disable it.

## 0.1.1

* `gtftools.py` now uses tempfile for intermidiate output, and tells GTF formate using the first line after headers in a GTF file.
* `get_tmp_fpkm.py` now has an option to specify output folder
* `merge_samples.py` tells number of lines in header to ignore on the fly
