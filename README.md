## 虛擬環境
```
cd C:\Users\IPLAB2\Documents\GitHub\Factor-Analysis
.\venv\Scripts\activate
cd Factor-Analysis

source ./venv/bin/activate
deactivate
```
```
python -m venv venv
pip freeze > requirements.txt
python -m pip install -r requirements.txt
```

## For Windows
```
pip3 install C:\Users\IPLAB2\Documents\GitHub\Factor-Analysis\Factor-Analysis\TA-Lib\TA_Lib-0.4.19-cp37-cp37m-win_amd64.whl
```

## For Mac
```
brew install ta-lib
pip install TA-lib
```

## 執行test中的程式
```
python3 test.test_mom
python3 test.test_ranking
```
