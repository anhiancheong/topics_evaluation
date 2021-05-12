"""
This script will generate a topics 'ratings' survey based on a topics survey
"""
import argparse
import json
import random

from survey_utils import load_topics_file, format_survey_blocks, update_survey_blocks_element, load_multi_topics_file


def format_ratings_question(question_id, topic_id, terms, model_name="topics", top_terms=10, include_confidence=False):
    """
    NOTE: The last value in terms should be the intruder word
    """
    data_export_tag = f"{model_name}_{topic_id}"
    terms_strings = ", ".join(terms[:top_terms])
    
    ratings_question = {
        'SurveyID': 'SV_4My2xeJALXVC80l',
        'Element': 'SQ',
        'PrimaryAttribute':  f'QID{question_id}',
        'SecondaryAttribute': f'How related are the following terms: {terms_strings}',
        'TertiaryAttribute': None,
        'Payload': {'QuestionText': f'<span style="font-weight: bolder;">How related are the following terms:</span><div><b>{terms_strings}</b></div>',
            'DataExportTag': data_export_tag,
            'QuestionType': 'MC',
            'Selector': 'SAHR',
            'SubSelector': 'TX',
            'DataVisibility': {'Private': False, 'Hidden': False},
            'Configuration': {'QuestionDescriptionOption': 'UseText',
            'LabelPosition': 'BELOW'},
            'QuestionDescription': f'How related are the following terms: {terms_strings}',
            'Choices': {'1': {'Display': 'Not Very Related'},
            '2': {'Display': 'Somewhat Related'},
            '3': {'Display': 'Very Related'}},
            'ChoiceOrder': ['1', '2', '3'],
            'Validation': {'Settings': {'ForceResponse': 'ON',
            'ForceResponseType': 'ON',
            'Type': 'None'}},
            'Language': [],
            'NextChoiceId': 4,
            'NextAnswerId': 1,
            'QuestionID': f'QID{question_id}'
            }
        }

    ratings_question_confidence = {
        "SecondaryAttribute": "Please rate how related the following terms are to each other and how confident you are in your a...", 
        "TertiaryAttribute": None, 
        "Element": "SQ", 
        "SurveyID": "SV_cGgwR9yoWhFLjSK", 
        "Payload": {
            "QuestionType": "MC", 
            "QuestionID": f'QID{question_id}', 
            "Validation": {
            "Settings": {
                "Type": "None", 
                "ForceResponse": "OFF"
            }
            }, 
            "QuestionText": f"<div>Please rate how related the following terms are to each other and how confident you are in your answer:</div><div><br><div> {terms_strings} </div></div>", 
            "Language": [], 
            "NextChoiceId": 6, 
            "GradingData": [], 
            "NextAnswerId": 1, 
            "Selector": "MAVR", 
            "QuestionDescription": "Please rate how related the following terms are to each other and how confident you are in your a...", 
            "DataVisibility": {
            "Hidden": False, 
            "Private": False
            }, 
            "DefaultChoices": False, 
            "ChoiceOrder": [
            1, 
            2, 
            3, 
            4, 
            5
            ], 
            "SubSelector": "TX", 
            "DataExportTag": data_export_tag, 
            "Choices": {
            "1": {
                "Display": "Not very related"
            }, 
            "3": {
                "Display": "Very related"
            }, 
            "2": {
                "Display": "Somewhat related"
            }, 
            "5": {
                "Display": "I am <em><strong>not</strong></em> confident in my rating"
            }, 
            "4": {
                "Display": "I am confident in my rating"
            }
            }, 
            "Configuration": {
            "QuestionDescriptionOption": "UseText"
            }, 
            "ChoiceGroups": {
            "cg_2": {
                "GroupLabel": "Answer Confidence", 
                "Options": {
                "Selection": "SAWithinGroup"
                }, 
                "ChoiceGroupOrder": [
                4, 
                5
                ]
            }, 
            "cg_1": {
                "Randomization": {
                "Type": "None"
                }, 
                "GroupLabel": "Rating", 
                "Options": {
                "Selection": "SAWithinGroup"
                }, 
                "ChoiceGroupOrder": [
                1, 
                2, 
                3
                ]
            }
            }, 
            "ChoiceGroupOrder": [
            "cg_1", 
            "cg_2"
            ]
        }, 
        "PrimaryAttribute": f'QID{question_id}'
    }
    
    return ratings_question_confidence if include_confidence else ratings_question

