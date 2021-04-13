import os
import sys
import logging
import shutil
import re
import tempfile
import benepar
import functools

from configparser import ConfigParser
from utils import stanford_parser_interface

open_file = functools.partial(open, encoding="utf-8")

if os.name == "nt":
    os.environ["JAVA_HOME"] = "C:\\Program Files\\Java\\jdk1.8.0_221\\"
    # os.environ["PYTHONIOENCODING"] = "utf8"

def get_config():
    config = ConfigParser()
    config.read("config.ini")
    config_aligner = config["ALIGNER"]
    config_pregcm = config["PREGCM"]
    config_general = config["GENERAL"]
    return config_aligner, config_pregcm, config_general

def preprocess_filter_data(lang1_in_file, lang2_in_file, pfms_file, align_op_file, tmpdir, input_loc, max_pfms):
    prefix = tmpdir
    source_file = "{}/input_source".format(prefix)
    target_file = "{}/input_target".format(prefix)
    alignfile = "{}/input_alignments".format(prefix)
    pfmsfile = "{}/input_pfms".format(prefix)
    source_file_ptr = open(source_file, "w")
    target_file_ptr = open(target_file, "w")
    alignfile_ptr = open(alignfile, "w")
    pfmsfile_ptr = open(pfmsfile, "w")

    print(os.path.join(input_loc, lang1_in_file))
    for l1line, l2line, pfms, alignment in zip(open(os.path.join(input_loc, lang1_in_file)), open(os.path.join(input_loc, lang2_in_file)), open(os.path.join(input_loc, pfms_file)), open(os.path.join(input_loc, align_op_file))):
        l1line = l1line.strip()
        l2line = l2line.strip()
        pfms = pfms.strip()
        alignment = alignment.strip()
        if len(l1line) > 0 and len(l2line) > 0 and len(pfms) > 0 and len(alignment) > 0:
            l1len = len(l1line.split(" "))
            l2len = len(l2line.split(" "))
            pfms_score = float(pfms)
            if 3 < l1len <= 100 and 3 < l2len <= 100 and pfms_score <= max_pfms:
                source_file_ptr.write(l1line + "\n")
                target_file_ptr.write(l2line + "\n")
                alignfile_ptr.write(alignment + "\n")
                pfmsfile_ptr.write(pfms + "\n")

    source_file_ptr.close()
    target_file_ptr.close()
    alignfile_ptr.close()
    pfmsfile_ptr.close()

    return source_file, target_file, alignfile, pfmsfile

def write_lines(source_file, target_file, lower_bound, upper_bound):
    with open_file(source_file, "r") as f:
        lines = f.read().strip().split("\n")[lower_bound:upper_bound]
    with open_file(target_file, "w") as f:
        f.write("\n".join(lines))

def stanford_parser_setup(logger):
    logger.info("Launching stanford parser server")

    # setup path to java for stanford parser
    path_to_jar = "stanford_parser/stanford_parser_full_2017_06_09/stanford-parser-3.8.0.jar"
    path_to_models_jar = "stanford_parser/stanford_parser_full_2017_06_09/stanford-parser-3.8.0-models.jar"
    java_options = ["-Xms2g", "-Xmx8g"]
    corenlp_options = ["-sentences", "newline"]

    # setup parser server
    parser_server = stanford_parser_interface.LexParserServer(
        path_to_jar=path_to_jar, path_to_models_jar=path_to_models_jar, java_options=java_options, corenlp_options=corenlp_options)
    server_port = parser_server.port
    parser_server.start()

    return server_port, parser_server


def benepar_setup():
    berkeley_parser = benepar.Parser("benepar_en2")
    return berkeley_parser

