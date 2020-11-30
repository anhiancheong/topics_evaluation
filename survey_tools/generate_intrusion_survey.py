"""
Script for generating a Word Intrusion Qualtrics Experiment

Input should be a file of topics in the following form:
- 1 Topic per line
- Topic terms are in descending order of model weights (highest weights at the beginning of the line)
- Terms are comman separated
- NOTE: We will use the 'line index' value for the topic ids in order to preserve some record of which topics
        are being analyzed
"""

import argparse
import json
import random

from survey_utils import load_topics_file, format_survey_blocks

def load_topics_file(filepath):
    reader = open(filepath)
    topics = []
    for idx, line in enumerate(reader.readlines()):
        topics.append(
            {
                "topic_id": idx,
                "terms": line.replace("\n", "").split(",")
            }
        )
    return topics

def setup_word_intrusion(topics_list, n=20, topic_idxs=None):
    """
    topics_list: format is a list of dicts [
        {"topic_id": 1, "terms": ["a","b","c"]},
        {"topic_id": 2, "terms": ["a","b","c"]}
    ]
    This is the format given out of the gensim wrapper for Mallet
    
    n: The number of topics to sample
    """
    # Can't sample more than the available topics
    assert len(topics_list) >= n
    
    intruder_list = []
    # Generate n random ints for the selection of topics we'll conduct intrusion on
    if not topic_idxs:
        topic_idxs = random.sample(range(len(topics_list)), n)
        
    for topic_idx in topic_idxs:
        # select another topic from which to grab a term, exclude the current topic
        random_topic_idx = random.choice([idx for idx in range(0, len(topics_list)) if (idx != topic_idx and idx not in topic_idxs)])

        # take the top 5 words of the current topic and ONE of the top 5 terms from the top of the other topic
        # assert that the new word is not in the top 50 words of the original topic
        correct_words = [word for word in topics_list[topic_idx]["terms"][:5]]
        
        # This collects the top 50 words of the current topic
        top_topic_words = [word for word in topics_list[topic_idx]["terms"][:50]]

        # This collects the top words of the 'intruder' topics that do NOT overlap with any of the top
        # 10 words of the other topic
        top_random_words = [word for word in topics_list[random_topic_idx]["terms"][:5] \
                            if word not in top_topic_words]
        
        # EDGE-CASE - The top 50 words of the selected topic may overlap heavily with the
        # 'intruder' topics's top words. In this case, narrow down the set of excluded terms
        # for the current topic to just the top 10. If that doesn't work, then..... skip??
        if not top_random_words:
            top_topic_words = [word for word in topics_list[topic_idx]["terms"][:10]]
            top_random_words = [word for word in topics_list[random_topic_idx]["terms"][:5] \
                                if word not in top_topic_words]
        
            if not top_random_words:
                print(f"Skipping word intrusion for topic {topic_idx} with intruder {random_topic_idx}")
                continue
        # select the intruder word
        selected_intruder = random.choice(top_random_words)
        
        print(topic_idx, random_topic_idx, correct_words + [selected_intruder])
        
        # The last word in each list is the 'intruder', this should be randomized before showing
        #[topics_list[topic_idx]["topic_id"]] + correct_words + [selected_intruder]
        intruder_list.append(
            {
                "topic_id": topics_list[topic_idx]["topic_id"],
                "intruder_id": topics_list[random_topic_idx]["topic_id"],
                "intruder_term": selected_intruder,
                "topic_terms": correct_words
            }
            )
    return intruder_list

