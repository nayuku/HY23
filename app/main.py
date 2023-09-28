# main.py
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_home():
    return templates.TemplateResponse("home.html", {"request": {}})


@app.get("/browser", response_class=HTMLResponse)
async def read_browser():
    return templates.TemplateResponse("browser.html", {"request": {}})


@app.get("/about", response_class=HTMLResponse)
async def read_about():
    return templates.TemplateResponse("about.html", {"request": {}})
