@echo off
git pull
pip install -r requirements.txt
cd cores
cd algo_manager v5
python Manager.py