#!/projects/team-1/devops/anaconda3/envs/gene_prediction/bin/python3

import argparse
import subprocess
import os
from multiprocessing import Pool 
import zipfile
import shutil

parser=argparse.ArgumentParser(description='example: ./gene_prediction_pipeline.py -i /home/team1/genome_assembly/output/assembly-reconciliation/ -t 5 -o /home/scleland7')
parser.add_argument("-i", required=True, help="full path to input folder with fasta files")
parser.add_argument("-t", default=1, help="Number of threads")
parser.add_argument("-o", required=True, help="full path to output folder")
parser.add_argument("-a", action="store_true", help="run aragorn")
parser.add_argument("-r", action="store_true", help="run rnammer")
parser.add_argument("-p", action="store_true", help="run prodigal")
parser.add_argument("-gm", action="store_true", help="run genemark")
parser.add_argument("-gl", action="store_true", help="run glimmer")
args=parser.parse_args()


print("*******************ARGUMENTS")
print(args)
subprocess.run(["touch", args.i + "/fake_file.txt"])

print("making gene_prediction_output directory")
if not os.path.exists(args.o + "/gene_prediction_output/"):
	os.mkdir(args.o + "/gene_prediction_output/")

print("making gene_prediction_output/gff_output directory")
if not os.path.exists(args.o + "/gene_prediction_output/gff_output"):
	os.mkdir(args.o + "/gene_prediction_output/gff_output")

print("making gene_prediction_output/glimmer_raw_output directory")
if not os.path.exists(args.o + "/gene_prediction_output/glimmer_raw_output"):
        os.mkdir(args.o + "/gene_prediction_output/glimmer_raw_output")

print("making gene_prediction_output/aragorn_raw_output directory")
if not os.path.exists(args.o + "/gene_prediction_output/aragorn_raw_output"):
        os.mkdir(args.o + "/gene_prediction_output/aragorn_raw_output")

#go through every file in input folder and add it to list
input_list=[]

#input_list.append(args.i)
print("***********************unzipping folder")
for file in os.scandir(args.i):
	print("****directory scan for zip. Prints all zip files found")
	if file.path.endswith(".zip"):
		print(file)
		dest= (file.name).replace(".zip", "")
		with zipfile.ZipFile(file, "r") as zip_ref:
			zip_ref.extractall(args.i)
		#for subfile in os.scandir(args.i + dest):
		#	shutil.copy2(subfile, args.i)	
		print("*******location of unzipped file folder")
		print(args.i + dest)
		#subprocess.call(["rm", "-r", args.i + dest])
		#subprocess.call(["rm", "-r", file])

print("********************************adding fasta files to input list")

for file in os.scandir(args.i):
	if file.path.endswith(".fasta"):
		input_list.append(file.path)

def aragorn(fasta_file):
	basename=os.path.basename(fasta_file).strip(".fasta")
	output_name=args.o + "/gene_prediction_output/aragorn_raw_output/"
	subprocess.call(["aragorn", "-w", fasta_file, "-o", output_name + basename + "_aragorn.txt"])
	aragorn_raw_gff_file=args.o + "/gene_prediction_output/aragorn_raw_output/" + basename + "_aragorn_raw.gff"
	subprocess.call(["./cnv_aragorn2gff.pl","-i",  output_name + basename + "_aragorn.txt", "-o", aragorn_raw_gff_file])
	aragorn_gff_file=open(args.o + "/gene_prediction_output/gff_output/" + basename + "_aragorn.gff", "w")
	with open(aragorn_raw_gff_file, "r") as fh:
		for line in fh:
			line_tab=line.strip()
			line_tab=line_tab.split("\t")
			if not line.startswith("#"):
				if int(line_tab[3])>int(line_tab[4]):
					pass
				else:
					aragorn_gff_file.write(line)


def rnammer(fasta_file):
	basename=(os.path.basename(fasta_file)).strip(".fasta")
	output_name=args.o + "/gene_prediction_output/"
	subprocess.call(["rnammer", "-S", "bac", "-m", "lsu,ssu,tsu", "-gff", output_name + "gff_output/" + basename + "_rnammer.gff", fasta_file])

def prodigal(fasta_file):
	print("*************************Running prodigal")
	basename=(os.path.basename(fasta_file)).strip(".fasta")
	print("**********prodigal input")
	print(fasta_file)
	print("*********file basename")
	print(basename)
	print("********prodigal output")
	output_name=args.o + "/gene_prediction_output/"
	print("********Prodigal output name")
	print(output_name)
	subprocess.call(["prodigal", "-i", fasta_file, "-f", "gff", "-o", output_name + "gff_output/" + basename + "_prodigal.gff"])

def genemark(fasta_file):
	print("**************************Running genemark")
	basename=(os.path.basename(fasta_file)).strip(".fasta")
	print("**********genemark input")
	print(fasta_file)
	print("*********file basename")
	print(basename)
	print("********genemark output")
	output_name=args.o + "/gene_prediction_output/"
	print("********Genemark Output name")
	print(output_name)
	#subprocess.Popen("gms2.pl --seq " + fasta_file + " --genome-type auto --format gff --output " + output_name + "gff_output/" + "_genemark.gff", shell=True)
	subprocess.call(["perl", "/projects/team-1/tools/gms2_linux_64/gms2.pl" , "--seq", fasta_file, "--genome-type", "auto", "--format", "gff", "--output", output_name + "gff_output/" + basename + "_genemark.gff"])


def glimmer(fasta_file):
	print("************************Running glimmer")
	basename=os.path.basename(fasta_file).strip(".fasta")
	print("**********glimmer input")
	print(fasta_file)
	print("*********file basename")
	print(basename)
	print("********glimmer output")
	output_name=args.o + "/gene_prediction_output/glimmer_raw_output/" + basename
	print("********Glimmer Output name")
	print(output_name)
	subprocess.call(["/projects/team-1/src/gene_prediction/src/Glimmer.csh", fasta_file, output_name + basename + "_glimmer"])
	predict_file= output_name + basename + "_glimmer.predict"
	print("*****Predict file")
	print(predict_file)
	glimmer_gff_file= open(args.o + "/gene_prediction_output/gff_output/" + basename + "_glimmer.gff", "w")
	print("*****Glimmer Gff file")
	print(glimmer_gff_file)
	subprocess.call(["/projects/team-1/src/gene_prediction/src/Glimmer_GFF_conversion.py", predict_file], stdout=glimmer_gff_file)


pool=Pool(int(args.t))
if args.r==True:
	list(pool.map(rnammer, input_list))
if args.a==True:
	list(pool.map(aragorn, input_list))
if args.p==True:
	print("***************************Input list")
	print(input_list)
	list(pool.map(prodigal, input_list))
if args.gl==True:
	list(pool.map(glimmer, input_list))
if args.gm==True: 
	for i in input_list:
		genemark(i)


