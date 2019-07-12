import os
import sys
import argparse
import pandas as pd

version = "1.0.0"

# converts count data to fpkm and tpm values
# remove anyheaders ...
#HTSEQ count footer is removed (last 5 lines)....
# prepare data
def prepare_data(**opt):
    count_file = opt['count_file']
    gene_len_file = opt['gene_len']
    index_label = 'ensid'
    min_read_count = 1
    # create data frame from htseq count data, ignore last 5 line of summary stats
    count_df = create_df(count_file,5,[index_label,'count'], index_label)
    # create gene length data frame 
    gene_len_df = create_df(gene_len_file, 0, [index_label, 'gene_name', 'length'], index_label)

    combined_df=pd.concat([gene_len_df,count_df], axis=1, sort =True)
    # filter genes with 0 read count
    combined_df.drop(combined_df[combined_df['count'] < min_read_count].index, inplace=True)
    #https: // docs.gdc.cancer.gov/Data/Bioinformatics_Pipelines/Expression_mRNA_Pipeline/  # fpkm
    combined_df['fpkm']= (combined_df['count'] * 1e9) / (combined_df['count'].sum() * combined_df['length'])
    # FPKM_UQ https://docs.gdc.cancer.gov/Data/Bioinformatics_Pipelines/Expression_mRNA_Pipeline/#upper-quartile-fpkm
    uq=combined_df['count'].quantile(q=0.75, interpolation='nearest')

    combined_df['fpkm_uq'] = (combined_df['count'] * 1e9) / (uq * combined_df['length'])
    #TPM = FPKM / (sum of FPKM over all genes/transcripts) * 10^6
    combined_df['tpm'] = combined_df['fpkm']/ combined_df['fpkm'].sum() * 1e6
	# print results
    _print_df(combined_df, index_label, count_file)

    return

# print data frame 
def _print_df(mydf, index_label, count_file ):
    mydf = mydf.round(decimals=8)
    (_, name) = os.path.split(count_file)
    (out_file, _) = os.path.splitext(name)
    mydf.to_csv(out_file + '_count_fpkm_tpm.tsv', sep='\t', mode='w', header=True, index=True, index_label=index_label, doublequote=False)

def create_df(infile,skip_footer,col_names, index_label):
    df = pd.read_csv(infile, compression='infer', sep="\t", skipfooter=skip_footer, engine='python', names=col_names,  header=None, index_col=index_label)
    return df

def main():
    usage = "\n %prog [options] -c count_file.tsv -g gene_len.tsv  -a archive.tar.gz"

    optParser = argparse.ArgumentParser(prog='get_fpkm')
    optional = optParser._action_groups.pop()
    required = optParser.add_argument_group('required arguments')

    required.add_argument("-c", "--count_file", type=str, dest="count_file", required=True,
                          default=None, help="count file path, format: gene count (last five lines of summary were ignored)")

    required.add_argument("-g", "--gene_len", type=str, dest="gene_len", required=True,
                          default=None, help="gene length file path, format: ensid gene_name length")

    optional.add_argument("-v", "--version", action='version', version='%(prog)s ' + version)
    optional.add_argument("-q", "--quiet", action="store_false", dest="verbose", required=False, default=True)

    optParser._action_groups.append(optional)
    if len(sys.argv) == 1:
        optParser.print_help()
        sys.exit(1)
    opts = optParser.parse_args()
    if not(opts.gene_len or opts.count_file):
        sys.exit('\nERROR Arguments required\n\tPlease run: get_fpkm.py --help\n')

    # vars function returns __dict__ of Namespace instance
    else:
        print("Converting count to FPKM....")
        prepare_data(**vars(opts))

if __name__ == "__main__":
    main()
