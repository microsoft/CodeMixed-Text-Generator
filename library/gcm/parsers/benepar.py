import benepar

def parse(text_to_parse):
    print("Loading benepar...")
    parser = benepar.Parser("benepar_en2")
    parsed_output = []

    print("parsing sentences...")
    for sent in text_to_parse.split("\n"):
        if sent != '':
            parsed_sent = "(ROOT "+" ".join(str(parser.parse(sent)).split())+")\n"
            parsed_output.append(parsed_sent)

    return parsed_output

if __name__ == '__main__':
    pass