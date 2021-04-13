# Batch Mode Documentation
---

The Batch mode is the most complete interface among the three due to the high amount of flexibility it provides for CM corpus generation. 

Apart from the general instructions regarding running of this mode that are provided in the README.md, here is some additional info about this mode:

- This mode is controlled by the `CodeMixed-Text-Generator/config.ini` file. 

- Also note that since both the Library mode and the Web UI mode are built on top of Batch mode, the config file is capable of controlling specific aspects of CM generation for both of those interfaces. 

- The **config.ini** file has 6 sections (GENERAL, ALIGNER, PREGCM, GCM, OUTPUT, WEB) each dealing with a specific sub-component of the GCM tool.

- Each section have parameters that can be changed for different experimental setttings.

- Most of the parameters are self-explanatory (have descriptions in the config file) and have default values.

The following are some of the variations that can be included in the CM generation process and the parameters that deal with them in the config file:

## I. Control which stages to run

The GCM process is sequential in nature and involves running the Aligner, Pre-GCM and GCM stage to produce the final output. When experimenting, you might want to run only particular stages at times. 

For example, running only the Aligner stage to generate alignments or re-running only the GCM stage in repeated experiments etc.

You can control that by passing in a comma-separated names of the stages to be run to the `stages_to_run` parameter under the `GENERAL` section of the config file:

```
# choose which stages of the pipeline are going to be run; default: pregcm, gcm
stages_to_run = aligner, pregcm
```

## II. Select a specific parser

The quality and style of generated CM sentence directly depends upon the quality of the parse trees given as input. Parsers are known to differ in their parsing methodologies and a lot of times give different parse trees for the same input sentences. It is something that we noticed in our internal experiments. Hence, for diversity of use, we currently support two very good parsers:

a. Berkeley Neural Parser (Benepar)
b. Stanford Parser

You can choose which parser you want to work with using the `parser` parameter in the `PREGCM` section of the config file:

```
# select the parser to be used from available parsers - stanford and benepar; default: benepar
parser = stanford
```

## III. Sample the GCM output

We support two types of sampling currently: Random Sampling and SPF based Sampling, here's how you can enable either:

### a.) Random Sampling

In order to enable this sampling, simply set the parameter `k` under the `GCM` section of the config file with the number of CM sentences you want sampled from the generated corpus:

```
# max number of sentences to generate per sentence, set -1 for getting all the generations; default: 5
k = -1
```

A value of `-1` means that all the generated CM will be in the output, any other number will force the GCM to sample that many sentences.

### b.) SPF based Sampling

In order to enable this sampling, simply set the parameter `sampling` under the `OUTPUT` section of the config file to `spf`:

```
# sampling technique to use - random or spf; default: random
sampling = spf
```

By default, the sampling method is random.

Once you've set the sampling type, then you have to set `k` in `GCM` section to the number of sentences you want to be sampled for the output.

## IV. Choose the linguistic theory to be used for CM generation

We support two linguistic theories currenlty: Equivalence-Constraint (EC) and Matrix Language (ML) theory, you can choose either of the two from the `linguistic_theory` parameter in `GCM` section of the config file:

```
# which theory to choose for generating cm sentences 'ec' (ec theory) or 'ml' (ml theory); default ec
linguistic_theory = ml
```

By default, EC theory is used.