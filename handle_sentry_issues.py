from utility.util_local import write_output_csv, read_input_csv

import os
import json
from datetime import datetime
from pprint import pprint

import requests


def make_sentry_GET_query(endpoint):
    output_lod = []
    resp = requests.get(
        "https://sentry.io/api/0/" + endpoint,
        headers={"Authorization": "Bearer " + os.environ["SENTRY_API_KEY"]}
    )
    if resp.status_code == 200:
        output_lod += resp.json()

    while resp.links['next']['results'] == 'true':
        new_endpoint = resp.links['next']['url']
        resp = requests.get(new_endpoint, headers={"Authorization": "Bearer " + os.environ["SENTRY_API_KEY"]})
        output_lod += resp.json()
        print("paginating - 100 issues per page")

    return output_lod, resp.status_code


def make_sentry_PUT_query(endpoint, status_to_change_to):
    resp = requests.put(
        "https://sentry.io/api/0/" + endpoint,
        headers={
            "Authorization": "Bearer " + os.environ["SENTRY_API_KEY"],
            "Content-Type": "application/json"
        },
        data=json.dumps({"status": status_to_change_to})
    )
    print(f"Status code: {resp.status_code} - Issue: {endpoint.replace('issues/', '').rstrip('/')}")
    return resp.status_code


#####


def export_all_issues_in_project(org_name, project_name):
    output_lod, last_status_code = make_sentry_GET_query(f"projects/{org_name}/{project_name}/issues/")
    print(f"Final status_code was {last_status_code}")

    today_utc = datetime.utcnow().strftime('%Y-%m-%d')
    write_output_csv(f"{today_utc}_Sentry_Issues_{project_name}.csv", output_lod)


# Dpcs: https://docs.sentry.io/api/events/update-an-issue/
# THey have a bulk endpoint which I did not implement: https://docs.sentry.io/api/events/bulk-mutate-a-list-of-issues/
def update_issues_with_string_in_title(filename, title_substr, status_to_change_to):
    issue_id_lod = read_input_csv(filename, columns=["title", "status", "id"])

    for x in issue_id_lod:
        if title_substr in x.get("title") and x.get("status") == "unresolved":
            make_sentry_PUT_query(f"issues/{x['id']}/", status_to_change_to) # trailing slash required


################################################

"""
if __name__ == "__main__":

    update_issues_with_string_in_title(filename, title_substr, status_to_change_to)

    export_all_issues_in_project(org_name, project_name)
"""
