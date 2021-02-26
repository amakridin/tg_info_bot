from telegram_api import *
import json_params as json_params

jsn = {}
new_offset = None
questions = {
    "1": {"msg": "2 * 2 = ?",
          "buttons": [
            {"text": "2", "callback_data": 0},
            {"text": "3", "callback_data": 0},
            {"text": "4", "callback_data": 1},
            {"text": "5", "callback_data": 0}]
        },
    "2": {"msg": "1 > 2",
          "buttons": [
            {"text": "Yes", "callback_data": 0},
            {"text": "No", "callback_data": 1}
        ]},
    "3": {"msg": "10 / 2 = ?",
          "buttons": [
            {"text": "2", "callback_data": 0},
            {"text": "3", "callback_data": 0},
            {"text": "4", "callback_data": 0},
            {"text": "5", "callback_data": 1}
        ]},
    "4": {"msg": "What is passed in digit row?\n 1 3 5 ? 9",
          "buttons": [
            {"text": "0", "callback_data": 0},
            {"text": "4", "callback_data": 0},
            {"text": "7", "callback_data": 1},
            {"text": "11", "callback_data": 0}
          ]},
    "5": {"msg": "True > False?",
          "buttons": [
            {"text": "Yes", "callback_data": 1},
            {"text": "No", "callback_data": 0}
          ]}
    }
def test(chat_id):
    nn = user_params[str(chat_id)]['question_num']
    if nn == 5:
        msg = f"Your score is: {user_params[str(chat_id)]['right_answers']}/{nn}"
        send_keyboard_button(chat_id=chat_id, msg=msg, button_type="location",
                             button_text="I'm here")
        nn = 999
    elif nn < 5:
        msg = questions[str(nn+1)]["msg"]
        buttons = [questions[str(nn+1)]["buttons"]]
        send_buttons(chat_id=chat_id, msg=msg, buttons=buttons)
if __name__ == "__main__":
    user_params = {}
    while True:
        for row in get_updates(offset=new_offset):
            jsn = json_params.get_params(row)
            if jsn['update_type'] == 'callback_query':
                # button click event
                if user_params.get(str(jsn['chat_id'])) is not None:
                    user_params[str(jsn['chat_id'])]['question_num'] = int(user_params[str(jsn['chat_id'])]['question_num']) + 1
                    user_params[str(jsn['chat_id'])]['right_answers'] = int(user_params[str(jsn['chat_id'])]['right_answers']) + int(jsn['text'])
                    test(jsn['chat_id'])
            elif jsn.get('contact') is not None:
                phone = jsn['contact']['phone']
                first_name = jsn['contact']['first_name']
                last_name = jsn['contact']['last_name']
                user_id = jsn['contact']['user_id']
                if user_params.get(str(jsn['chat_id'])) is None:
                    user_params[str(jsn['chat_id'])] = {"phone": None, "question_num": 0, "right_answers": 0}
                user_params[str(jsn['chat_id'])]["phone"] = phone
                test(jsn['chat_id'])
            elif jsn.get('location') is not None:
                latitude = jsn['location']['latitude']
                longitude = jsn['location']['longitude']
            else:
                chat_text = jsn['text']
                chat_id = jsn['chat_id']
                print(jsn)
                if str(chat_text).lower().replace(' ','') == '/start':
                    user_params[str(jsn['chat_id'])] = {"phone": None, "question_num": 0, "right_answers": 0}
                    res = send_keyboard_button(chat_id=jsn['chat_id'],
                                         msg="print your phone number",
                                         button_type="contact",
                                         button_text="Send my phone")
                    if res is not None:
                        send_message(chat_id=jsn['chat_id'], msg=res)
            new_offset = int(jsn['update_id']) + 1
