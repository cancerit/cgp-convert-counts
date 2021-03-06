#!/usr/bin/python3

# import modules
import argparse
import sys
import tempfile

version = "0.1.5"

###############
# sb43 modified to suit casm need and output additional columns : boiotype, gnene name and chromosome
# Hong-Dong Li, GTFtools: a Python package for analyzing various modes of gene models, bioRxiv, 263517, doi: https://doi.org/10.1101/263517
# removed chromosome name option to accomodate all species by default instead of canoncal human 1-22 and XY
# converted to python 3 compatible syntax
# tested as below:
# python gtftools.py -l test_75.bed  ensembl_75.gtf
# compared with R GenomicFeatures, results are identical
##############


####################################################################
### notes: in this library, bed files for operations like merge  ###
### and substracting contains require at least four columns:     ###
### chr,start,end,strand.                                        ###
####################################################################

################################
######## function list  ########
################################
#1.	neighbor_merge: merge two ranges, say two exons
#2.	bedmerge: merge a list of ranges, say a few exons
#3.	exon2intron: calculate intron bed from a list of exons.
#4.	masked_intron: identify introns which are covered by exons of other isoforms
#5.	get_UTR: get 5' and 3' UTR of isoforms.
#6.	get_gene_bed: generate bed files for a list of input genes given in a txt file
#7.	merge_exon: merge all exons of multiple isoforms from the same gene.
#8. 	get_intron: calculate intron bed for each isoform
#
#
#
#################################
############ functions:  ########
#################################


def neighbor_merge(range1,range2):
	if range2[1]<=range1[2]:
		merged =[(range1[0],range1[1],max(range1[2],range2[2]),range1[3])]
	else:
		merged=[range1,range2]
	return merged


def bedmerge(featureRange):
	# featureRange: a list of ranges in bed format, such as [(1,1000,2000,+),(1,2200,3000,-)]
	featureRange.sort(key = lambda x: (x[0],x[1]))
	merged=[]
	nRange=len(featureRange)
	if nRange == 1:
		merged=featureRange
	elif nRange == 2:
		imerge=neighbor_merge(featureRange[0],featureRange[1])
		for each in imerge:
			merged.append(each)
	else:
		i = 2
		imerge=neighbor_merge(featureRange[0],featureRange[1])
		n_imerge=len(imerge)
		while n_imerge > 0:
			if n_imerge == 2:
				merged.append(imerge[0])

			imerge=neighbor_merge(imerge[n_imerge-1],featureRange[i])
			n_imerge=len(imerge)
			if i == nRange-1:
				for each in imerge:
					merged.append(each)
				n_imerge = -1
			i+=1

	return merged


def exon2intron(featureRange):
	featureRange.sort(key = lambda x: (x[0],x[1]))
	nRange=len(featureRange)
	intron=[]
	if nRange > 1:
		for i in range(1,nRange):
			exon0=featureRange[i-1]
			exon1=featureRange[i]
			thisintron=(exon0[0],exon0[2],exon1[1],exon1[3])
			intron.append(thisintron)
	return intron


def masked_intron(GTFfile_obj,maskedfile="masked_intron.bed"):
	merged = merge_exon(GTFfile_obj)
	introns= get_intron(GTFfile_obj)

	exon = merged['merged_exon']
	intron   = introns['intron']
	iso2gene = introns['iso2gene']
	fnew = open(maskedfile,'w')

	for isoform in intron:
		the_introns = intron[isoform]
		the_gene = iso2gene[isoform]
		the_exons = exon[the_gene]
		for i in range(len(the_introns)):
			for j in range(len(the_exons)):
				if the_introns[i][1] >= the_exons[j][1]  and the_introns[i][2] <= the_exons[j][2]:
					output = "\t".join(map(str,the_introns[i]))+'\t'+isoform+'\t'+the_gene+'\n'
					fnew.write(output)
	fnew.close()


