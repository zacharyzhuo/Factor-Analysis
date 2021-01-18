# 安裝虛擬環境
```
python -m venv venv
pip freeze > requirements.txt
python -m pip install -r requirements.txt
```

# For Windows
### install TA-Lib
```
pip3 install C:\Users\IPLAB2\Documents\GitHub\Factor-Analysis\Factor-Analysis\TA-Lib\TA_Lib-0.4.19-cp37-cp37m-win_amd64.whl
```
### virtualenv
```
cd C:\Users\IPLAB2\Documents\GitHub\Factor-Analysis
.\venv\Scripts\activate
cd Factor-Analysis

deactivate
```

# For Mac
### install TA-Lib
```
brew install ta-lib
pip install TA-lib
```
### virtualenv
```
cd /Users/zachary/Documents/GitHub/Factor-Analysis
source ./venv/bin/activate
cd Factor-Analysis

deactivate
```
