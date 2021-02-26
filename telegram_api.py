import requests
import json
proxies = None
with open('config') as f:
    token = f.read()
token = token.strip().strip('\n')
url = f"https://api.telegram.org/bot{token}/"

# buttons=[[
#         {"text": "button1", "callback_data": 1, "url": "htps://..."},
#         {"text": "button2", "callback_data": 0, "url": "htps://..."}
#       ]]
def get_updates(offset=None, timeout=30):
    method = 'getUpdates'
    params = {'timeout': timeout, 'offset': offset}
    resp = requests.get(url=url + method, json=params, proxies=proxies, verify=False)
    result_json = resp.json()
    if result_json.get('result') is not None:
        return result_json['result']
    else:
        return []

def get_chats():
    return _send(method='getChats')


def kick_chat_user(chat_id, user_id):
    return _send(chat_id=chat_id, user_id=user_id, method='kickChatMember')


def unban_chat_user(chat_id, user_id):
    return _send(chat_id=chat_id, user_id=user_id, method='restrictChatMember')


# def create_chat(chat_title, userlist):
#     return _send(title=chat_title, users=userlist, method='createChat')


def get_chat_info(chat_id):
    return _send(chat_id=chat_id, method='getChat')


def get_chat_admins(chat_id):
    return _send(chat_id=chat_id, method='getChatAdministrators')


def send_message(chat_id, msg, reply_mid=None):
    return _send(chat_id=chat_id, method='sendMessage', text=msg, reply_to_msg_id=reply_mid)


def send_buttons(chat_id, msg, buttons, reply_mid=None):
    return _send(chat_id=chat_id, method='sendMessage', text=msg, reply_markup=buttons, reply_to_msg_id=reply_mid)


def send_image(chat_id, file_path, msg=None, caption=None, reply_mid=None, buttons=None):
    return _send(chat_id=chat_id, method='sendPhoto', file_type='photo', text=msg, caption=caption, reply_to_msg_id=reply_mid, file_path=file_path, reply_markup=buttons)


def send_document(chat_id, file_path, msg=None, caption=None, reply_mid=None, buttons=None):
    return _send(chat_id=chat_id, method='sendDocument', file_type='document', text=msg, caption=caption, reply_to_msg_id=reply_mid, file_path=file_path, reply_markup=buttons)


def edit_message(chat_id, mid, msg, buttons=None):
    return _send(chat_id=chat_id, method='editMessageText', message_id=mid, text=msg, reply_markup=buttons)


def delete_message(chat_id, mid):
    return _send(chat_id=chat_id, message_id=mid, method='deleteMessage')


def pin_message(chat_id, mid):
    return _send(chat_id=chat_id, message_id=mid, method='pinChatMessage')


# def setDiscussionGroup(channel_id, group_id):
#     return _send(broadcast=channel_id, group=group_id, method='setDiscussionGroup')


def _send(method, **params):
    jsn = {}
    files = None
    for k, v in params.items():
        if v:
            if k == 'reply_markup':
                jsn[k] = json.dumps({"inline_keyboard": v})
            elif k == 'file_path':
                if v.find('http') == 0:
                    jsn["photo"] = v
                else:
                    with open(v, "rb") as f:
                        files = {params['file_type']: f}
            else:
                jsn[k] = v
    return requests.post(url=url + method, data=jsn, files=files, proxies=proxies, verify=False).json()

def send_keyboard_button(chat_id, msg, button_type, button_text):
    button_types = {"contact": "request_contact", "location": "request_location", "poll": "request_poll	"}
    jsn = {"chat_id": chat_id,
           "text": msg,
           "reply_markup": {
                "keyboard": [[{"text": button_text, button_types[button_type]: True}]],
                "one_time_keyboard": True,
                "resize_keyboard": True
            }
    }
    method = 'sendMessage'
    resp = requests.post(url=url + method, json=jsn, proxies=proxies, verify=False)
    print(resp.text)
    resp = resp.json()
    if resp.get('error_code') is not None:
        return resp['description']
    return None


if __name__ == "__main__":
    # pass
    print(send_image(chat_id=314602198, file_path='https://instagram.fnjf3-2.fna.fbcdn.net/v/t51.2885-19/s320x320/145549448_206462371214924_6878609620421372420_n.jpg?_nc_ht=instagram.fnjf3-2.fna.fbcdn.net&_nc_ohc=c5PMq819OvYAX_iFuzD&tp=1&oh=f153788538cf3a872edbf736af12404a&oe=60606605'))