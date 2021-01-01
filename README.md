// 虛擬環境

.\Factor-Analysis\venv\Scripts\activate
deactivate

python -m venv venv
pip freeze > requirements.txt
python -m pip install -r requirements.txt
