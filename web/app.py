from flask import Flask, render_template, request
from configparser import ConfigParser
from nltk.tree import Tree
import uuid, json, re, os, subprocess, urllib
import svgling

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

BASE_DIR = os.getcwd().split('web')[0]

# ROUTING CODE BELOW

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate')
def translate():
    return render_template('translate.html')

@app.route('/gcmgen', methods = ['POST', 'GET'])
def gcm_generate():
    # if a POST request is made on this URL then process the form details
    if request.method == 'POST':
        # extracting form information
        source_lang = request.form['inputSourceLang'].upper()
        target_lang = request.form['inputTargetLang'].upper()
        source_sentence = request.form['inputSourceSentence']
        target_sentence = request.form['inputTargetSentence']
        alignment = request.form['inputAlignments']
        linguistic_theory = request.form['linguisticTheory']

        # update the GCM config
        update_gcm_config(source_lang, target_lang, linguistic_theory)

        # set up GCM files
        gcm_op_file = setup_gcm(source_lang, target_lang, source_sentence, target_sentence, alignment)

        # run gcm pipeline
        gcm_output_cm, gcm_output_tree = run_gcm(gcm_op_file)

        # if gcm output is an error
        if gcm_output_tree != -9999:
            gcm_output_cm = gcm_output_cm.split('\n')
            gcm_output_tree = gcm_output_tree.split('\n')
            gcm_output_cm = list(filter(len, gcm_output_cm))
            gcm_output_tree = list(filter(len, gcm_output_tree))

            # gen all the parse trees
            parse_tree_images = gen_parse_trees(gcm_output_tree)

            # once gcm and parse tree is succesfully run, return the view
            output = {v:k for k, v in zip(gcm_output_cm, parse_tree_images)}
            return output

        return gcm_output_cm
    else:
        # if a GET request is made on this URL then simply route to the index page
        return render_template('index.html')

@app.route('/translatetext', methods = ['POST'])
def translate_text():
    # extracting form information
    source_text = request.form.get('inputSourceText', False)
    source_lang = request.form.get('inputSourceLanguage', False)
    target_lang = request.form.get('inputTargetLanguage', False)

    # make a call to azure translator api
    tresponse = get_translation(source_text, source_lang, target_lang)

    # once request is succesfully completed, return the output
    return json.dumps(tresponse, sort_keys=True, indent=4, separators=(',', ': '))

# UTILITY CODE BELOW

def tree2png(treestring, outname):
        IMAGE_DIR = BASE_DIR + 'web/static/images/'
        # convert treestring to a tree using nltk
        t = Tree.fromstring(treestring)
        # draw an svg from the tree
        img = svgling.draw_tree(t)
        svg_data = img.get_svg()
        # save the svg file to the disk
        print('writing generated svg to disk..')
        with open(IMAGE_DIR + 'tmp.svg', 'w', encoding='utf-8') as fp:
                svg_data.write(fp, pretty=True, indent=2)
        # return svg_data
        print('conveting from svg to png..')
        p_convert = subprocess.run(['rsvg-convert', IMAGE_DIR + 'tmp.svg', '-o', IMAGE_DIR + outname], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print('The image file is written to disk:', IMAGE_DIR + outname)
        print((p_convert.stdout).decode())
        print('cleaning up svg..')
        os.remove(IMAGE_DIR + 'tmp.svg')

def gen_parse_trees(gcm_output_tree):
    count = 0
    image_names = []
    for tree in gcm_output_tree:
        # print(tree)
        img = 'image' + str(count) + '.png'
        tree2png(tree, img)
        count += 1
        image_names.append(img)
    return image_names

def gen_alignments(st1, st2, raw_aligns):
    st1_word_boundaries = [(ele.start(), ele.end() - 1) for ele in re.finditer(r'\S+', st1)]
    st2_word_boundaries = [(ele.start(), ele.end() - 1) for ele in re.finditer(r'\S+', st2)]
    st1_word_map, st2_word_map = {}, {}
    for i, w in enumerate(st1_word_boundaries):
        st1_word_map[str(w[0]) + ":" + str(w[1])] = str(i)
    for i, w in enumerate(st2_word_boundaries):
        st2_word_map[str(w[0]) + ":" + str(w[1])] = str(i)
    final_aligns = ''
    for a in raw_aligns.split():
        tmp = a.split('-')
        final_aligns += st1_word_map[tmp[0]] + '-' + st2_word_map[tmp[1]]
        final_aligns += ' '
    return final_aligns

def get_translation(source_text, source_lang, target_lang):
    # read azure subscription from the config file
    config_path = os.path.join(BASE_DIR, 'config.ini')
    config = ConfigParser()
    config.read(config_path)
    subscription_key = config['WEB']['azure_subscription_key'] 

    # setting up the request
    endpoint = 'https://api.cognitive.microsofttranslator.com'
    path = '/translate?api-version=3.0'
    params = '&from=' + source_lang + '&to=' + target_lang + '&includeAlignment=true'
    constructed_url = endpoint + path + params
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4()),
        'Ocp-Apim-Subscription-Region': 'eastus2'
    }
    body = [{
        'text' : source_text
    }]
    # convert body to bytes for urllib
    body = str(json.dumps(body)).encode('utf-8')
    # make a post call to the api url
    req = urllib.request.Request(url=constructed_url, headers=headers, data=body, method='POST')
    request = urllib.request.urlopen(req)
    # parse the recieved bytes into a json
    response = json.loads(request.read())
    # print response to the console
    print(response)

    trans = response[0]['translations'][0]
    # convert alignments into the format that gcm expects
    trans['alignments'] = gen_alignments(source_text, trans['text'], trans['alignment']['proj'])

    return trans

