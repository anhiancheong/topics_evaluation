

import argparse
import json
import requests
import time

API_KEY = "PG36cliH5kXi0ARzC2wCxotb3Wo2t9v7A2O6MQDC"

ENDPOINT = "https://az1.qualtrics.com/API/v3"

survey_ids = {
    "SV_50zRZfCRm5wvvxA": '../may_20_results/NYT_Ratings.csv',
    "SV_ezlYrHXuI4oxV8W": '../may_20_results/NYT_Intrusion_1.csv',
    "SV_0Va3pTzbIGiS8tM": '../may_20_results/Wiki_Intrusion_1.csv',
    "SV_80UG9Vuo5KHKbFI": '../may_20_results/Wiki_Ratings.csv',
    "SV_3z2XeepZD1uheui": '../may_20_results/NYT_Intrusion_2.csv',
    "SV_6GuDFnyQX0IhAeq": '../may_20_results/Wiki_Intrusion_2.csv'
}



for survey_id in survey_ids:
    resp = requests.post(
        f"{ENDPOINT}/surveys/{survey_id}/export-responses",
        headers={"X-API-TOKEN": API_KEY},
        json={
            "format": "csv",
            "compress": False,
            "breakoutSets": False
        }
    )
    print(resp.__dict__)
    if resp.status_code < 299:
        progress_id = resp.json()["result"]["progressId"]
    else:
        raise Exception(json.dumps(resp.__dict__))

    # begin polling for the export progress
    file_id = None
    for i in range(0, 6):
        resp = requests.get(
            f"{ENDPOINT}/surveys/{survey_id}/export-responses/{progress_id}",
            headers={"X-API-TOKEN": API_KEY}
        )
        if resp.status_code > 299:
            raise Exception(json.dumps(resp.__dict__))
        resp_json = resp.json()
        if resp_json["result"]["status"] == "inProgress":
            print("Waiting...")
            time.sleep(5)
        if resp_json["result"]["status"] == "complete":
            file_id = resp_json["result"]["fileId"]
            break

    if not file_id:
        print("Exitting.... no file id.")
    
    print("Found file id!")
    resp = requests.get(
        f"{ENDPOINT}/surveys/{survey_id}/export-responses/{file_id}/file",
        headers={"X-API-TOKEN": API_KEY}
    )

    print(resp.status_code)
    writer = open(survey_ids[survey_id], "wb+")
    writer.write(resp.content)
    writer.close()