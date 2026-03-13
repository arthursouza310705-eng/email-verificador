from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

import pandas as pd
import dns.resolver
from email_validator import validate_email, EmailNotValidError

app = FastAPI()

templates = Jinja2Templates(directory="templates")


# página inicial
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# verificação de email
def check_email(email):

    try:
        validate_email(email)
    except EmailNotValidError:
        return "inativo"

    domain = email.split("@")[1]

    try:
        dns.resolver.resolve(domain, 'MX')
        return "ativo"
    except:
        return "inativo"


# endpoint para verificar CSV
@app.post("/verificar")
async def verificar(file: UploadFile = File(...)):

    df = pd.read_csv(file.file)

    resultados = []

    for email in df["email"]:

        status = check_email(email)

        resultados.append({
            "email": email,
            "status": status
        })

    resultado_df = pd.DataFrame(resultados)

    output_file = "resultado_emails.csv"

    resultado_df.to_csv(output_file, index=False)

    return FileResponse(output_file, filename=output_file)