def main(parsed_sentences = None):
    # setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(name)s: %(levelname)s: %(asctime)s: %(message)s",
        handlers=[
            # logging.FileHandler(filename=path),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)

    # setup file paths using config file
    config_aligner, config_pregcm, config_general = get_config()
    lang1 = config_general["language_1"] if config_general["language_1"] else "HINDI"
    lang1_code = lang1.lower()[:2]
    lang2 = config_general["language_2"] if config_general["language_2"] else "ENGLISH"
    lang2_code = lang2.lower()[:2]
    input_loc = config_general["input_loc"] if config_general["input_loc"] else "data"
    output_loc = config_general["output_loc"] if config_general["output_loc"] else "data"
    lang1_in_file = config_aligner["source_inp_file"] if config_aligner["source_inp_file"] else lang1_code + "-to-" + lang2_code + "-input_lang1"
    lang2_in_file = config_aligner["target_inp_file"] if config_aligner["target_inp_file"] else lang1_code + "-to-" + lang2_code + "-input_lang2"
    pfms_file = config_aligner["pfms_file"] if config_aligner["pfms_file"] else lang1_code + "-to-" + lang2_code + "_pfms.txt"
    align_op_file = config_aligner["align_op_file"] if config_aligner["align_op_file"] else lang1_code + "-to-" + lang2_code + "-input_parallel_alignments"
    max_pfms = config_pregcm["max_pfms"] if config_pregcm["max_pfms"] else 1
    pregcm_output_loc = config_pregcm["pregcm_output_loc"] if config_pregcm["pregcm_output_loc"] else lang1_code + "-to-" + lang2_code 
    parser = config_pregcm["parser"] if config_pregcm["parser"] else "benepar"

    # setup root directory
    root_dir = os.getcwd()
    logger.info("ROOT DIR: {}".format(root_dir))

    with tempfile.TemporaryDirectory() as tmpdir:
        # preprocess and filter input data using PFMS cut-off score
        source_file, target_file, alignfile, pfmsfile = preprocess_filter_data(lang1_in_file, lang2_in_file, pfms_file, align_op_file, tmpdir, input_loc, max_pfms)
        # setup output directory
        output_dir = os.path.join(output_loc, pregcm_output_loc)
        shutil.rmtree(output_dir, ignore_errors=True)
        os.makedirs(output_dir, exist_ok=True)

        # if parsed sentences are already being sent from the library mode
        if parsed_sentences is None:
            if parser == "benepar":
                berkeley_parser = benepar_setup()
            elif parser == "stanford":
                stanford_server_port, stanford_parser_server = stanford_parser_setup(logger)

        # setup regex
        re1 = re.compile("[\n ]+")
        try:
            block = 500
            # if parsed sentences are already being sent from the library mode
            if parsed_sentences is None:
                logger.info("Starting sentence parsing")

            with open_file(source_file, "r") as f:
                l = f.read().strip().split("\n")
                total = len(l)
            with open("{}/count".format(output_dir), "w") as f:
                f.write(str(total))

            logger.info("Parsing {} sentences".format(total))

            source_s = []
            target_s = []
            pfms_s = []
            align_s = []
            for i, (sourceline, targetline, pfms, alignment) in enumerate(zip(open(source_file), open(target_file), open(pfmsfile), open(alignfile))):
                sourceline = sourceline.strip()
                targetline = targetline.strip()
                pfms = pfms.strip()
                alignment = alignment.strip()
                if len(sourceline) > 0 and len(targetline) > 0 and len(pfms) > 0 and len(alignment) > 0:
                    source_s.append(sourceline)
                    target_s.append(targetline)
                    pfms_s.append(pfms)
                    align_s.append(alignment)
                    if i == total - 1 or i % block == block - 1:
                        lower_bound = i + 1 - block if i != total - 1 else i - (i % block)
                        logger.info("Parsing sentences: {}, {}".format(lower_bound, i))
                        assert len(target_s) == i + 1 - lower_bound
                        # if parsed sentences are already being sent from the library mode
                        if parsed_sentences is None:
                            if parser == "benepar":
                                output = ["(ROOT "+" ".join(str(berkeley_parser.parse(sentence)).split())+")\n" for sentence in target_s]
                            elif parser == "stanford":
                                output = [stanford_parser_interface.parse_sentence(sentence, stanford_server_port) for sentence in target_s]
                            logger.info("Parsed {} sentences".format(len(output)))
                            parsed_output = [re1.sub(" ", t.strip()) for t in output]
                        else:
                            parsed_output = parsed_sentences[lower_bound:i+1]
                            parsed_output = [re1.sub(" ", t.strip()) for t in parsed_output]
                        with open_file(output_dir + "/flag-cm-" + lang1_code + "-" + lang2_code + "-" + str(lower_bound) + ".txt", "w") as f:
                            f.write("{}".format(lower_bound))

                        print("len of source sents:", len(source_s), "len of parse trees:", len(parsed_output))
                        assert len(source_s) == len(parsed_output), "please check the corpus length matches with the number of parse trees"
                        out_string = [
                            "{}\t{}\n{}\n{}\n{}\n{}".format(lower_bound + j, pfms_s[j], source_s[j], target_s[j], parsed_output[j], align_s[j])
                            for j in range(len(source_s))
                        ]

                        with open_file(output_dir + "/input-cm-" + lang1_code + "-" + lang2_code + "-" + str(lower_bound) + ".txt", "w") as f:
                            f.write("\n\n".join(out_string))

                        source_s = []
                        target_s = []
                        pfms_s = []
                        align_s = []
        finally:
            if parser == "stanford":
                stanford_parser_server.stop()

if __name__ == "__main__":
    main()