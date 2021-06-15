import json
store = StoreClient(input_data['secret'])
g = store.get('google')
# test if token is still valid
req_uri = "https://tasks.googleapis.com/tasks/v1/users/@me/lists"
headers = {'Authorization': 'Bearer {}'.format(g['auth_token']['access_token']),
           'Accept': 'application/json',
          }
r = requests.get(req_uri, headers=headers)
# if not, refresh token
if r.status_code == 401:
    data = {'refresh_token': g['auth_token']['refresh_token'],
            'client_id': g['web_client']['client_id'],
            'client_secret': g['web_client']['client_secret'],
            'grant_type': 'refresh_token'}

    r = requests.post('https://oauth2.googleapis.com/token', data=data)
    credentials = r.json()
    g['auth_token'].update(credentials)
    store.set('google', g)
return

import re
list_id = re.search(r'lists/(\w+)/', input_data['selfLink']).groups()[0]

req_uri = "https://tasks.googleapis.com/tasks/v1/users/@me/lists/{}".format(list_id)
headers = {'Authorization': 'Bearer {}'.format(input_data['access_token']),
           'Accept': 'application/json',
          }
r = requests.get(req_uri, headers=headers)
output = r.json()
output['list_id'] = list_id


import re

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

import re

task = input_data['task']
priority = re.search(r"p([0-9])", task)
project = re.search(r"#(\w+)", task)
tags = re.findall(r"@(\w+)", task)

for pattern in [r"p[0-9]", r"#\w+", r"@\w+"]:
    task = re.sub(pattern, "", task)

output = {}
if priority:
    priority = priority.group()
else:
    priority = 1
output["priority"] = priority
if project:
    project = project.group()
else:
    project = "Inbox"
output["project"] = project.lstrip("#").capitalize()
if tags:
    tags = ", ".join(tags)
output["tags"] = tags
output["gtask_id"] = input_data["id"]
output["title"] = task
output = [output]

import requests, uuid, json
token = '44c93dd9f6cf17968abfeca0cbec6e3d78095fe2'
output = {}.update(input_data)
for k, v in output.items():
    if v is 'missing sample data':
        output[k] = None

# get existing labels
labels = requests.get(
    "https://api.todoist.com/rest/v1/labels", 
    headers={
        "Authorization": "Bearer %s" % token
    }).json()
l_names = {l['name']:l['id'] for l in labels}
# create non existing labels (from tags)
tags = list(input_data['tags'])
new_tags = filter(lambda tag: tag not in l_names, tags)
for tag in new_tags:
    requests.post(
        "https://api.todoist.com/rest/v1/labels",
        data=json.dumps({
            "name": tag
        }),
        headers={
            "Content-Type": "application/json",
            "X-Request-Id": str(uuid.uuid4()),
            "Authorization": "Bearer %s" % token
        }).json()
# refresh list of existing labels
labels = requests.get(
    "https://api.todoist.com/rest/v1/labels", 
    headers={
        "Authorization": "Bearer %s" % token
    }).json()
l_names = {l['name']:l['id'] for l in labels}
# convert tags to tag_IDs
output['labels_ids'] = [l_names[tag] for tag in tags]

# get pid
p_name = input_data['project']
projs = requests.get(
    "https://api.todoist.com/rest/v1/projects", 
    headers={
        "Authorization": "Bearer %s" % token
    }).json()
p = list(filter(lambda p : p['name'] == p_name, projs))
pid = p[0]['id']
output['project'] = pid

# create section if needed
s_name = input_data['section']
if not s_name.startswith('missing') :
    create_section = True
    sections = requests.get(
        "https://api.todoist.com/rest/v1/sections?project_id={}".format(pid), 
        headers={
            "Authorization": "Bearer %s" % token
        }).json()
    if sections:
        s = list(filter(lambda s : s['name'] == s_name, sections))
        if s:
            sid = s[0]['id']
            output['section'] = sid
            create_section = False
        
    if create_section:
        import uuid, json
        s = requests.post(
            "https://api.todoist.com/rest/v1/sections",
            data=json.dumps({
                "project_id": pid,
                "name": s_name
            }),
            headers={
                "Content-Type": "application/json",
                "X-Request-Id": str(uuid.uuid4()),
                "Authorization": "Bearer %s" % your_token
            }).json()
        sid = s[0]['id']
        output['section'] = sid