def get_UTR(GTFfile_obj, utr_file=""):
	# record UTR, CDS and strand information for determining iUTR5 or iUTR3
	utr = {}
	cds = {}
	strand = {}
	for line in GTFfile_obj:
		table = line.split('\t')
		if line[0] != '#':
			if table[2] == 'UTR' and 'transcript_id' in line:
				tcx  = line.split('transcript_id')[1].split('"')[1]
				gene = line.split('gene_id')[1].split('"')[1]
				infor=[table[0],int(table[3]),int(table[4]),table[6],gene]
				if tcx in utr:
					utr[tcx].append(infor)
				else:
					utr[tcx]=[infor]
				strand[tcx] = table[6]
			if table[2] == 'CDS' and 'transcript_id' in line:
				tcx  = line.split('transcript_id')[1].split('"')[1]
				gene = line.split('gene_id')[1].split('"')[1]
				cds[tcx] = int((int(table[3])+int(table[4]))/2)
				strand[tcx] = table[6]
	# return pointer to beginning
	GTFfile_obj.seek(0)

	# determine 5UTR and 3UTR
	allUTR=[]
	for tcx in cds:
		if tcx in utr:
			istrand = strand[tcx]
			icds = cds[tcx]
			iutr = utr[tcx]
			iUTR5 = []
			iUTR3 = []
			for thisUTR in iutr:
				if istrand == '+':
					if thisUTR[1] > icds:
						iUTR3.append(thisUTR[1])
						iUTR3.append(thisUTR[2])
					else:
						iUTR5.append(thisUTR[1])
						iUTR5.append(thisUTR[2])
				elif istrand == '-':
					if thisUTR[1] > icds:
						iUTR5.append(thisUTR[1])
						iUTR5.append(thisUTR[2])
					else:
						iUTR3.append(thisUTR[1])
						iUTR3.append(thisUTR[2])
			iUTR5.sort()
			iUTR3.sort()
			iiutr=iutr[0]
			if len(iUTR5) > 1:
				allUTR.append([iiutr[0],iUTR5[0]-1,iUTR5[-1],iiutr[3],iiutr[4],'5UTR',tcx])
			if len(iUTR3) > 1:
				allUTR.append([iiutr[0],iUTR3[0]-1,iUTR3[-1],iiutr[3],iiutr[4],'3UTR',tcx])

	allUTR.sort(key = lambda x: (x[0],x[1]))

	# print UTR to file if required
	if len(utr_file) > 1:
		f=open(utr_file,'w')
		for iUTR in allUTR:
			table = iUTR
			iUTR[1] = str(iUTR[1])
			iUTR[2] = str(iUTR[2])
			out = "\t".join(iUTR)+'\n'
			f.write(out)
		f.close()

	return(allUTR)


def get_tss_region(GTFfile_obj,w=2000,tss_bed_file=''):
	# assume genelistfile contains one gene per line.
	# get bed format
	TSSbed=[]
	for line in GTFfile_obj:
		table = line.split('\t')
		if table[2] == 'transcript':
			chrom  = table[0]
			strand = table[6]
			tcx = line.split('transcript_id')[1].split('"')[1]
			geneid = line.split('gene_id')[1].split('"')[1]
			genesymbol = line.split('gene_name')[1].split('"')[1]
			if strand == "+":
				if int(table[3])-1-w >0:
					iregion = [chrom,int(table[3])-1-w,int(table[3])-1+w,strand,tcx,geneid,genesymbol]
			elif strand == '-':
				if int(table[4])-w > 0:
					iregion = [chrom,int(table[4])-w,int(table[4])+w,strand,tcx,geneid,genesymbol]
			TSSbed.append(iregion)
	# return pointer to beginning
	GTFfile_obj.seek(0)

	# write to file
	if len(tss_bed_file) > 1:
		f=open(tss_bed_file,'w')
		for item in TSSbed:
			out = '\t'.join([item[0],str(item[1]),str(item[2]),item[3],item[4],item[5],item[6]])+'\n'
			f.write(out)
		f.close()


