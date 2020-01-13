import requests
import json

def login():
    headers = {'Content-Type': 'application/json',}
    data = '{ "userName": "master", "password": "secret" }'
    response = requests.post('http://163.172.168.41:8888/services/auth/login', headers=headers, data=data)
    cookies = response.cookies
    return cookies

def uploadfile(nonce,dataJSON):

        cookies = login()
        dataJSON = json.dumps(dataJSON)
        dataJSON = dataJSON.encode('utf-8')
        files = {'file': (dataJSON),}
        requests.post('http://163.172.168.41:8888/services/files/upload/newdir/'+ nonce + '.json', cookies=cookies, files=files)