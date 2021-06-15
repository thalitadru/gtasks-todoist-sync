import requests, uuid, json

def get_labels(token):
    # get existing labels
    labels = requests.get(
        "https://api.todoist.com/rest/v1/labels",
        headers={
            "Authorization": "Bearer %s" % token
        }).json()
    l_names = {l['name']:l['id'] for l in labels}
    return l_names

def find_or_create_labels(tags, l_names, token):
    # create non existing labels (from tags)
    new_tags = filter(lambda tag: tag not in l_names, tags)
    added_tags = {}
    for tag in new_tags:
        r = requests.post(
            "https://api.todoist.com/rest/v1/labels",
            data=json.dumps({
                "name": tag
            }),
            headers={
                "Content-Type": "application/json",
                "X-Request-Id": str(uuid.uuid4()),
                "Authorization": "Bearer %s" % token
            }).json()
        added_tags[tag] = r['id']
    return added_tags

def tags2label_ids(tags, l_names):
    # convert tags to tag_IDs
    return [l_names[tag] for tag in tags]

def get_pid(p_name, token):
    # get pid
    projs = requests.get(
        "https://api.todoist.com/rest/v1/projects",
        headers={
            "Authorization": "Bearer %s" % token
        }).json()
    p = list(filter(lambda p : p['name'] == p_name, projs))
    pid = p[0]['id']
    return pid

def get_sections(pid, token):
    sections = requests.get(
    "https://api.todoist.com/rest/v1/sections?project_id={}".format(pid),
    headers={
        "Authorization": "Bearer %s" % token
    }).json()
    return sections

def new_section(s_name, pid, token):
    s = requests.post(
            "https://api.todoist.com/rest/v1/sections",
            data=json.dumps({
                "project_id": pid,
                "name": s_name
            }),
            headers={
                "Content-Type": "application/json",
                "X-Request-Id": str(uuid.uuid4()),
                "Authorization": "Bearer %s" % token
            }).json()
    return s

def find_or_create_section(s_name, pid, token):
    # create section if needed
    sections = get_sections(pid, token)
    if sections:
        s = list(filter(lambda s : s['name'] == s_name, sections))
        if s:
            return s[0]

    return new_section(s_name, pid, token)