def get_gene_bed(GTFfile_obj,gene_bed_file=''):
	# assume genelistfile contains one gene per line.
	# get bed format
	genebed={}
	for line in GTFfile_obj:
		table = line.split('\t')
		if table[2] == "gene":
			ensid  = line.split('gene_id')[1].split('"')[1]
			symbol = line.split('gene_name')[1].split('"')[1].upper()
			record = (table[0],int(table[3])-1,int(table[4]),table[6],ensid,symbol)
			if table[0] in genebed:
				genebed[table[0]].append(record)
			else:
				genebed[table[0]] = [record]
	# return pointer to beginning
	GTFfile_obj.seek(0)

	# print to file if required
	if len(gene_bed_file) > 1:
		f=open(gene_bed_file,'w')
		for ichrom in list(genebed.keys()):
			ichrom_gene = genebed[ichrom]
			for igene in ichrom_gene:
				f.write('\t'.join([igene[0],str(igene[1]),str(igene[2]),igene[3],igene[4],igene[5],])+'\n')
		f.close()

	return(genebed)


def get_isoform_bed(GTFfile_obj,isoform_bed_file=''):
	# assume genelistfile contains one gene per line.

	# get bed format
	isoformbed={}
	for line in GTFfile_obj:
		table = line.split('\t')
		if table[2] == "transcript":
			isoformid  = line.split('transcript_id')[1].split('"')[1]
			ensid  = line.split('gene_id')[1].split('"')[1]
			symbol = line.split('gene_name')[1].split('"')[1].upper()
			record = (table[0],int(table[3])-1,int(table[4]),table[6],isoformid,ensid,symbol)
			if table[0] in isoformbed:
				isoformbed[table[0]].append(record)
			else:
				isoformbed[table[0]] = [record]
	# return pointer to beginning
	GTFfile_obj.seek(0)

	# print to file if required
	if len(isoform_bed_file) > 1:
		f=open(isoform_bed_file,'w')
		for ichrom in list(isoformbed.keys()):
			ichrom_isoform = isoformbed[ichrom]
			for iisoform in ichrom_isoform:
				f.write('\t'.join([iisoform[0],str(iisoform[1]),str(iisoform[2]),iisoform[3],iisoform[4],iisoform[5],iisoform[6]])+'\n')
		f.close()
	return(isoformbed)


def merge_exon(GTFfile_obj,merged_exon_file=''):
	# record exon coordination
	exon={}
	gene_meta={}
	for line in GTFfile_obj:
		table=line.split('\t')
		if line[0] != '#': #and table[0] in chroms:  # skip comment line
			if table[2] == 'exon':
				gene=line.split('gene_id')[1].split('"')[1]
				iexon=(table[0],int(table[3])-1,int(table[4]),table[6])  # gtf to bed coordination
				if gene in exon:
					exon[gene].append(iexon)
				else:
					exon[gene]=[iexon]
					#sb43 done only once for each gene....
					if line.find('gene_biotype') >= 0:
						biotype = line.split('gene_biotype')[1].split('"')[1]
					else:
						biotype = 'unknown'

					if line.find('gene_name') >= 0:
						gene_name = line.split('gene_name')[1].split('"')[1]
						gene_meta[gene] = [gene_name, biotype, table[0] ]
					else:
						gene_meta[gene] = [gene, biotype, table[0] ]
	# return pointer to beginning
	GTFfile_obj.seek(0)
	# merge all exons of each gene
	merged_exon={}
	gene_length={}
	for gene in exon:
		merged=bedmerge(exon[gene])
		merged_exon[gene]=merged

		# calculate merged gene length(sum of non-overlapping exons)
		length=0
		for each in merged:
			length+=each[2]-each[1]
		gene_length[gene]=length

	# assign merged exons and gene lengths
	merged = {}
	merged['merged_exon']=merged_exon
	merged['merged_gene_length']=gene_length
	merged['metadata']=gene_meta

	# print merged exons if required
	if len(merged_exon_file) > 1:
		m=open(merged_exon_file,'w')
		for gene in merged_exon:
			imerged=merged_exon[gene]
			for each in imerged:
				joined="\t".join([each[0],str(each[1]),str(each[2]),gene,'0',each[3]])+"\n"
				m.write(joined)
		m.close()

	return merged


