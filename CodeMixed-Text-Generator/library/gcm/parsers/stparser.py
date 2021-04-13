import os, sys

# adding module search path so that main modules can be imported
LIBR_DIR = os.getcwd()
BASE_DIR = LIBR_DIR.split('library')[0]
sys.path.insert(0, BASE_DIR)

from utils import stanford_parser_interface

def stanford_parser_setup():
    print("Launching stanford parser server...")

    # setup path to java for stanford parser
    path_to_jar = os.path.join(BASE_DIR, "stanford_parser", "stanford_parser_full_2017_06_09", "stanford-parser-3.8.0.jar")
    path_to_models_jar = os.path.join(BASE_DIR, "stanford_parser", "stanford_parser_full_2017_06_09", "stanford-parser-3.8.0-models.jar")
    java_options = ["-Xms2g", "-Xmx8g"]
    corenlp_options = ["-sentences", "newline"]

    # setup parser server
    parser_server = stanford_parser_interface.LexParserServer(
        path_to_jar=path_to_jar, path_to_models_jar=path_to_models_jar, java_options=java_options, corenlp_options=corenlp_options)
    server_port = parser_server.port
    parser_server.start()

    return server_port, parser_server

def parse(text_to_parse):
    stanford_server_port, stanford_parser_server = stanford_parser_setup()
    parsed_output = []

    print("parsing sentences...")
    for sent in text_to_parse.split("\n"):
        if sent != '':
            parsed_sent = stanford_parser_interface.parse_sentence(sent, stanford_server_port)
            parsed_output.append(parsed_sent)

    # shutdown stanford parser server
    stanford_parser_server.stop()

    return parsed_output


if __name__ == '__main__':
    pass