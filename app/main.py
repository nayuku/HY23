import os
import openai
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# your openai key
dir_path = os.path.dirname(os.path.realpath(__file__))
with open(f"{dir_path}/apikey.txt") as f:
  openai.api_key = f.read().strip()

@app.get("/", response_class=HTMLResponse)
async def read_calc():
  return templates.TemplateResponse("home.html", {"request": {}})


@app.get("/browser", response_class=HTMLResponse)
async def read_browser():
  return templates.TemplateResponse("browser.html", {"request": {}})


@app.get("/about", response_class=HTMLResponse)
async def read_about():
  return templates.TemplateResponse("about.html", {"request": {}})

# openai integration
@app.post("/recommend")
async def recommend(request: Request, interest: str = Form(...)):
  r = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  #model="gpt-4",
  messages=[
    {"role": "system", "content": """Jesteś znawcą polskich uczelni wyższych. Wiesz jakie są
    kierunki, wymagania, progi punktowe na każdej uczelni. Chcesz dobrze doradzić młodemu
    człowiekowi jaki kierunek i uczelnię powinien wybrać na podstawie serii pytań, które
    użytkownik Ci zada."""},
    {"role": "user", "content": f"""Użytkownik jest zainteresowany {interest}.
     Na podstawie tego zainteresowania zaproponuj 8 najlepiej dopasowanych pod jego profil
     kierunkó wraz z uczelnią i miastem w formacie:
     | Kierunek | Uczelnia | Miasto |"""}
    ]
  )
  text = r["choices"][0]["message"]["content"]
  print(text)
  return
