import json
import re
import requests

def get_list(list_id, access_token):
    req_uri = "https://tasks.googleapis.com/tasks/v1/users/@me/lists/{}".format(list_id)
    headers = {'Authorization': 'Bearer {}'.format(access_token),
            'Accept': 'application/json',
            }
    r = requests.get(req_uri, headers=headers)
    output = r.json()
    output['list_id'] = list_id

def get_list_id(selfLink):
    list_id = re.search(r'lists/(\w+)/', selfLink).groups()[0]
    return list_id

def parse_task(input_data):
    output = {}

    output['due_date'] = input_data['due_date'].split('T')[0]

    project = input_data['list']
    parent = re.search(r"#(\w+)", project)

    if parent:
        parent = parent.groups()[0].capitalize()
        project = re.sub(r"\s*#\w+", "", project)

    output["project"] = project
    output["parent"] = parent
        
    task = input_data['task']
    priority = re.search(r"p([0-9])", task)
    section = re.search(r"/(\w+)", task)
    tags = re.findall(r"@(\w+)", task)

    for pattern in [r"\s*p[0-9]", r"\s*#\w+", r"\s*@\w+", r"\s*/(\w+)"]:
        task = re.sub(pattern, "", task)

    if priority:
        priority = priority.groups()[0]
    else:
        priority = 1
    output["priority"] = priority

    if section:
        section = section.groups()[0].capitalize()
    output["section"] = section

    if tags:
        tags.append("gtasks")
        tags = ", ".join(tags)
    else:
        tags = "gtasks"
    output["tags"] = tags
    output["gtask_id"] = input_data["gtask_id"]
    output["title"] = task