
"""

Quick and dirty CLI for generating some MTurk tasks for topics

Example:
python generate_mturk_task.py --type parse_results --aws_key <AWS_KEY> --aws_secret <AWS_SECRET> --hit_id


"""


import argparse
import boto3
import json
import random
import xmltodict


def create_mturk_client(
    aws_access_key_id,
    aws_secret_access_key,
    endpoint_url='https://mturk-requester-sandbox.us-east-1.amazonaws.com',
    region_name='us-east-1'
    ):
    
    client = boto3.client(
        'mturk',
        endpoint_url=endpoint_url,
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    return client

def test_mturk_client(client):
    # This will return $10,000.00 in the MTurk Developer Sandbox
    print(client.get_account_balance()['AvailableBalance'])

def create_ratings_task(topic_id, terms):
    ratings_html = f"""
    <div id="ratings_question_{topic_id}">
    <h3 id="instructions_header"> Please rate how related the following terms are to each other: </h3>
    <h4 id="terms"> {",".join(terms)} </h4>
    <input type="radio" id="not_very_related" name="ratings_{topic_id}" value="1">
    <label for="not_very_related">Not very related</label><br>
    <input type="radio" id="somewhat_related" name="ratings_{topic_id}" value="2">
    <label for="somewhat_related">Somewhat related</label><br>
    <input type="radio" id="very_related" name="ratings_{topic_id}" value="3">
    <label for="very_related">Very related</label>
    </div>
    """
    return ratings_html

def create_intrusion_task(topic_id, terms, intruder_topic_id, intruder_term):
    
    radio_button_strings = [
        f"""
            <input type="radio" id="{term}" name="intrusion_{topic_id}_{intruder_topic_id}" value="{term}_{idx}">
            <label for="{term}">{term}</label>
        """
        for idx, term in enumerate(terms)
    ]
    # add the intruder
    radio_button_strings.append(
        f"""
            <input type="radio" id="{intruder_term}" name="intrusion_{topic_id}_{intruder_topic_id}" value="{intruder_term}_-1">
            <label for="{intruder_term}">{intruder_term}</label>
        """
    )
    random.shuffle(radio_button_strings)
    intrusion_html = f"""
    <div id="intrusion_question_{topic_id}_{intruder_topic_id}">
    <h3 id="instructions_header"> Please select the term that is least related to all other terms: </h3>
    {"".join(radio_button for radio_button in radio_button_strings)}
    </div>
    """
    return intrusion_html

def create_intrusion_assignment(intrusion_setup):
    intrusion_strings = "".join([
        create_intrusion_task(
            setup["topic_id"],
            setup["topic_terms"],
            setup["intruder_id"],
            setup["intruder_term"]
        ) for setup in intrusion_setup
    ])
    
    intrusion_assignment = f"""
        <HTMLQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2011-11-11/HTMLQuestion.xsd">
        <HTMLContent><![CDATA[
        <!-- YOUR HTML BEGINS -->
        <!DOCTYPE html>
        <html>
        <head>
        <meta http-equiv='Content-Type' content='text/html; charset=UTF-8'/>
        <script type='text/javascript' src='https://s3.amazonaws.com/mturk-public/externalHIT_v1.js'></script>
        </head>
        <body>
        <form name='mturk_form' method='post' id='mturk_form' action='https://www.mturk.com/mturk/externalSubmit'>
        <input type='hidden' value='' name='assignmentId' id='assignmentId'/>
        {intrusion_strings}
        <p><input type='submit' id='submitButton' value='Submit' /></p></form>
        <script language='Javascript'>turkSetAssignmentID();</script>
        </body></html>
        <!-- YOUR HTML ENDS -->
        ]]>
        </HTMLContent>
        <FrameHeight>600</FrameHeight>
        </HTMLQuestion>
    """
    return intrusion_assignment

def create_ratings_assignment(ratings_setup):
    ratings_strings = "".join(
        [create_ratings_task(setup["topic_id"], setup["terms"]) for setup in ratings_setup]
    )
    ratings_form = f"""
        <HTMLQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2011-11-11/HTMLQuestion.xsd">
        <HTMLContent><![CDATA[
        <!-- YOUR HTML BEGINS -->
        <!DOCTYPE html>
        <html>
        <head>
        <meta http-equiv='Content-Type' content='text/html; charset=UTF-8'/>
        <script type='text/javascript' src='https://s3.amazonaws.com/mturk-public/externalHIT_v1.js'></script>
        </head>
        <body>
        <form name='mturk_form' method='post' id='mturk_form' action='https://www.mturk.com/mturk/externalSubmit'>
        <input type='hidden' value='' name='assignmentId' id='assignmentId'/>
        {ratings_strings}
        <p><input type='submit' id='submitButton' value='Submit' /></p></form>
        <script language='Javascript'>turkSetAssignmentID();</script>
        </body></html>
        <!-- YOUR HTML ENDS -->
        ]]>
        </HTMLContent>
        <FrameHeight>600</FrameHeight>
        </HTMLQuestion>
    """
    return ratings_form

def create_intrusion_hit(client, intrusion_setup):
    new_hit = client.create_hit(
        Title = 'Topic Intrusion',
        Description = 'Please identify which term is the least related to the other terms',
        Keywords = 'text, quick, labeling',
        Reward = '0.15',
        MaxAssignments = 10,
        LifetimeInSeconds = 172800,
        AssignmentDurationInSeconds = 600,
        AutoApprovalDelayInSeconds = 14400,
        Question = create_intrusion_assignment(intrusion_setup),
    )
    print("A new HIT has been created. You can preview it here:")
    print("https://workersandbox.mturk.com/mturk/preview?groupId=" + new_hit['HIT']['HITGroupId'])
    print("HITID = " + new_hit['HIT']['HITId'] + " (Use to Get Results)")
    hit_id = new_hit['HIT']['HITId']
    return hit_id

def create_ratings_hit(client, ratings_setup):
    new_hit = client.create_hit(
        Title = 'Topic Ratings',
        Description = 'Please describe how related the following sets of words are to each other',
        Keywords = 'text, quick, labeling',
        Reward = '0.15',
        MaxAssignments = 10,
        LifetimeInSeconds = 172800,
        AssignmentDurationInSeconds = 600,
        AutoApprovalDelayInSeconds = 14400,
        Question = create_ratings_assignment(ratings_setup),
    )
    print("A new HIT has been created. You can preview it here:")
    print("https://workersandbox.mturk.com/mturk/preview?groupId=" + new_hit['HIT']['HITGroupId'])
    print("HITID = " + new_hit['HIT']['HITId'] + " (Use to Get Results)")
    hit_id = new_hit['HIT']['HITId']
    return hit_id

def parse_results(client, hit_id):
    worker_results = client.list_assignments_for_hit(HITId=hit_id, AssignmentStatuses=['Submitted'])
    scores = []
    for assignment in worker_results["Assignments"]:
        assignment_dict = xmltodict.parse(assignment["Answer"])
        for answer in assignment_dict["QuestionFormAnswers"]["Answer"]:
            print(answer["QuestionIdentifier"], answer["FreeText"])
            scores.append({"question_id":answer["QuestionIdentifier"], "answer":answer["FreeText"]})
    return scores


if __name__ == "__main__":

    # Parse out the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--prod", help="Use production MTurk endpoint", action="store_true")
    parser.add_argument("--type", '-t', type=str, help="Select either 'ratings', 'intrusion' or 'parse_results'", required=True)
    parser.add_argument("--aws_key", help="AWS Key", type=str, required=True)
    parser.add_argument("--aws_secret", help="AWS Secret", type=str, required=True)
    parser.add_argument("--topics_file", help="Filename of topics to use for generating task", type=str)
    parser.add_argument("--hit_id", help="HIT ID for parsing results", type=str)

    args = parser.parse_args()

    endpoint = "https://mturk-requester.us-east-1.amazonaws.com" if args.prod \
        else "https://mturk-requester-sandbox.us-east-1.amazonaws.com"

    client = create_mturk_client(
        aws_access_key_id=args.aws_key,
        aws_secret_access_key=args.aws_secret,
        endpoint_url=endpoint
    )
    
    test_mturk_client(client)

    # TODO - Add actual topics file parsing
    ratings_setup = [
        {"topic_id": 0, "terms": ['dog','cat','rabbit','snake','fish']},
        {"topic_id": 1, "terms": ['taco','burrito','enchilada','fajitas','salsa']},
        {"topic_id": 2, "terms": ['andrew','riley','claire','annelise','eric']}
    ]
    
    intrusion_setup = [
        {
            "topic_id": 0,
            "topic_terms": ['dog','cat','rabbit','snake','fish'],
            "intruder_id": 10,
            "intruder_term": "apple"
        },
        {
            "topic_id": 1,
            "topic_terms": ['taco','burrito','enchilada','fajitas','salsa'],
            "intruder_id": 20,
            "intruder_term": "mouse"
        },
        {
            "topic_id": 2,
            "topic_terms": ['andrew','riley','claire','annelise','eric'],
            "intruder_id": 30,
            "intruder_term": "vlad"
        }
    ]

    if args.type == "ratings":
        hit_id = create_ratings_hit(client, ratings_setup)
    elif args.type == "intrusion":
        hit_id = create_ratings_hit(client, intrusion_setup)
    elif args.type == "parse_results":
        parse_results(client, args.hit_id)
    else:
        raise Exception(f"Invalid specified task type: {args.type}")
