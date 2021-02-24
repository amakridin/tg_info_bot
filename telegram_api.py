import requests
import json
proxies = None
with open('config') as f:
    token = f.read()
url = f"https://api.telegram.org/bot{token}/"

# buttons=[[
#         {"text": "button1", "callback_data": 1, "url": "htps://..."},
#         {"text": "button2", "callback_data": 0, "url": "htps://..."}
#       ]]
def get_updates(offset=None, timeout=30):
    method = 'getUpdates'
    params = {'timeout': timeout, 'offset': offset}
    resp = requests.get(url=url + method, json=params, proxies=proxies)
    result_json = resp.json()['result']
    return result_json

def get_chats():
    return _send(method='getChats')

# def add_chat_user(chat_id, user_id, fwd_limit=50):
#     return _send(chat_id=chat_id, user_id=user_id, fwd_limit=fwd_limit, method='addChatMember')

def kick_chat_user(chat_id, user_id):
    return _send(chat_id=chat_id, user_id=user_id, method='kickChatMember')

def unban_chat_user(chat_id, user_id):
    return _send(chat_id=chat_id, user_id=user_id, method='restrictChatMember')

# def create_chat(chat_title, userlist):
#     return _send(chat_title=chat_title, userlist=userlist, method='createChat')

def get_chat_info(chat_id):
    return _send(chat_id=chat_id, method='getChat')

def get_chat_admins(chat_id):
    return _send(chat_id=chat_id, method='getChatAdministrators')

def send_message(chat_id, msg, reply_mid=0):
    return _send(chat_id=chat_id, method='sendMessage', msg=msg, reply_mid=reply_mid)

def send_buttons(chat_id, msg, buttons, reply_mid=0):
    return _send(chat_id=chat_id, method='sendMessage', msg=msg, buttons=buttons, reply_mid=reply_mid)

def send_image(chat_id, file_path, msg='', caption='', reply_mid=0, buttons=[]):
    return _send(chat_id=chat_id, method='sendPhoto', file_type='photo', msg=msg, caption=caption, reply_mid=reply_mid, file_path=file_path, buttons=buttons)

def send_document(chat_id, file_path, msg='', caption='', reply_mid=0, buttons=[]):
    return _send(chat_id=chat_id, method='sendDocument', file_type='document', msg=msg, caption=caption, reply_mid=reply_mid, file_path=file_path, buttons=buttons)

def edit_message(chat_id, mid, msg, buttons=[]):
    return _send(chat_id=chat_id, method='editMessageText', mid=mid, msg=msg, buttons=buttons)

def delete_message(chat_id, mid):
    return _send(chat_id=chat_id, mid=mid, method='deleteMessage')

def pin_message(chat_id, mid):
    return _send(chat_id=chat_id, mid=mid, method='pinChatMessage')
# def get_chat_member

# def setDiscussionGroup(channel_id, group_id):
#     return _send(channel_id=, group_id=mid, method='setDiscussionGroup')


def _send(method, chat_id=0, mid=0, msg='', caption='', reply_mid=0, userlist=[], buttons=[], file_path='', file_type='', user_id=0, fwd_limit=0, chat_title='', channel_id=0, group_id=0):
    jsn = {}
    if channel_id != 0: jsn['broadcast'] = channel_id
    if group_id != 0: jsn['group'] = group_id
    if chat_id != 0: jsn['chat_id'] = chat_id
    if mid > 0: jsn['message_id'] = mid
    if user_id != 0: jsn['user_id'] = user_id
    if fwd_limit > 0: jsn['fwd_limit'] = fwd_limit
    if msg != '': jsn['text'] = msg
    if chat_title != '': jsn['title'] = chat_title
    if caption != '': jsn['caption'] = caption
    if reply_mid > 0: jsn["reply_to_msg_id"] = reply_mid
    if buttons != []: jsn["reply_markup"] = json.dumps({"inline_keyboard": buttons})
    if userlist != []: jsn["users"] = userlist
    if file_path != '' and file_path.find('http') == 0:
        jsn["photo"] = file_path
        return requests.post(url=url + method, json=jsn, proxies=proxies).json()
    elif file_path != '' and file_path.find('http') < 0:
        with open(file_path, "rb") as f:
            files = {file_type: f}
            return requests.post(url=url + method, data=jsn, files=files, proxies=proxies).json()
    else:
        return requests.post(url=url + method, json=jsn, proxies=proxies).json()

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
    resp = requests.post(url=url + method, json=jsn, proxies=proxies)
    print(resp.text)
    resp = resp.json()
    if resp.get('error_code') is not None:
        return resp['description']
    return None

if __name__ == "__main__":
    # print(send_image(chat_id=314602198, file_path='moon.jpg', caption="moon", reply_mid=655, buttons=[[{"text": "Yes", "callback_data": 1}, {"text": "No", "callback_data": 0}]]))
    # print(send_document(chat_id=314602198, file_path='moon.jpg', caption="moon", reply_mid=655, buttons=[[{"text": "Yes", "callback_data": 1}, {"text": "No", "callback_data": 0}]]))
    # print(edit_message(chat_id=314602198, mid=655, msg='hello бля'))
    # print(send_buttons(chat_id=314602198, msg='hello', buttons=[[{"text": "Yes", "callback_data": 1}, {"text": "No", "callback_data": 0}]]))
    # print(delete_message(chat_id=314602198, mid=700))
    # print(get_chat_info(-334198960))
    # print(get_chat_admins(-334198960))
    # print(get_chats())
    # print(send_message(chat_id=-334198960, msg='hello'))

    # print(create_chat('test', [970402676, 747711712]))
    # print(kick_chat_user(chat_id=-334198960, user_id=747711712))
    # print(unban_chat_user(chat_id=-334198960, user_id=747711712))
    # print(pin_message(chat_id=-334198960, mid=721))
    print(send_image(chat_id=314602198, file_path='https://instagram.fnjf3-2.fna.fbcdn.net/v/t51.2885-19/s320x320/145549448_206462371214924_6878609620421372420_n.jpg?_nc_ht=instagram.fnjf3-2.fna.fbcdn.net&_nc_ohc=c5PMq819OvYAX_iFuzD&tp=1&oh=f153788538cf3a872edbf736af12404a&oe=60606605'))