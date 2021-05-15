import json

def load_multi_topics_file(filepath, model_type):
    topic_file = json.load(open(filepath))
    # first set of keys are the datasets
    datasets = {
      key: [
              {
                  "topic_id": idx,
                  "terms": topic,
                  "model_name": key,
                  "model_type": model_type
              }
              for idx, topic in enumerate(topic_file[key]["topics"])
      ]
      for key in topic_file.keys()
    }
    return datasets


def load_topics_file(filepath, delimiter=","):
    reader = open(filepath)
    # This is risky 'bad' logic for dynamically determining the delimiter
    lines = [line.replace("\t", " ") for line in reader.readlines()]
    if len(lines[0].split(" ")) > len(lines[0].split(",")):
        delimiter = " "
    # Otherwise we use the regular comma delimiter
    print("Delimiter: ", delimiter, "---")
    topics = []
    for idx, line in enumerate(lines):
        topics.append(
            {
                "topic_id": idx,
                "terms": line.replace("\n", "").split(delimiter)
            }
        )
    return topics

def set_redirect_url(survey_elements, redirct_url):
    for element in survey_elements:
        if element["PrimaryAttribute"] == "Survey Options":
            element["Payload"]["EOSRedirectURL"] = redirect_url
        

def update_survey_blocks_element(survey_blocks_element, questions, num_random=25):
    survey_blocks_element["Payload"][-1]["BlockElements"] = [
        {"Type": "Question", "QuestionID": question["Payload"]["QuestionID"]} for question in questions]
    survey_blocks_element["Payload"][-1]["Options"]["RandomizeQuestions"] = "RandomWithOnlyX"
    survey_blocks_element["Payload"][-1]["Options"]["Randomization"]["Advanced"]["TotalRandSubset"] = num_random

def format_survey_blocks(questions, n=25):
    """
    The SurveyBlocks section has to be extended with the set of questions
    """
    return {
      "SurveyID": "SV_5sXmuibskKlpHmJ",
      "Element": "BL",
      "PrimaryAttribute": "Survey Blocks",
      "SecondaryAttribute": None,
      "TertiaryAttribute": None,
      "Payload": [
        {
          "Type": "Default",
          "Description": "Introduction Block",
          "ID": "BL_cvxoPps3HflxlsN",
          "BlockElements": [
            {
              "Type": "Question",
              "QuestionID": "QID1"
            },
            {
              "Type": "Question",
              "QuestionID": "QID2"
            }
          ]
        },
        {
          "Type": "Trash",
          "Description": "Trash / Unused Questions",
          "ID": "BL_0IH9ow1MoCfyMW9"
        },
        {
          "Type": "Standard",
          "SubType": "",
          "Description": "Intruder Experiment",
          "ID": "BL_2soHZqi6foVxie1",
          "BlockElements": [{"Type": "Question", "QuestionID": question["Payload"]["QuestionID"]} for question in questions],
          "Options": {
            "BlockLocking": "false",
            "RandomizeQuestions": "RandomWithOnlyX",
            "Randomization": {
              "Advanced": {
                "QuestionsPerPage": 0,
                "TotalRandSubset": n
              }
            }
          }
        }
      ]
    }