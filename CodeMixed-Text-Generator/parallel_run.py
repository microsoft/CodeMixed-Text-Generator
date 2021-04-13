import argparse
import os
import subprocess
import math

'''
Splits GCM generation source files into batches based on num_procs
Runs num_procs//2 gcm generation pipelines in parallel
'''


def main():
    parser = argparse.ArgumentParser("Run GCM Generation in parallel")
    parser.add_argument("--data_dir", type=str, required=True, help="Location of GCM source files")
    parser.add_argument("--num_procs", type=int, required=True, help="Number of processes to run in parallel (this is equal to 2 times the number of GCM generation pipelines in parallel)")
    parser.add_argument("--output_dir", type=str, required=True, help="Location to dump output files")
    args = parser.parse_args()

    n_pipelines = args.num_procs // 2

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    for i in range(n_pipelines):
        os.makedirs(os.path.join(args.output_dir, str(i)), exist_ok=True)

    input_files = os.listdir(args.data_dir)
    with open(os.path.join(args.data_dir, input_files[0]), 'r') as f:
        lines = f.read().strip().split('\n')
        num_sentences = len(lines)  # Obtains the total number of sentences on which the generation has to be run on
    print("Num Sentences: {}".format(num_sentences))

    end = 0
    block_size = math.ceil(num_sentences / n_pipelines)  # Calcualted based on number of sentences and number of pipelines

    print("Splitting input files into batches")

    # Splits data into batches of size block_size
    for file_name in input_files:
        with open(os.path.join(args.data_dir, file_name), 'r') as f:
            lines = f.read().strip().split('\n')
        end = 0
        for i in range(n_pipelines):
            # Start and end are calculated based on block_size
            start = end
            end = start + block_size
            if end > num_sentences:
                # Handling value of end for the last batch
                end = num_sentences
            with open(os.path.join(args.output_dir, str(i), file_name), 'w') as f:
                f.write('\n'.join(lines[start:end]))

    pre_gcm_command_template = 'python pre_gcm.py --input-path {} --output-path {}/pre_gcm/ --max-pfms 0.7'
    gcm_command_template = 'python gcm.py --input-path {}/pre_gcm/ --output-path {}/gcm/ --k 5'

    pre_gcm_procs = []
    gcm_procs = []
    for i in range(n_pipelines):
        directory = os.path.join(args.output_dir, str(i))

        pre_gcm_command = pre_gcm_command_template.format(directory, directory)
        gcm_command = gcm_command_template.format(directory, directory)

        print(pre_gcm_command)
        print(gcm_command)

        # Runs pre_gcm and gcm commands
        # Stdout of both programs are logged to pre_gcm_out and gcm_out in the respective batch's folders
        pre_gcm_procs.append(subprocess.Popen(pre_gcm_command.split(' '), stdout=open(os.path.join(args.output_dir, str(i), 'pre_gcm_out'), 'w')))
        gcm_procs.append(subprocess.Popen(gcm_command.split(' '), stdout=open(os.path.join(args.output_dir, str(i), 'gcm_out'), 'w')))

    # Waits for process completion
    # Kills all processes if a KeyboardInterrupt is recieved
    try:
        for p in pre_gcm_procs:
            p.wait()
        for p in gcm_procs:
            p.wait()
    except KeyboardInterrupt:
        for p in pre_gcm_procs:
            p.kill()
        for p in gcm_procs:
            p.kill()


if __name__ == "__main__":
    main()
