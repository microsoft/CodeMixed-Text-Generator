import os
import logging
import tempfile
import subprocess
import re

from configparser import ConfigParser

import numpy as np

def get_config():
    config = ConfigParser()
    config.read("config.ini")
    config_aligner = config["ALIGNER"]
    config_general = config["GENERAL"]
    return config_general, config_aligner

def read_data(input_loc, lang1_in_file, lang2_in_file):
    with open(os.path.join(input_loc, lang1_in_file), "r") as f:
        lang1_in = f.read().strip().split("\n")
    with open(os.path.join(input_loc, lang2_in_file), "r") as f:
        lang2_in = f.read().strip().split("\n")
    return lang1_in, lang2_in

def clean_sentence(sent):
    return re.sub(r"[()]", "", re.sub(r"\s+", " ", re.sub(r"([?!,.])", r" \1 ", sent))).strip()

def write_pfms(indices, total_length, pfms_file, lang1_code, lang2_code):
    if not pfms_file:
        pfms_scores = ["0.0" for _ in range(total_length)]
    else:
        with open(os.path.join(input_loc, pfms_file), "r") as f:
            lines = f.read().split("\n")
        pfms_scores = []
        for index in indices:
            pfms_scores.append(lines[index])

    pfms_file = lang1_code + "-to-" + lang2_code + "_pfms.txt"
    with open(os.path.join(output_loc, pfms_file), "w") as f:
        f.write("\n".join(pfms_scores))

def fast_align(pfms_file, lang1_code, lang2_code, align_op_file, lang1_op_file, lang2_op_file):
    total_length = len(lang1_in)

    with tempfile.TemporaryDirectory() as tmpdir:
        root_dir = os.getcwd()

        with open("{}/parallel".format(tmpdir), "w") as f:
            lines = ["{} ||| {}".format(lang1_s, lang2_s) for lang1_s, lang2_s in zip(lang1_in, lang2_in)]
            f.write("\n".join(lines))

        path_to_fast_align = "{}/alignment_generator/fast_align-master/build".format(root_dir)
        subprocess_call = ["{}/fast_align".format(path_to_fast_align),
                            "-i",
                            "{}/parallel".format(tmpdir),
                            "-o",
                            "-v"
                            ]
        os.makedirs("{}/fast_align".format(tmpdir), exist_ok=True)
        with open("{}/fast_align/forward.align".format(tmpdir), "w") as stdout:
            subprocess.run(subprocess_call, stdout=stdout)
        subprocess_call.append("-r")
        with open("{}/fast_align/reverse.align".format(tmpdir), "w") as stdout:
            subprocess.run(subprocess_call, stdout=stdout)
        subprocess_call = ["{}/atools".format(path_to_fast_align),
                            "-c",
                            "grow-diag-final-and",
                            "-i",
                            "{}/fast_align/forward.align".format(tmpdir),
                            "-j",
                            "{}/fast_align/reverse.align".format(tmpdir)
                            ]
        with open("{}/alignments".format(tmpdir), "w") as stdout:
            subprocess.run(subprocess_call, stdout=stdout)
        logger.info("Generating Alignments Done")

        with open("{}/alignments".format(tmpdir), "r") as f:
            align_in = f.read().split("\n")

        indices = [_ for _ in range(total_length)]
        lang1_op = []
        lang2_op = []
        align_op = []

        for index in indices:
            lang1_op.append(lang1_in[index])
            lang2_op.append(lang2_in[index])
            align_op.append(align_in[index])

        os.makedirs(output_loc, exist_ok=True)
        with open(os.path.join(output_loc, lang1_op_file), "w") as f:
            f.write("\n".join(lang1_op))
        with open(os.path.join(output_loc, lang2_op_file), "w") as f:
            f.write("\n".join(lang2_op))
        with open(os.path.join(output_loc, align_op_file), "w") as f:
            f.write("\n".join(align_op))

        # Writes PFMS file
        write_pfms(indices, total_length, pfms_file, lang1_code, lang2_code)

if __name__ == "__main__":
    # setup logging
    logger = logging.getLogger(__name__)

    # setup file paths using config file
    config_general, config_aligner = get_config()
    lang1 = config_general["language_1"] if config_general["language_1"] else "HINDI"
    lang1_code = lang1.lower()[:2]
    lang2 = config_general["language_2"] if config_general["language_2"] else "ENGLISH"
    lang2_code = lang2.lower()[:2]
    input_loc = config_general["input_loc"] if config_general["input_loc"] else "data"
    output_loc = config_general["output_loc"] if config_general["output_loc"] else "data"
    lang1_in_file = config_aligner["source_inp_file"] if config_aligner["source_inp_file"] else lang1_code + "-to-" + lang2_code + "-input_lang1"
    lang2_in_file = config_aligner["target_inp_file"] if config_aligner["target_inp_file"] else lang1_code + "-to-" + lang2_code + "-input_lang2"
    lang1_op_file = config_aligner["source_op_file"] if config_aligner["source_op_file"] else lang1_in_file
    lang2_op_file = config_aligner["target_op_file"] if config_aligner["target_op_file"] else lang2_in_file
    pfms_file = config_aligner["pfms_file"]
    align_op_file = config_aligner["align_op_file"] if config_aligner["align_op_file"] else lang1_code + "-to-" + lang2_code + "-input_parallel_alignments"

    # read data
    lang1_in, lang2_in = read_data(input_loc, lang1_in_file, lang2_in_file)

    # clean data
    for i in range(len(lang1_in)):
        lang1_in[i] = clean_sentence(lang1_in[i])
    for i in range(len(lang2_in)):
        lang2_in[i] = clean_sentence(lang2_in[i])

    # check if both files are of equal length
    try:
        assert len(lang1_in) == len(lang2_in)
    except AssertionError:
        logger.error("Mismatch in length of {lang1} ({lang1_len}) and {lang2} ({lang2_len}) \
                    sentences".format(lang1 = lang1, lang1_len = len(lang1_in), lang2 = lang2, lang2_len = len(lang2_in)))
        exit()

    # Learn alignments on all sentences
    fast_align(pfms_file, lang1_code, lang2_code, align_op_file, lang1_op_file, lang2_op_file)
