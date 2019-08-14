#!/usr/bin/python3

import os
import sys
import argparse
import pandas as pd
import numpy as np

version = "1.0.1"

# converts count data to fpkm and tpm values
# remove anyheaders ...
#HTSEQ count footer is removed (last 5 lines)....
# prepare data
def prepare_data(**opt):

    # check output directory exists, create if not, exit if can't create.
    if opt['output_dir']:
        if not os.path.exists(opt['output_dir']):
            try:
                os.mkdir(opt['output_dir'])
            except OSError:
                print ("Failed to create the output directory: %s" % opt['output_dir'])
                sys.exit(1)
    else:
        opt['output_dir'] = os.getcwd()

    count_file = opt['count_file']
    gene_len_file = opt['gene_len']
    index_label = 'ensid'
    min_read_count = opt['minimum_read_count']
    gene_len_col=opt['gene_length_column']
    user_biotypes=opt['transcript_biotype']
    # create data frame from htseq count data, ignore last 5 line of summary stats
    count_df = create_df(count_file,5,0,[index_label,'count'], index_label)
    # create gene length data frame 
    gene_len_df = create_df(gene_len_file,0,1, [index_label,'gene','biotype','chr', 'mean','median', 'longest_isoform', 'merged'], index_label)

    # check if gene length and count data frame have equal rows
    ensid_comparison= np.array_equal(np.sort(count_df.index.values), np.sort(gene_len_df.index.values))
    print("COUNT_ROWS:{} GENELEN_ROWS:{} ENSID_COMPARISON STATUS:{}".format(count_df.shape[0],gene_len_df.shape[0], ensid_comparison) )

    if  not ensid_comparison:
        sys.exit("Error: Ensembl ids in gene length and count file DO NOT match")

    drop_columns=['mean','median', 'longest_isoform', 'merged']
    drop_columns.remove(gene_len_col)
    # drop other columns except considered for gene length ...
    gene_len_df.drop(drop_columns, axis=1, inplace=True)

    combined_df=pd.concat([gene_len_df,count_df], axis=1, sort =True)
    # filter genes with user defined read counts read count, these will be set to 0
    combined_df['unfiltered_count'] = combined_df['count']
    combined_df.loc[combined_df['count'] < min_read_count, 'count'] = 0
    #https: // docs.gdc.cancer.gov/Data/Bioinformatics_Pipelines/Expression_mRNA_Pipeline/  # fpkm
    combined_df['fpkm']= (combined_df['count'] * 1e9) / (combined_df['count'].sum() * combined_df[gene_len_col])
    # FPKM_UQ https://docs.gdc.cancer.gov/Data/Bioinformatics_Pipelines/Expression_mRNA_Pipeline/#upper-quartile-fpkm
    # filter data frame for protein coding genes only...
    fpkm_quantile_df=combined_df[combined_df.biotype.isin(user_biotypes)]
    # calculate upper quantile value...
    uq=fpkm_quantile_df['count'].quantile(q=0.75, interpolation='nearest')
    combined_df['fpkm_uq'] = (combined_df['count'] * 1e9) / (uq * combined_df[gene_len_col])
    #TPM = FPKM / (sum of FPKM over all genes/transcripts) * 10^6
    combined_df['tpm'] = combined_df['fpkm']/ combined_df['fpkm'].sum() * 1e6
	# print results and header lines ....

    print(combined_df.shape)

    header_data={}
    for key in opt:
        if key is not None:
            header_data["##"+key+"="]=str(opt[key])

    header_data['##Upper_Quartile_Val=']=str(uq)
    header_data['##WARNING user filtered read count is set to ='] = 0

    header_df=pd.DataFrame.from_dict(header_data,orient='index')

    _print_df(combined_df, index_label, count_file, header_df, opt['output_dir'])

    return

# print data frame 
def _print_df(mydf, index_label, count_file, header_df, output_dir):
    mydf = mydf.round(decimals=2)
    (_, name) = os.path.split(count_file)
    (out_file, _) = os.path.splitext(name)
    out_file += '_count_fpkm_tpm.tsv'
    out_file = os.path.join(output_dir, out_file)
    if os.path.exists(out_file):
        sys.exit("Error: existing out_file: %s, not to overwite, exits!" % out_file)
    header_df.to_csv(out_file,sep="\t", header=False, mode ='w')
    mydf.to_csv(out_file, sep='\t', mode='a', header=True, index=True, index_label="#"+index_label, doublequote=False)

def create_df(infile,skip_footer,skip_header,col_names, index_label):
    df = pd.read_csv(infile, compression='infer', sep="\t", skipfooter=skip_footer, skiprows=skip_header, engine='python', names=col_names,  header=None, index_col=index_label)
    return df

def main():
    usage = "\n %prog [options] -c count_file.tsv -g gene_len.tsv "

    optParser = argparse.ArgumentParser(prog='get_tpm_fpkm.py')
    optional = optParser._action_groups.pop()
    required = optParser.add_argument_group('required arguments')

    required.add_argument("-c", "--count_file", type=str, dest="count_file", required=True,
                          default=None, help="count file path, format: gene count (last five lines of summary were ignored)")

    required.add_argument("-g", "--gene_len", type=str, dest="gene_len", required=True,
                          default=None, help="gene length file path, format: ensid gene_name length [Warning first line will be skipped as header]")
    
    optional.add_argument("-od", "--output_dir", type=str, dest="output_dir", required=False,
                          default=None, help="output directory path, default to current directory.")

    optional.add_argument("-minrc", "--minimum_read_count", type=int, dest="minimum_read_count", required=False,
                          default=0, help="Minimum read count to consider for fpkm,tpm calculations default:0")

    optional.add_argument("-len_col", "--gene_length_column", type=str, dest="gene_length_column", required=False,
                          default="longest_isoform", help="gene length column name to use from gene_len file default:longest_isoform")

    optional.add_argument("-biotype", "--transcript_biotype", type=str, nargs='+', dest="transcript_biotype", required=False,
                          default=["protein_coding"], help="transcript biotypes to choose for fpkm_uq (upper quartile normalization), default: protein_coding,")

    optional.add_argument("-v", "--version", action='version', version='%(prog)s ' + version)
    optional.add_argument("-q", "--quiet", action="store_false", dest="verbose", required=False, default=True)

    optParser._action_groups.append(optional)
    if len(sys.argv) == 1:
        optParser.print_help()
        sys.exit(1)
    opts = optParser.parse_args()
    if not(opts.gene_len or opts.count_file):
        sys.exit('\nERROR Arguments required\n\tPlease run: get_tpm_fpkm.py --help\n')

    # vars function returns __dict__ of Namespace instance
    else:
        print("Converting count to FPKM, TPM and FPKM_UQ....")
        prepare_data(**vars(opts))

if __name__ == "__main__":
    main()
