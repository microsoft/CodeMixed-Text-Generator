import os
import subprocess

from configparser import ConfigParser

def get_config():
    config = ConfigParser()
    config.read("config.ini")
    config_general = config["GENERAL"]
    return config_general

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        output = process.stdout.readline()
        if process.poll() is not None:
            break
        if output:
            print(output.decode().strip())
    rc = process.poll()
    return rc

if __name__ == "__main__":
    config_general = get_config()
    stages_to_run = config_general["stages_to_run"] if config_general["stages_to_run"] else "pregcm, gcm"
    stages_to_run = stages_to_run.split(",")
    stages_to_run = [x.strip() for x in stages_to_run]

    if "aligner" in stages_to_run:
        print("====================\n\nSTARTING ALIGNER...\n\n====================")
        p_aligner = run_command(["python", "aligner.py"])
    if "pregcm" in stages_to_run:
        print("====================\n\nSTARTING PRE-GCM...\n\n====================")
        p_pregcm = run_command(["python", "pre_gcm.py"])
    if "gcm" in stages_to_run:
        print("====================\n\nSTARTING GCM...\n\n====================")
        p_gcm = run_command(["python", "gcm.py"])