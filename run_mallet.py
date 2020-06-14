import argparse
from gensim import corpora
from gensim.test.utils import common_corpus, common_dictionary
from gensim.models.wrappers import LdaMallet
import os
import time

if __name__ == "__main__":

    print("Starting...")
    start_time = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Input file to read for modeling", required=True)
    parser.add_argument("--num_topics", '-k', default=30, type=int, help="Number of Topics to Generate", required=True)
    parser.add_argument("--model_name", help="Input file to read for modeling", required=True)

    args = parser.parse_args()

    path_to_mallet_binary = os.environ.get("MALLET_BINARY", 
        "/Users/hiancheong/Personal/grad/UMD/comp_ling/topics_evaluation/mallet-2.0.8/bin/mallet")

    # Read the file
    print("Loading file...")
    reader = open(args.input)
    lines = [line.replace("\n", "") for line in reader.readlines()]
    texts = [line.split(" ") for line in lines]

    print("File Loaded...")
    dictionary = corpora.Dictionary(texts)
    dictionary.save(f'dicts/{args.model_name}.dict')  # store the dictionary, for future reference
    corpus = [dictionary.doc2bow(text) for text in texts]
    print("Beginning LDA...")
    model = LdaMallet(path_to_mallet_binary, corpus=corpus, num_topics=args.num_topics, id2word=dictionary)
    model.print_topics()

    model.save(f"models/{args.model_name}.model")
    end_time = time.time()
    print(f"Elapsed Time: {end_time - start_time}")