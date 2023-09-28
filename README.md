# HY23

TODO

- virtual env to isolate project dependencies (from main folder)
```
python -m venv venv
venv\Scripts\activate.bat
```
- install dependencies
```
pip install -r requirements.txt
```
- run app (from app folder)
```
uvicorn main:app --reload
http://127.0.0.1:8000
```

- add new dependencies
```
pip freeze > requirements.txt
```
