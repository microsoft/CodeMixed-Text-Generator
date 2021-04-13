import nltk
import socket
import os
import re
import time
import sys
from nltk.internals import find_jar_iter, config_java, java, _java_options
from nltk.parse.corenlp import CoreNLPServerError, try_port

_stanford_url = 'http://stanfordnlp.github.io/CoreNLP/'

class LexParserServer(object):

    _MODEL_JAR_PATTERN = r'stanford-parser-(\d+)\.(\d+)\.(\d+)-models\.jar'
    _JAR = r'stanford-parser-(\d+)\.(\d+)\.(\d+)\.jar'

    def __init__(
        self,
        path_to_jar=None,
        path_to_models_jar=None,
        verbose=False,
        java_options=None,
        corenlp_options=None,
        port=4466,
    ):
        '''
        if corenlp_options is None:
            corenlp_options = ['-preload']
        '''
        jars = list(
            find_jar_iter(
                self._JAR,
                path_to_jar,
                env_vars=('CORENLP',),
                searchpath=(),
                url=_stanford_url,
                verbose=verbose,
                is_regex=True,
            )
        )

        # find the most recent code and model jar
        stanford_jar = max(jars, key=lambda model_name: re.match(self._JAR, model_name))

        port = try_port()
        corenlp_options.extend(['-port', str(port)])

        self.host = 'localhost'
        self.port = port

        model_jar = max(
            find_jar_iter(
                self._MODEL_JAR_PATTERN,
                path_to_models_jar,
                env_vars=('CORENLP_MODELS',),
                searchpath=(),
                url=_stanford_url,
                verbose=verbose,
                is_regex=True,
            ),
            key=lambda model_name: re.match(self._MODEL_JAR_PATTERN, model_name),
        )

        self.verbose = verbose

        self._classpath = stanford_jar, model_jar
        self.corenlp_options = corenlp_options
        self.java_options = java_options or ['-mx2g']

    def start(self, stdout='devnull', stderr='devnull'):
        """ Starts the CoreNLP server

        :param stdout, stderr: Specifies where CoreNLP output is redirected. Valid values are 'devnull', 'stdout', 'pipe'
        """

        cmd = ['edu.stanford.nlp.parser.server.LexicalizedParserServer']

        if self.corenlp_options:
            cmd.extend(self.corenlp_options)

        # Configure java.
        # default_options = ' '.join(_java_options)
        default_options = ''
        config_java(options=self.java_options, verbose=self.verbose)
        try:
            self.popen = java(
                cmd,
                classpath=self._classpath,
                blocking=False,
                stdout=stdout,
                stderr=stderr,
            )
        finally:
            # Return java configurations to their default values.
            config_java(options=default_options, verbose=self.verbose)

        # Check that the server is istill running.
        returncode = self.popen.poll()
        if returncode is not None:
            _, stderrdata = self.popen.communicate()
            raise CoreNLPServerError(
                returncode,
                'Could not start the server. '
                'The error was: {}'.format(stderrdata.decode('ascii')),
            )

        for i in range(5):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((self.host, self.port))
            except ConnectionRefusedError:
                time.sleep(1)
            else:
                break
        else:
            raise CoreNLPServerError('Could not connect to the server.')

    def stop(self):
        self.popen.terminate()
        self.popen.wait()

    def __enter__(self):
        self.start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False

def parse_sentence(sentence, port, hostname='localhost'):
    command = 'parse ' + sentence + '\n'
    byte_size = 5
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', port))
        s.send(bytes(command, encoding='utf8'))
        d = ''
        data = s.recv(byte_size).decode('utf8', 'ignore')
        while data != '':
            d += data
            data = s.recv(byte_size).decode('utf8', 'ignore')

    return d

def test_parser():
    # parser_dir/stanford_parser/stanford_parser_full_2017_06_09/
    path_to_jar = 'parser_dir/stanford_parser/stanford_parser_full_2017_06_09/stanford-parser-3.8.0.jar'
    path_to_models_jar = 'parser_dir/stanford_parser/stanford_parser_full_2017_06_09/stanford-parser-3.8.0-models.jar'
    # folder_of_jar = 'parser_dir/stanford_parser/stanford_parser_full_2017_06_09/'
    java_options = ['-mx500m', '-Xms2048m', '-Xmx2048m']
    corenlp_options = ['-sentences','newline']#'-model', 'edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz']
    server = LexParserServer(path_to_jar=path_to_jar, path_to_models_jar=path_to_models_jar, java_options=java_options, corenlp_options=corenlp_options)
    port = server.port
    print(port)
    try:
        server.start()#stdout=sys.stdout, stderr=sys.stderr)
        print("testing server")
        t = time.time()
        for _ in range(1000):
            d = parse_sentence('do you have it or not?', port)
        print(d)
        print(time.time()-t)
    finally:
        server.stop()

if __name__ == "__main__":
    test_parser()