def get_independent_intron(GTFfile_obj,independent_intron_file='iintron.tmp'):
	# record exon coordination
	exon={}
	for line in GTFfile_obj:
		table=line.split('\t')
		if line[0] != '#':  # skip comment line
			ichr = table[0]
			if table[2] == 'exon':
				iexon=(ichr,int(table[3])-1,int(table[4]),table[6])  # gtf to bed coordination
				if ichr in exon:
					exon[ichr].append(iexon)
				else:
					exon[ichr]=[iexon]
	# return pointer to beginning
	GTFfile_obj.seek(0)

	# get gene coordinates in bed formats
	genebed=get_gene_bed(GTFfile_obj)

	# calculate and write independent introns
	f = open(independent_intron_file,'w')
	record=[]
	for ichrom in list(genebed.keys()):
		ichrom_gene = genebed[ichrom]
		ichrom_exon = exon[ichrom]
		sub = bed_subtract(ichrom_gene,ichrom_exon)
		for item in sub:
			if item[2] - item[1] >= 10:
				uniqued = unique_judge(item,ichrom_gene)
				if len(uniqued)>0:
					record.append(uniqued)
	# write to file
	f = open(independent_intron_file,'w')
	record = list(set(record))
	record.sort(key = lambda x: (x[0],x[1]))
	for item in record:
		ilength = item[2]-item[1]
		f.write('\t'.join([item[0],str(item[1]),str(item[2]),item[4],str(ilength)])+'\n')
	f.close()


def unique_judge(intron,genes):
	# intron: a single intron
	# genes: a list of genes
	hostgene=[]
	ngene=len(genes)
	i = 0
	count = 0
	flag = 0
	while i < ngene and flag == 0:
		igene = genes[i]
		if intron[1] > igene[1] and intron[1] < igene[2]:
			count = count + 1
			hostgene = igene
			if count > 1:
				flag = 1
		i = i+1

	if  count == 1:
		#return((intron[0],intron[1],intron[2],intron[3]))
		return((intron[0],intron[1],intron[2],intron[3],hostgene[4]))
	else:
		return([])


def bed_subtract(bedA,bedB):
	# assume that A and B are on the same chromosome.
	# calculate bedA-bedB
	bedA=bedmerge(bedA)
	bedB=bedmerge(bedB)
	AminusB=[]
	for ibed in bedA:
		ichr    = ibed[0]
		istart  = ibed[1]
		iend    = ibed[2]
		istrand = ibed[3]

		# find overlapping regions in bedB
		overlapped=[]
		for ibedB in bedB:
			ibedB = list(ibedB)
			judgeleft  = (ibedB[1] > istart and ibedB[1] < iend)
			judgeright = (ibedB[2] > istart and ibedB[2] < iend)
			if judgeleft == 1 or judgeright == 1:
				if ibedB[1] <= istart:
					ibedB[1] = istart
				if ibedB[2] >= iend:
					ibedB[2] = iend
				overlapped.append(ibedB)

		# calculate independent introns
		nexons = len(overlapped)
		if nexons == 0:
			AminusB.append((ichr,istart,iend,istrand))
		else:
			for i in range(nexons):
				iexon = overlapped[i]
				if i == 0:
					if iexon[1] > istart:
						AminusB.append((ichr,istart,iexon[1],istrand))
				if i >= 1:
					pexon = overlapped[i-1]
					AminusB.append((ichr,pexon[2],iexon[1],istrand))
				if i == nexons-1:
					if iexon[2] < iend:
						AminusB.append((ichr,iexon[2],iend,istrand))

	# return
	return(AminusB)


