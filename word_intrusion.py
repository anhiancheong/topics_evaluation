import csv
import random

def setup_word_intrusion(topics_list, n=20):
    """
    topics_list: format is a list of tuples [
    (topic_id, [(word, score),(word, score),(word, score)]),
    (topic_id, [(word, score),(word, score),(word, score)])]
    This is the format given out of the gensim wrapper for Mallet
    
    n: The number of topics to sample
    """
    # Can't sample more than the available topics
    assert len(topics_list) > n
    
    intruder_list = []
    # Generate n random ints for the selection of topics we'll conduct intrusion on
    topic_idxs = random.sample(range(len(topics_list)), n)
    for topic_idx in topic_idxs:
        # select another topic from which to grab a term, exclude the current topic
        random_topic_idx = random.choice([idx for idx in range(0, len(topics_list)) if idx != topic_idx])

        # take the top 5 words of the current topic and ONE of the top 5 terms from the top of the other topic
        # assert that the new word is not in the top 50 words of the original topic
        correct_words = [word_tuple[0] for word_tuple in topics_list[topic_idx][1][:5]]
        
        # This collects the top 50 words of the current topic
        top_topic_words = [word_tuple[0] for word_tuple in topics_list[topic_idx][1][:50]]

        # This collects the top words of the 'intruder' topics that do NOT overlap with any of the top
        # 10 words of the other topic
        top_random_words = [word_tuple[0] for word_tuple in topics_list[random_topic_idx][1][:5] \
                            if word_tuple[0] not in top_topic_words]
        
        # EDGE-CASE - The top 50 words of the selected topic may overlap heavily with the
        # 'intruder' topics's top words. In this case, narrow down the set of excluded terms
        # for the current topic to just the top 10. If that doesn't work, then..... skip??
        if not top_random_words:
            top_topic_words = [word_tuple[0] for word_tuple in topics_list[topic_idx][1][:10]]
            top_random_words = [word_tuple[0] for word_tuple in topics_list[random_topic_idx][1][:5] \
                                if word_tuple[0] not in top_topic_words]
        
            if not top_random_words:
                print(f"Skipping word intrusion for topic {topic_idx} with intruder {random_topic_idx}")
                continue
        # select the intruder word
        selected_intruder = random.choice(top_random_words)
        
        print(topic_idx, random_topic_idx, correct_words + [selected_intruder])
        
        # The last word in each list is the 'intruder', this should be randomized before showing
        intruder_list.append(correct_words + [selected_intruder])
    return intruder_list

def load_topics(path):
    """
    Loads the word_topics.csv file format which has the full weights of every word per topic
    and converts it to the tuple-format that gensim creates and is used to create the word intrusion
    experiment
    """
    reader = csv.DictReader(open(path), delimiter=",")
    topics_list = [(topic_name, []) for topic_name in reader.fieldnames if topic_name != "Word"]
    for idx, row in enumerate(reader):
        for topic_tuple in topics_list:
            topic_name = topic_tuple[0]
            topic_tuple[1].append((row["Word"], row[topic_name]))

    # We need to sort each of the word lists once they are reassembled
    for topic_tuple in topics_list:
        topic_tuple[1].sort(key=lambda t: t[1])
    return topics_list


topics_list = load_topics("/Users/hiancheong/Downloads/export_shro_10topics/word_topics.csv")
topic_intruders = setup_word_intrusion(topics_list, n=5)