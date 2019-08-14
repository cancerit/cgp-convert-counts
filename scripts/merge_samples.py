#!/usr/bin/python3

import os
import sys
import argparse
import pandas as pd

version = "1.0.1"

# converts count data to fpkm and tpm values
# needs some mofifications before running ....
# prepare data 
# print data frame
def _print_df(mydf, outfile, index_label):
    mydf.to_csv(outfile, sep='\t', mode='w', header=True, index=True, index_label=index_label, doublequote=False)

def create_df(infile,skip_footer,skip_header,col_names, index_label):
    df = pd.read_csv(infile, compression='infer', sep="\t", skipfooter=skip_footer, skiprows=skip_header, engine='python', names=col_names,  header=None, index_col=index_label)
    return df


# merge per sample files to a single file

def merge_files(exp_type, **opt):
    out_file = opt.get('outfile',None)
    gene_len_file = opt['gene_len'].strip()
    merge_ext=opt['merge_ext'].strip()
    gene_len_col = opt['gene_length_column'].strip()
    user_loc =  opt.get('input_path','.')
    mydfs=[]
    column_order=[]
    index_label = 'ensid'
    gene_len_df = create_df(gene_len_file,0,1, [index_label,'gene','biotype','chr', 'mean','median', 'longest_isoform', 'merged'], index_label)
    # drop unecessary columns....
    drop_columns = ['mean', 'median', 'longest_isoform', 'merged']
    drop_columns.remove(gene_len_col)
    # drop other columns except considered for gene length ...
    gene_len_df.drop(drop_columns, axis=1, inplace=True)
    mydfs.append(gene_len_df)
    for (dirpath, dirnames, filenames) in os.walk(user_loc,topdown=True):
        # avoid going into subdirectories if any...
        dirnames.clear()
        for myfile in sorted(filenames):
            if myfile.endswith(merge_ext):
                (sample,_)=os.path.splitext(myfile)
                sample=sample.split(".")[0]
                full_path=os.path.join(dirpath, myfile)
                skip_header = 0
                with open(full_path, 'r') as sample_counts:
                    for line in sample_counts:
                        if not line.startswith('##'):
                            break
                        else:
                            skip_header += 1
                tmpdf=create_df_to_merge(full_path,skip_header)
                # select colum from data frame
                tmpdf=tmpdf[[exp_type]]
                tmpdf.columns=[sample]
                column_order.append(sample)
                mydfs.append(tmpdf)
        combined_df = pd.concat(mydfs, axis=1, sort=True, join="inner", verify_integrity=True)
        combined_df.fillna(0,inplace=True)
        _print_df(combined_df, 'merged_' + exp_type + '.tsv', index_label)
    return

def create_df_to_merge(infile,skip_header):
    df = pd.read_csv(infile, compression='infer', skiprows=skip_header, sep="\t", index_col=['#ensid'])
    return df


def main():
    usage = "\n %prog [options] -g gene_len.tsv  -merge_ext _count_fpkm_tpm.tsv"

    optParser = argparse.ArgumentParser(prog='merge_samples.py')
    optional = optParser._action_groups.pop()
    required = optParser.add_argument_group('required arguments')

    required.add_argument("-g", "--gene_len", type=str, dest="gene_len", required=True,
                          default=None, help="gene length file path, format: ensid gene_name length")

    optional.add_argument("-len_col", "--gene_length_column", type=str, dest="gene_length_column", required=False,
                          default="longest_isoform",
                          help="gene length column name to use from gene_len file default:longest_isoform")

    required.add_argument("-merge_ext", "--merge_ext", type=str, dest="merge_ext",
                          default=None, help="unique part of file extension to merge")

    optional.add_argument("-in_path", "--input_path", type=str, dest="input_path",
                          default=".", help="input directory path for files to merge")

    optional.add_argument("-col_name", "--column_names", type=str, nargs='+', dest="column_names",
                          required=False,
                          default=["unfiltered_count","count","tpm","fpkm","fpkm_uq"],
                          help=" column names to merger defaut: count tpm fpkm fpkm_uq")

    optional.add_argument("-v", "--version", action='version', version='%(prog)s ' + version)
    optional.add_argument("-q", "--quiet", action="store_false", dest="verbose", required=False, default=True)

    optParser._action_groups.append(optional)
    if len(sys.argv) == 1:
        optParser.print_help()
        sys.exit(1)
    opts = optParser.parse_args()
    if not (opts.gene_len):
        sys.exit('\nERROR Arguments required\n\tPlease run: merge_samples.py --help\n')
    # vars function returns __dict__ of Namespace instance
    # use this step after analysis to merge files into single tsv file
    opt= vars(opts)
    print(opt)
    for type in opt['column_names']:
       print("Merging val {} for samples into a single file....: ".format(type))
       merge_files(type, **vars(opts))

if __name__ == "__main__":
    main()
