import os, subprocess
from configparser import ConfigParser

BASE_DIR = os.getcwd().split('library')[0]

def get_config():
    config = ConfigParser()
    config.read(os.path.join(BASE_DIR, "config.ini"))
    config_aligner = config["ALIGNER"]
    config_general = config["GENERAL"]
    return config_general, config_aligner

def write_to_file(lang1_sents, lang1_in_file, lang2_sents, lang2_in_file):
    # write lang1 file
    with open(os.path.join(BASE_DIR, "data", lang1_in_file), "w") as f:
        f.write(lang1_sents)
    # write lang2 file
    with open(os.path.join(BASE_DIR, "data", lang2_in_file), "w") as f:
        f.write(lang2_sents)

def gen_aligns(corpus):
    # setup file paths using config file
    config_general, config_aligner = get_config()
    # get file names
    lang1 = config_general["language_1"] if config_general["language_1"] else "HINDI"
    lang1_code = lang1.lower()[:2]
    lang2 = config_general["language_2"] if config_general["language_2"] else "ENGLISH"
    lang2_code = lang2.lower()[:2]
    lang1_in_file = config_aligner["source_inp_file"] if config_aligner["source_inp_file"] else lang1_code + "-to-" + lang2_code + "-input_lang1"
    lang2_in_file = config_aligner["target_inp_file"] if config_aligner["target_inp_file"] else lang1_code + "-to-" + lang2_code + "-input_lang2"
    align_op_file = config_aligner["align_op_file"] if config_aligner["align_op_file"] else lang1_code + "-to-" + lang2_code + "-input_parallel_alignments"

    # write the input sentences to the file
    write_to_file(corpus['lang1'], lang1_in_file, corpus['lang2'], lang2_in_file)

    # call aligner
    print('loading fast_align..')
    os.chdir(BASE_DIR)
    p_aligner = subprocess.run(['python', os.path.join(BASE_DIR, 'aligner.py')], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print((p_aligner.stdout).decode())
    print('word level alignments generated...')
    
    # read alignments file
    with open(os.path.join(BASE_DIR, "data", align_op_file), "r") as f:
        alignments = f.read()

    return alignments.split("\n")

if __name__ == '__main__':
    pass