if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-f", "--file", dest="file", help="File path for input files", required=True)
    arg_parser.add_argument("-o", "--output", dest="output", help="Output file name", required=True)
    arg_parser.add_argument("-n", "--num_topics", dest="num_topics",
                            type=int, help="Number of Topics to sample",
                            default=20)
    arg_parser.add_argument("-m", "--model_name", dest="model_name", help="Useful model name param", default="topics")
    arg_parser.add_argument("--include_confidence", dest="include_confidence", action="store_true", default=False, help="Include an option specify confidence")
    arg_parser.add_argument("--multi", dest="multi", help="Multi topic file experiment", default=None)
    arg_parser.add_argument("--file_2", dest="file_2", help="Second topic file")
    arg_parser.add_argument("--model_name_2", dest="model_name_2", help="Useful model name param for the second topic file")

    args = arg_parser.parse_args()

    survey_template = json.load(open("Topic_Ratings_Template.qsf"))

    question_id = 3
    questions = []

    if args.multi:
        topics_1 = load_multi_topics_file(args.file, args.model_name)[args.multi]
        topics_2 = load_multi_topics_file(args.file_2, args.model_name_2)[args.multi]

        #all_topics = topics_1[args.multi] + topics_2[args.multi]

        selected_topics_idxs_1 = random.sample(range(len(topics_1)), args.num_topics)
        selected_topics_idxs_2 = random.sample(range(len(topics_2)), args.num_topics)
        print(f"Selected the following topics for ratings from model 1: {selected_topics_idxs_1}")
        print(f"Selected the following topics for ratings from model 2: {selected_topics_idxs_2}")

        for topic_idx in selected_topics_idxs_1:
            topic = topics_1[topic_idx]
            questions.append(
                format_ratings_question(
                    question_id=question_id,
                    topic_id=topic["topic_id"],
                    terms=topic["terms"],
                    model_name=args.model_name,
                    include_confidence=args.include_confidence
                )
            )
            question_id += 1

        for topic_idx in selected_topics_idxs_2:
            topic = topics_2[topic_idx]
            questions.append(
                format_ratings_question(
                    question_id=question_id,
                    topic_id=topic["topic_id"],
                    terms=topic["terms"],
                    model_name=args.model_name_2,
                    include_confidence=args.include_confidence
                )
            )
            question_id += 1
    else:
        all_topics = load_topics_file(args.file)
        
        selected_topics_idxs = random.sample(range(len(all_topics)), args.num_topics)
        print(f"Selected the following topics for ratings: {selected_topics_idxs}")

        for topic_idx in selected_topics_idxs:
            topic = all_topics[topic_idx]
            questions.append(
                format_ratings_question(
                    question_id=question_id,
                    topic_id=topic["topic_id"],
                    terms=topic["terms"],
                    model_name=args.model_name,
                    include_confidence=args.include_confidence
                )
            )
            question_id += 1

    print(f"Generating {len(questions)} questions")

    if survey_template["SurveyElements"][0]["PrimaryAttribute"] == "Survey Blocks":
        update_survey_blocks_element(
            survey_template["SurveyElements"][0], 
            questions
        )
        
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

    survey_template["SurveyEntry"]["SurveyName"] = f"Ratings {args.model_name.title()}"

    json.dump(survey_template,
            open(f"{args.output}.qsf", "w+"),
            indent=2)
    


    