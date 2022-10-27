python3.10 -m venv /root/py/common_tg_bot/venv
source venv/bin/activate
pip install -r requirements.txt
nohup python3.10 run_event_listener.py &>/log_listener.log &
nohup python3.10 run_event_processing.py &>log_processing.log &