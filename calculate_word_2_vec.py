import gensim
import gensim.models
import gensim.models.word2vec

import argparse

def main(args):

    if args.directory:
        sentences = gensim.models.word2vec.PathLineSentences(args.input)
        model = gensim.models.word2vec.Word2Vec(
            sentences=sentences,
            size=100,
            window=10
        )

    else:
        model = gensim.models.word2vec.Word2Vec(
            corpus_file=aargs.input,
            size=100,
            window=10
        )

    model.save(args.output)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", help="Input Line Sentence File to use", required=True)
    parser.add_argument("-o", "--output", help="Output filename", required=True)
    parser.add_argument("-d", "--directory", help="Specify is processing a directory of files", action="store_true", required=False)

    args = parser.parse_args()

    main(args)