import json

import requests


def main():
    a = """
    {'chat_type_id': 1, 'message': {'client_msg_id': '0622477f-ca1b-3df6-a247-50d11b02f1d7', 'content': 'aaa', 'from': {'role': 'user', 'uid': '42
84357278'}, 'msg_id': '1604480525949', 'nickname': '伊*****************0', 'pre_msg_id': '1604454723862', 'titan_msg_id': '1604480526100#527095361#c34d495b', 'to': {'role': 'mall_cs', 'uid': 'sd'}
, 'ts': '1604480525', 'type': 0, 'version': 1}}
    """
    a = eval(a.replace('\n', ''))
    print(type(a))
    res = requests.post('http://localhost:8000/api/model/dialog/', json={'query': json.dumps(a)})
    print(res.json())


if __name__ == '__main__':
    main()
