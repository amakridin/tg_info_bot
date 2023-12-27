python3.10 -m venv /root/py/tg_info_bot/venv
source venv/bin/activate
pip install -r requirements.txt
nohup python3.10 run_tg_info_bot_listener.py &>/log_listener.log &
nohup python3.10 run_tg_info_bot_processing.py &>log_processing.log &