def subtract(fileA, fileB):
	A=[]
	f = open(fileA)
	for line in f:
		t = line.strip().split('\t')
		A.append((t[0],int(t[1]),int(t[2]),t[3]))
	f.close()

	B=[]
	f = open(fileB)
	for line in f:
		t = line.strip().split('\t')
		B.append((t[0],int(t[1]),int(t[2]),t[3]))
	f.close()

	A=bedmerge(A)
	for item in A:
		print(('\t'.join([item[0],str(item[1]),str(item[2]),item[3]])))

	B=bedmerge(B)

	R=bed_subtract(A,B)
	length = len(R)
	print(('length:'+str(length)))
	for item in R:
		print(('\t'.join([item[0],str(item[1]),str(item[2]),item[3]])))


def get_isoform_length(GTFfile_obj,isoformlength_file=''):
	'''
	calculate length of isoforms
	'''
	isolength = {}
	gene2iso= {}
	iso2gene= {}
	for line in GTFfile_obj:
		table=line.split('\t')
		if line[0] != '#':  # skip comment line
			if table[2] == 'exon':
				gene= line.split('gene_id')[1].split('"')[1]  # gene ID
				tcx = line.split('transcript_id')[1].split('"')[1]  # tcx ID
				exon_length = int(table[4])-int(table[3])+1

				# isoform length calculate
				if tcx in isolength:
					isolength[tcx] = isolength[tcx] + exon_length
				else:
					isolength[tcx] =  exon_length

				# record isoforms of genes
				if gene in gene2iso:
					gene2iso[gene].append(tcx)
				else:
					gene2iso[gene] = [tcx]
				iso2gene[tcx] = gene
	# return pointer to beginning
	GTFfile_obj.seek(0)

	if len(isoformlength_file) > 1:
		f=open(isoformlength_file,'w')
		f.write('isoform\tgene\tlength\n')
		for thisiso in iso2gene:
			out=thisiso+'\t'+iso2gene[thisiso]+'\t'+str(isolength[thisiso])+'\n'
			f.write(out)
		f.close()

	# return
	ret={}
	ret['gene2iso']  = gene2iso
	ret['isoform_length'] = isolength
	return(ret)


def get_gene_length(GTFfile_obj,genelength_file=''):
	'''
	record exon coordinates
	calculate length of merged exons
	'''
	print('Calculating gene length from GTF...', end='', flush=True)
	merged_data = merge_exon(GTFfile_obj)
	merged_gene_length = merged_data['merged_gene_length']
	metadata = merged_data['metadata']

	# calculate length of each transcrpt isoform
	ret_isoform_length = get_isoform_length(GTFfile_obj)
	gene2iso =ret_isoform_length['gene2iso']
	isolength=ret_isoform_length['isoform_length']

	# calculate gene length as mean, median or max of isoforms
	gene_length = {}
	for igene in gene2iso:
		isoforms = gene2iso[igene]
		length_set = []
		for iisoform in isoforms:
			length_set.append(isolength[iisoform])
		gene_length[igene] = [int(list_mean(length_set)),int(list_median(length_set)),max(length_set),merged_gene_length[igene]]
	print('Done')

	if len(genelength_file) > 1:
		print('Writing gene length to file...', end='', flush=True)
		f = open(genelength_file,'w')
		f.write('ensid\tgene\tbiotype\tchr\tmean\tmedian\tlongest_isoform\tmerged\n')
		for igene in gene_length:
			tmp =  gene_length[igene]
			metalist=metadata[igene]
			tmplst = [igene,metalist[0], metalist[1], metalist[2], str(tmp[0]),str(tmp[1]),str(tmp[2]),str(tmp[3])]
			f.write('\t'.join(tmplst)+'\n')
		f.close()
		print('Done')