def update_gcm_config(source_lang, target_lang, linguistic_theory):
    config_path = os.path.join(BASE_DIR, 'config.ini')
    config = ConfigParser(comment_prefixes = '/', allow_no_value = True)
    config.read(config_path)

    config.set('GENERAL', 'language_1', source_lang)
    config.set('GENERAL', 'language_2', target_lang)

    config.set('GCM', 'k', '-1')

    with open(config_path, 'w') as cfg:
        config.write(cfg)


def setup_gcm(source_lang, target_lang, source_sentence, target_sentence, alignment):
    data_path = os.path.join(BASE_DIR, 'data')
    lang1_code = source_lang.lower()[:2]
    lang2_code = target_lang.lower()[:2]

    lang1_in_file = lang1_code + '-to-' + lang2_code + '-input_lang1'
    lang2_in_file = lang1_code + '-to-' + lang2_code + '-input_lang2'
    pfms_file = lang1_code + '-to-' + lang2_code + '_pfms.txt'
    align_op_file = lang1_code + '-to-' + lang2_code + '-input_parallel_alignments'
    gcm_op_file = os.path.join(lang1_code + '-to-' + lang2_code + '-gcm', 'out' + '-cm-' + lang1_code + '-' + lang2_code + '.txt') 

    with open(os.path.join(data_path, lang1_in_file), 'w') as l1:
        l1.write(source_sentence+'\n'+'युवा क्रांतिकारियों का एक बड़ा समूह उनके चारों ओर एकत्रित हो गया था .')

    with open(os.path.join(data_path, lang2_in_file), 'w') as l2:
        l2.write(target_sentence+'\n'+'A large group of young revolutionaries had gathered around them .')

    with open(os.path.join(data_path, pfms_file), 'w') as pf:
        pf.write('0.0'+'\n'+'0.0')

    with open(os.path.join(data_path, align_op_file), 'w') as af:
        af.write(alignment+'\n'+'0-4 1-5 2-3 3-0 4-1 5-2 6-9 7-8 8-8 9-7 11-6 12-6 13-1')

    return os.path.join(data_path, gcm_op_file)

def run_gcm(gcm_op_file):
    os.chdir(BASE_DIR)
    p_gcm = subprocess.run(['python', 'sequence_run.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print((p_gcm.stdout).decode())

    with open(gcm_op_file) as outf:
        gcm_out = outf.readlines()
        cm_out, ptree_out = [], []
        if len(gcm_out) > 0:
            for out in gcm_out:
                if out.startswith('[CM]'):
                    out = out.split('[CM]')
                    cm_out.append(out[1])
                elif out.startswith('[TREE]'):
                    out = out.split('[TREE]')
                    ptree_out.append(out[1])
            cm_out = '\n'.join(cm_out)
            ptree_out = '\n'.join(ptree_out)
            return cm_out, ptree_out
        else:
            return 'Sorry, due to bad alignments/input data we could not generate CM for the given sentence.', -9999


if __name__ == '__main__':
    app.run(debug=True)