
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

def update_survey_blocks_element(survey_blocks_element, questions):
    survey_blocks_element["Payload"][-1]["BlockElements"] = [
        {"Type": "Question", "QuestionID": question["Payload"]["QuestionID"]} for question in questions]

def format_survey_blocks(questions):
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
            "RandomizeQuestions": "RandomWithXPerPage",
            "Randomization": {
              "Advanced": {
                "QuestionsPerPage": 0
              }
            }
          }
        }
      ]
    }