def get_exon(GTFfile_obj,exon_file=''):
	'''
	record exon coordinates
	'''
	exon = {}
	iso2gene= {}
	for line in GTFfile_obj:
		table=line.split('\t')
		if line[0] != '#':  # skip comment line
			if table[2] == 'exon':
				gene= line.split('gene_id')[1].split('"')[1]  # gene ID
				tcx = line.split('transcript_id')[1].split('"')[1]  # tcx ID
				iso2gene[tcx] = gene   # map isoforms to genes
				iexon=(table[0],int(table[3])-1,int(table[4]),table[6])  # gtf to bed coordination
				if tcx in exon:
					exon[tcx].append(iexon)
				else:
					exon[tcx]=[iexon]
	# return pointer to beginning
	GTFfile_obj.seek(0)
	ret={}
	ret['exon']=exon
	ret['iso2gene']=iso2gene

	if len(exon_file) > 1:
		f=open(exon_file,'w')
		alltcx = list(exon.keys())
		for itcx in alltcx:
			exonlist = exon[itcx]
			for item in exonlist:
				out = list(map(str,item))+[itcx, iso2gene[itcx]]
				out = '\t'.join(out)+'\n'
				f.write(out)
		f.close()
	#return
	return(ret)


def get_intron(GTFfile_obj,intron_file=''):
	'''
	record intron coordinates
	'''
	exon = {}
	iso2gene= {}
	for line in GTFfile_obj:
		table=line.split('\t')
		if line[0] != '#':  # skip comment line
			if table[2] == 'exon':
				gene= line.split('gene_id')[1].split('"')[1]  # gene ID
				tcx = line.split('transcript_id')[1].split('"')[1]  # tcx ID
				iso2gene[tcx] = gene   # map isoforms to genes
				iexon=(table[0],int(table[3])-1,int(table[4]),table[6])  # gtf to bed coordination
				if tcx in exon:
					exon[tcx].append(iexon)
				else:
					exon[tcx]=[iexon]
	# return pointer to beginning
	GTFfile_obj.seek(0)

	# calculate intron location based on exons for each tcx
	intron={}
	for tcx in exon:
		iexon = exon[tcx]
		iintron=exon2intron(iexon)
		if len(iintron) > 0:
			intron[tcx]=iintron
	to_return={}
	to_return['intron']=intron
	to_return['iso2gene']=iso2gene

	# print intron to file if required
	if len(intron_file) > 0:
		f=open(intron_file,'w')
		for tcx in intron:
			iintron=intron[tcx]
			for each in iintron:
				joined="\t".join([each[0],str(each[1]),str(each[2]),tcx,iso2gene[tcx],each[3]])+"\n"
				f.write(joined)
		f.close()

	# return
	return to_return


def gencode2ensembl(gtf1,gtf2):
	'''
	convert GENCODE to ENSEMBL format
	gtf1: ensembl GTF file object
	gtf2: gencode GTF file object
	'''

	print('Converting GTF to ENSEMBL format...', end = '', flush=True)
	for line in gtf1:
		if line[0:3] == 'chr':
			t = line.strip().split('\t')
			# update
			cname = t[0].split('chr')[1]
			if cname == 'M':
				cname = 'MT'

			# replace
			t[0] =  cname
			out = '\t'.join(t)+'\n'
			gtf2.write(out)
		else:
			gtf2.write(line)
	print('Done')
	# return pointer to the start
	gtf1.seek(0)
	gtf2.seek(0)


def gtf_format_check(gtf):
	'''
	check format of GTF: ensembl or gencode
	'''
	for line in gtf:
		if not line.startswith('#'):
			chrom=line.split('\t')[0]
			if len(chrom) >= 4:
				ftype = 'GENCODE'
			else:
				ftype = 'ENSEMBL'
			break
	gtf.seek(0)
	return(ftype)

############################################
##############   END OF FUNCTIONS  #########
############################################



############################################
##############   START: SIMPLE MATH ########
############################################
def list_sum(x):
	# assume x is lists of numbers
	s = 0
	for i in x:
		s = s + i
	return(s)

def list_mean(x):
	m = list_sum(x)/float(len(x))
	return m

