import os, sys, glob
from configparser import ConfigParser

# adding module search path so that main modules can be imported
LIBR_DIR = os.getcwd()
BASE_DIR = LIBR_DIR.split('library')[0]
DATA_DIR = os.path.join(BASE_DIR, "data")

# to import pre_gcm as a module from this directory
sys.path.insert(0, BASE_DIR)

import pre_gcm

def get_config():
    config = ConfigParser()
    config.read(os.path.join(BASE_DIR, "config.ini"))
    config_aligner = config["ALIGNER"]
    config_general = config["GENERAL"]
    config_pregcm = config["PREGCM"]
    return config_aligner, config_pregcm, config_general

def setup_pregcm(corpus, aligns, pfms):
    config_aligner, config_pregcm, config_general = get_config()
    lang1 = config_general["language_1"] if config_general["language_1"] else "HINDI"
    lang1_code = lang1.lower()[:2]
    lang2 = config_general["language_2"] if config_general["language_2"] else "ENGLISH"
    lang2_code = lang2.lower()[:2]
    lang1_in_file = config_aligner["source_inp_file"] if config_aligner["source_inp_file"] else lang1_code + "-to-" + lang2_code + "-input_lang1"
    lang2_in_file = config_aligner["target_inp_file"] if config_aligner["target_inp_file"] else lang1_code + "-to-" + lang2_code + "-input_lang2"
    pfms_file = config_aligner["pfms_file"] if config_aligner["pfms_file"] else lang1_code + "-to-" + lang2_code + "_pfms.txt"
    align_op_file = config_aligner["align_op_file"] if config_aligner["align_op_file"] else lang1_code + "-to-" + lang2_code + "-input_parallel_alignments"
    pregcm_output_loc = config_pregcm["pregcm_output_loc"] if config_pregcm["pregcm_output_loc"] else lang1_code + "-to-" + lang2_code 

    # write corpus to input files
    with open(os.path.join(DATA_DIR, lang1_in_file), 'w') as f:
        f.write(corpus['lang1'])
    with open(os.path.join(DATA_DIR, lang2_in_file), 'w') as f:
        f.write(corpus['lang2'])

    # write alignments to file
    with open(os.path.join(DATA_DIR, align_op_file), 'w') as f:
        f.write("\n".join(aligns))

    if pfms is not None:
        with open(os.path.join(DATA_DIR, pfms_file), 'w') as f:
            f.write("\n".join(pfms))

    return pregcm_output_loc

def read_pregcm_output(pregcm_output_loc):
    output = []
    file_list = glob.glob(os.path.join(DATA_DIR, pregcm_output_loc, "input*.txt"))
    for fil in file_list:
        tmp = ""
        with open(fil, "r") as f:
            tmp = f.read()
            tmp = tmp.split("\n\n")
        output.extend(tmp)
    return output


def process(corpus, aligns, parsetrees, pfms = None):
    print("setting up pre-gcm...")
    pregcm_output_loc = setup_pregcm(corpus, aligns, pfms)
    print("running pre-gcm...")
    pre_gcm.main(parsetrees)
    print("pre-gcm completed..")
    pregcm_output = read_pregcm_output(pregcm_output_loc)
    return pregcm_output

if __name__ == '__main__':
    pass