import requests

def get_token(g):
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

    return g['auth_token']['access_token']