def list_median(x):
	x.sort()
	length = len(x)
	if length % 2 == 0:
		# added floor division required for python 3
		half = length//2
		return((x[half-1]+x[half])//2)
	else:
		return(x[(length-1)//2])

############################################
##############   END: SIMPLE MATH  #########
############################################



############################################
#############  ENTRY  ######################
############################################


# argument parser
parser = argparse.ArgumentParser()  # create a parser
parser.add_argument('GTFfile',help="GTF file: only ENSEMBL or GENCODE GTF file accepted")
parser.add_argument('-m','--merged_exon',metavar='merged_exon',help="file name for outputing merged exons from all isoforms of a gene in bed format")
parser.add_argument('-e','--exon',metavar='exon',help="file name for outputing exon coordination of splice isoforms in bed format")
parser.add_argument('-i','--intron',metavar='intron',help="file name for outputing intron coordination of splice isoforms in bed format")
parser.add_argument('-d','--independent_intron',metavar='independent_intron',help="file name for outputing independent intron coordination of genes. Independent introns refer to those introns that do not overlap with any exon of isoforms. It is calcualted by merging all exons of a chromosome followed by substracting them from gene regions.")
parser.add_argument('-l','--gene_length',metavar='gene_length',help="file name for gene length file. Gene length is calculated as the mean, median and max of isoforms. The length by merging exons of all isoforms is also calculated.")
parser.add_argument('-r','--isoform_length',metavar='isoform_length',help="file name for isoform length file. Isoform length is calculated as the summed length of its exons.mean, median and max of isoforms.")
parser.add_argument('-k','--masked_intron',metavar='masked_intron',help="file name for intron completely overlapping exons")
parser.add_argument('-u','--UTR',metavar='UTR',help="file name for UTR data")
parser.add_argument('-s','--isoform',metavar='isoform',help="file name for isoform bed data.")
parser.add_argument('-g','--gene',metavar='gene',help="file name for gene bed data.")
parser.add_argument('-t','--TSS',metavar='TSS',help="file name for a region centering at transcription start site (TSS). It is calculated as (TSS-w,TSS+w) where w is a user-specified distance, say 2000bp.")
parser.add_argument('-w','--window',metavar='window_size',help="the value of w in calculating TSS regions as described in '-t'. Default: 2000")
parser.add_argument('-v','--version',action='version',version="GTFtools version: %s" % version)
args = parser.parse_args()   # parse command-line arguments


######################################
#################  main   ############
######################################
with open(args.GTFfile, 'r') as GTFfile, tempfile.TemporaryFile(mode='w+t') as GTFfile_ensembl:
	ftype = gtf_format_check(GTFfile)
	print('Input GTF format is '+ftype)
	in_file_obj = GTFfile
	if ftype == 'GENCODE':
		gencode2ensembl(GTFfile, GTFfile_ensembl)
		in_file_obj = GTFfile_ensembl

	# print merged exon in bed format
	if args.merged_exon:
		merge_exon(in_file_obj,merged_exon_file=args.merged_exon)

	# print gene length of merged exons
	if args.gene_length:
		get_gene_length(in_file_obj,genelength_file=args.gene_length)

	# print isoform length of summed exons
	if args.isoform_length:
		get_isoform_length(in_file_obj,isoformlength_file=args.isoform_length)

	# print introns of splice isoforms in bed formatgit
	if args.exon:
		get_exon(in_file_obj,exon_file=args.exon)

	# print introns of splice isoforms in bed format
	if args.intron:
		get_intron(in_file_obj,intron_file=args.intron)

	# print introns of splice isoforms in bed format
	if args.independent_intron:
		get_independent_intron(in_file_obj,independent_intron_file=args.independent_intron)

	if args.masked_intron:
		masked_intron(in_file_obj,maskedfile=args.masked_intron)

	# print UTR in bed format
	if args.UTR:
		get_UTR(in_file_obj,utr_file=args.UTR)

	# print gene bed
	if args.gene:
		get_gene_bed(in_file_obj,gene_bed_file=args.gene)

	# print isoform bed
	if args.isoform:
		get_isoform_bed(in_file_obj,isoform_bed_file=args.isoform)

	# print TSS neighborhood bed
	if args.window:
		w = int(args.window)
	else:
		w = 2000
	if args.TSS:
		get_tss_region(in_file_obj,w=w,tss_bed_file=args.TSS)
