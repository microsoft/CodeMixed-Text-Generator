import os
import sys
import logging
import shutil
import time
import cm_text_generator.bench
import multiprocessing
import tempfile
import random
import functools
import nltk

from configparser import ConfigParser

open_file = functools.partial(open, encoding='utf-8')

def get_config():
    config = ConfigParser()
    config.read("config.ini")
    config_pregcm = config["PREGCM"]
    config_gcm = config["GCM"]
    config_general = config["GENERAL"]
    config_output = config["OUTPUT"]
    return config_pregcm, config_gcm, config_general, config_output

def run_in_try(func, pipe, params):
    try:
        ret = func(params)
    except Exception as e:
        ret = "fail"
    pipe.send(ret)
    pipe.close()

def lang_tag(gcm_raw_output, parse_string_src, source_lang, target_lang):
    # l = gcm_raw_output
    # print("\n>>>>>>>>>>>>\n", "len(l):", len(l), "\nlen(l[0]):", len(l[0]), "\nlen(l[0][0]):", len(l[0][0]), "\nl[0][0]", l[0][0],"\nl[0][1]", l[0][1], "\n>>>>>>>>>>>>")
    source_lang = source_lang.upper()
    target_lang = target_lang.upper()
    tagged_strings = []
    
    for i in gcm_raw_output:
        string, parse_string_cm = i[0], i[1]
        tokens = string.split()
        parse_tree = nltk.tree.Tree.fromstring(parse_string_src)
        leaves = parse_tree.leaves()
        tagged_tokens = []
        for token in tokens:
            if token in leaves:
                tagged_tokens.append('{}/{}'.format(token, target_lang))
            else:
                tagged_tokens.append('{}/{}'.format(token, source_lang))
        tagged_strings.append((' '.join(tagged_tokens), parse_string_cm))
    return tagged_strings

def run_sh(inpfile, outfile, source_lang, target_lang, k, lid_output):
    logger = logging.getLogger(__name__)
    working_dir = "{}/cm_text_gnenerator/generator/"
    errfile = '{}.err'.format(inpfile)
    shutil.rmtree("{}onetweet-{}-{}.txt".format(working_dir,
                                                source_lang, target_lang), ignore_errors=True)
    shutil.rmtree(outfile, ignore_errors=True)
    count = 0
    outputs = []
    out_string = ""
    with open_file(inpfile, 'r') as inpfile_f:
        for line in inpfile_f.read().split('\n'):
            if line != "":
                out_string += line + '\n'
            else:
                arguments = out_string.split('\n')
                out_string = ""

                '''
                In the original bash version, this function/file was called with a timeout of 1s
                For some test sentences, when the dfa is being minimized, the code runs into an infinite loop
                The exact reason for the infinite loop hasn't been looked into
                Hence, to get the code to atleast run, it is being called in a separate process with a 10 sec timeout
                '''
                source, dest = multiprocessing.Pipe()
                p = multiprocessing.Process(target=run_in_try, args=(
                    cm_text_generator.bench.main, source, arguments,))
                p.start()
                t = 10
                p.join(t)
                ret = 'fail'
                if p.exitcode is not None and p.exitcode >= 0:
                    ret = dest.recv()
                dest.close()
                p.terminate()
                if type(ret) != str and len(ret) > 0:
                    # random sample only if k != -1
                    if k !=-1 and len(ret) >= k:
                        ret = random.sample(ret, k)
                    # word level language tagging
                    if lid_output == 1:
                        ret = lang_tag(ret, arguments[3], source_lang, target_lang)
                    outputs.append(ret)
    # print("RAW OUTPUTS:\n", outputs)
    return outputs


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(name)s: %(funcName)s: %(levelname)s: %(asctime)s: %(message)s",
        handlers=[
            # logging.FileHandler(filename=path),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)

    # setup file paths using config file
    config_pregcm, config_gcm, config_general, config_output = get_config()
    lang1 = config_general["language_1"] if config_general["language_1"] else "HINDI"
    lang1_code = lang1.lower()[:2]
    lang2 = config_general["language_2"] if config_general["language_2"] else "ENGLISH"
    lang2_code = lang2.lower()[:2]
    input_loc = config_general["input_loc"] if config_general["input_loc"] else "data"
    pregcm_output_loc = config_pregcm["pregcm_output_loc"] if config_pregcm["pregcm_output_loc"] else lang1_code + "-to-" + lang2_code 
    gcm_input_loc = config_gcm["gcm_input_loc"] if config_gcm["gcm_input_loc"] else pregcm_output_loc
    gcm_output_loc = config_gcm["gcm_output_loc"] if config_gcm["gcm_output_loc"] else lang1_code + "-to-" + lang2_code + "-gcm"
    k = int(config_gcm["k"]) if config_gcm["k"] else 5
    lid_output = int(config_output["lid_output"]) if config_output["lid_output"] else 0

    # setup root directory
    root_dir = os.getcwd()
    logger.info("ROOT DIR: {}".format(root_dir))
    logger.info("generating code mixed sentences")

    # setup input and output directories
    inputdir = os.path.join(input_loc, gcm_input_loc)
    outdir = os.path.join(input_loc, gcm_output_loc)
    while not os.path.exists(inputdir):
        logger.info("{} does not exist".format(inputdir))
        time.sleep(30)
    shutil.rmtree(outdir, ignore_errors=True)
    os.makedirs(outdir)

    # setup initial variables
    count_file = "{}/count".format(inputdir)
    source_lang = lang1_code
    target_lang = lang2_code
    block = 500
    with open_file(count_file, "r") as f:
        end = int(f.read())
    outputs = []

    # iterate over all the files of a block and start the generation process
    for value in range(0, end, block):
        while not os.path.exists("{}/flag-cm-{}-{}-{}.txt".format(inputdir, source_lang, target_lang, value)):
            logger.info("Waiting for file starting at {}".format(value))
            time.sleep(30)
        arguments = ['{}/input-cm-{}-{}-{}.txt'.format(inputdir, source_lang, target_lang, value),
                '{}/out-cm-{}-{}-{}.txt'.format(outdir,
                                                source_lang, target_lang, value),
                source_lang,
                target_lang,
                k,
                lid_output,
                ]
        logger.info("Generating for {} to {}".format(
            value, min(end, value + block)))

        # calling the generation code
        outputs.extend(run_sh(*arguments))

    # writing the generations to the output file
    finaloutput = ""
    for i in outputs:
        for j in i:
            finaloutput += "[CM]" + j[0] + "\n[TREE]" + j[1] + "\n"
    outfile = '{}/out-cm-{}-{}.txt'.format(outdir, source_lang, target_lang)
    with open(outfile, 'w') as f:
        f.write(finaloutput)
    logger.info("Sentence Generation Done")
