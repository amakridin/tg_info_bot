# from get_db_data import ins_data
def get_params(json_in):
    ret = {}
    try:
        data = json_in
        ret['update_id'] = data['update_id']
        ret['bot_id'] = 0
        ret['user_id'] = 0
        ret['user_name'] = ''
        ret['callback_payload'] = ''
        ret['chat_id'] = 0
        ret['chat_type'] = ''
        ret['admin_deleted'] = 0
        ret['admin_invited'] = 0
        ret['sender_id'] = 0
        ret['sender_name'] = ''
        ret['mid'] = ''
        ret['text'] = ''
        ret['message_type'] = ''
        ret['reply_mid'] = 0
        ret['reply_text'] = ''
        ret['reply_sender_id'] = 0
        ret['reply_sender_name'] = ''
        ret['timestamp'] = 0
        ret['update_type'] = ''
        ret['title'] = ''
        ret['link'] = ''
        ret['attachment_userid'] = 0
        if data.get('callback_query') is not None:
            ret['update_type'] = 'callback_query'
            ret['mid'] = data['callback_query']['message']['message_id']
            ret['chat_id'] = data['callback_query']['message']['chat']['id']
            ret['text'] = data['callback_query']['data']
            ret['user_id'] = data['callback_query']['from']['id']
            ret['user_name'] = data['callback_query']['from']['username']
            ret['timestamp'] = data['callback_query']['message']['date']
            ret['chat_type'] = data['callback_query']['message']['chat']['type']
        # elif (update_type in('user_removed', 'user_added', 'bot_added', 'bot_removed')):
        #     chat_id = data['chat_id']
        #     chat_type = 'chat'
        #     timestamp = data['timestamp']
        #     user_id = data['user']['user_id']
        #     user_name = data['user']['name']
        #     # admin_deleted = data['updates'][0]['admin_id']  # Кто удалил пользователя
        #     # admin_invited = data['updates'][0]['inviter_id']  # Кто добавил пользователя
        #     qr = "insert into crm.bot_chats(chat_id, user_id, update_type) values("+str(chat_id)+","+str(user_id)+",'"+update_type+"')"
        #     ins_data(qr)
        elif data.get('edited_message') is not None:
            ret['update_type'] = 'edited_message'
            ret['user_id'] = data['edited_message']['from']['id']
            ret['user_name'] = data['edited_message']['from']['username']
            ret['chat_id'] = data['edited_message']['chat']['id']
            ret['chat_type'] = data['edited_message']['chat']['type']  # dialog, chat
            ret['timestamp'] = data['edited_message']['edit_date']
            ret['mid'] = data['edited_message']['message_id']
            ret['text'] = data['edited_message']['text']
        elif data.get('message') is not None:
            ret['update_type'] = 'message'
            ret['user_id'] = data['message']['from']['id']
            ret['user_name'] = data['message']['from']['username']
            ret['chat_id'] = data['message']['chat']['id']
            ret['chat_type'] = data['message']['chat']['type']  # private, group
            ret['timestamp'] = data['message']['date']
            ret['mid'] = data['message']['message_id']
            ret['text'] = data['message'].get('text')
            if data['message'].get('contact') is not None:
                contact = {}
                contact['phone'] = data['message']['contact'].get('phone_number')
                contact['first_name'] = data['message']['contact'].get('first_name')
                contact['last_name'] = data['message']['contact'].get('last_name')
                contact['username'] = data['message']['contact'].get('username')
                contact['user_id'] = data['message']['contact'].get('user_id')
                ret['contact'] = contact
            if data['message'].get('location') is not None:
                location = {}
                location['latitude'] = data['message']['location']['latitude']
                location['longitude'] = data['message']['location']['longitude']
                ret['location'] = location
            if data['message'].get('left_chat_member') is not None:
                user_removed = {}
                user_removed['phone'] = data['message']['left_chat_member'].get('phone_number')
                user_removed['first_name'] = data['message']['left_chat_member'].get('first_name')
                user_removed['last_name'] = data['message']['left_chat_member'].get('last_name')
                user_removed['username'] = data['message']['left_chat_member'].get('username')
                user_removed['user_id'] = data['message']['left_chat_member'].get('id')
                user_removed['is_bot'] = data['message']['left_chat_member'].get('is_bot')
                ret['user_removed'] = user_removed
            if data['message'].get('new_chat_member') is not None:
                user_added = {}
                user_added['phone'] = data['message']['new_chat_member'].get('phone_number')
                user_added['first_name'] = data['message']['new_chat_member'].get('first_name')
                user_added['last_name'] = data['message']['new_chat_member'].get('last_name')
                user_added['username'] = data['message']['new_chat_member'].get('username')
                user_added['user_id'] = data['message']['new_chat_member'].get('id')
                user_added['is_bot'] = data['message']['new_chat_member'].get('is_bot')
                ret['user_added'] = user_added

        # elif (update_type == 'message_removed'):
        #     mid = data['message_id']
        # elif update_type == 'message_chat_created':
        #     chat_id = data['chat']['chat_id']
        #     title = data['chat']['title']
        #     link = data['chat']['link']
        #     timestamp = data['timestamp']
        #     ins_data(query=f"insert into crm.bot_chat_list(recordid,chat_id,typ,chat_name,link,issue) values(crm.bot_seq.nextval, {chat_id}, 3, '{title}', '{link}', '{title[0:title.find(':')]}')")

    except Exception as ex:
        print('error', ex.__str__())
    finally:
        return ret