def format_intruder_question(question_id, topic_id, topic_intruder_id, terms, model_name="topics"):
    """
    NOTE: The last value in terms should be the intruder word
    """
    data_export_tag = f"{model_name}_{topic_id}_{topic_intruder_id}"

        #{'0': {'Display': 'Andrew'}, '1': {'Display': 'Eric'}, '2': {'Display': 'Claire'}, '3': {'Display': 'Riley'},
        #'4': {'Display': 'Daniel'}, '5': {'Display': 'Potato'}}
    choices = { str(idx + 1): {"Display": term} for idx,term in enumerate(terms)}

    choice_order = [i for i in range(0, len(choices))]

    intruder_question = {
        "SurveyID": "SV_5sXmuibskKlpHmJ",
        "Element": "SQ",
        "PrimaryAttribute": f'QID{question_id}',
        "SecondaryAttribute": "This survey will ask you to evaluate the outputs of a Machine Learning computer model.\u00a0Researcher..",
        "TertiaryAttribute": None,
        'Payload': {
            'QuestionText': 'Identify which word does not belong with the others',
            'DefaultChoices': False,
            'DataExportTag': data_export_tag,
            'QuestionType': 'MC',
            'Selector': 'SAVR',
            'SubSelector': 'TX',
            'DataVisibility': {'Private': False, 'Hidden': False},
            'Configuration': {'QuestionDescriptionOption': 'UseText'},
            'QuestionDescription': 'Identify which word does not belong with the others',
            'Choices': choices,
            'ChoiceOrder': choice_order,
            'Randomization': {'Advanced': None, 'Type': 'All', 'TotalRandSubset': ''},
            'Validation': {'Settings': {'ForceResponse': 'ON',
                'ForceResponseType': 'ON',
                'Type': 'None'}},
            'GradingData': [],
            'Language': [],
            'NextChoiceId': len(choices) + 1,
            'NextAnswerId': 1,
            'QuestionID': f'QID{question_id}'}
    }
     
    return intruder_question


if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-f", "--file", dest="file", help="File path for input files", required=True)
    arg_parser.add_argument("-o", "--output", dest="output", help="Output file name", required=True)
    arg_parser.add_argument("-n", "--num_intruders", dest="num_intruders",
                            type=int, help="Number of Topics to generate intruder experiment for",
                            default=20)
    arg_parser.add_argument("-m", "--model_name", dest="model_name", help="Useful model name param", default="topics")

    args = arg_parser.parse_args()
    topics = load_topics_file(args.file)

    intruder_setup = setup_word_intrusion(topics, n=args.num_intruders, topic_idxs=None)
    print(intruder_setup)

    survey_template = json.load(open("Intrusion_Template.qsf"))

    questions = []
    # THIS NEED TO START AT 3 TO TAKE INTO ACCOUNT THE 2 INTRO BLOCKS
    question_id = 3
    for intruder in intruder_setup:
        # This ensures the intruder is always the last work in the list and will be the last encoded term
        full_terms = [term for term in intruder["topic_terms"]]
        full_terms.append(intruder["intruder_term"])

        questions.append(
            format_intruder_question(
                question_id=question_id,
                topic_id=intruder["topic_id"],
                topic_intruder_id=intruder["intruder_id"],
                terms=full_terms,
                model_name=args.model_name)
        )
        question_id += 1
    print(f"Generating {len(questions)} questions")

    # Step 1: Find and tweak the Survey Blocks sections
    if survey_template["SurveyElements"][0]["PrimaryAttribute"] == "Survey Blocks":
        survey_template["SurveyElements"][0] = format_survey_blocks(questions)
        
    # Step 2: Wipe the existing old questions that are there for easy reference
    idx_to_delete = []
    for idx, element in enumerate(survey_template["SurveyElements"]):

        if element["Element"] == "SQ":
            if element.get("Payload", {}).get('QuestionType') == "MC":
                idx_to_delete.append(idx)

    survey_template["SurveyElements"] = [element for idx, element in enumerate(survey_template["SurveyElements"])
                                        if not idx in idx_to_delete]
        
    # Step 3: Append the new questions to the end
    for question in questions:
        survey_template["SurveyElements"].append(question)

    json.dump(survey_template,
            open(f"{args.output}.qsf", "w+"),
            indent=2)



    

