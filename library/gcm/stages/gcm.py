import os, subprocess
from configparser import ConfigParser

# adding module search path so that main modules can be imported
LIBR_DIR = os.getcwd()
BASE_DIR = LIBR_DIR.split('library')[0]
DATA_DIR = os.path.join(BASE_DIR, "data")

def get_config():
    config = ConfigParser()
    config.read(os.path.join(BASE_DIR, "config.ini"))
    config_general = config["GENERAL"]
    config_pregcm = config["PREGCM"]
    config_gcm = config["GCM"]
    return config_general, config_pregcm, config_gcm 

def setup_gcm(processed_corpus, block, total_size, lang1_code, lang2_code, pregcm_output_loc):
    for i, _ in enumerate(processed_corpus):
        if i == total_size - 1 or i % block == block - 1:
            lower_bound = i + 1 - block if i != total_size - 1 else i - (i % block)

            # writing flag file
            with open(pregcm_output_loc + "/flag-cm-" + lang1_code + "-" + lang2_code + "-" + str(lower_bound) + ".txt", "w") as f:
                f.write("{}".format(lower_bound))

            # outstring
            out_string = processed_corpus[lower_bound : i+1]

            # writing input file
            with open(pregcm_output_loc + "/input-cm-" + lang1_code + "-" + lang2_code + "-" + str(lower_bound) + ".txt", "w") as f:
                f.write("\n\n".join(out_string))

def gen(processed_corpus):
    config_general, config_pregcm, config_gcm = get_config()
    lang1 = config_general["language_1"] if config_general["language_1"] else "HINDI"
    lang1_code = lang1.lower()[:2]
    lang2 = config_general["language_2"] if config_general["language_2"] else "ENGLISH"
    lang2_code = lang2.lower()[:2]
    pregcm_output_loc = config_pregcm["pregcm_output_loc"] if config_pregcm["pregcm_output_loc"] else lang1_code + "-to-" + lang2_code 
    gcm_output_loc = config_gcm["gcm_output_loc"] if config_gcm["gcm_output_loc"] else lang1_code + "-to-" + lang2_code + "-gcm"
    pregcm_output_loc = os.path.join(DATA_DIR, pregcm_output_loc)
    gcm_op_file = os.path.join(gcm_output_loc, 'out' + '-cm-' + lang1_code + '-' + lang2_code + '.txt') 

    block = 500
    total_size = len(processed_corpus)

    # setup for gcm to run
    print("setting up gcm...")
    setup_gcm(processed_corpus, block, total_size, lang1_code, lang2_code, pregcm_output_loc)

    # run gcm
    os.chdir(BASE_DIR)
    print("running gcm process...")
    p_gcm = subprocess.run(['python', 'sequence_run.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # print((p_gcm.stdout).decode())

    # return output
    with open(os.path.join(DATA_DIR, gcm_op_file)) as outf:
        gcm_out = outf.readlines()
        if len(gcm_out) > 0:
            return gcm_out
        else:
            return 'Sorry, due to bad alignments/input data we could not generate CM for the given sentence.'

if __name__ == '__main__':
    pass