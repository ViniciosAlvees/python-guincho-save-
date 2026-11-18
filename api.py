"""API HTTP do Guincho Save Lives. Execute com uvicorn api:app."""
from typing import Literal

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from main import estimar_preco

app = FastAPI(title="Guincho Save Lives", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://viniciosalvees.github.io",
        "http://localhost:5173",
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
def inicio():
    return {"status": "online", "projeto": "Guincho Save Lives"}


@app.get("/estimativa")
def estimativa(
    preco_base: float = Query(ge=20, le=10000, allow_inf_nan=False),
    km: float = Query(gt=0, le=1000, allow_inf_nan=False),
    tipo: Literal["carro", "moto", "utilitario"] = "carro",
    noturno: bool = False,
):
    valor = estimar_preco(preco_base, km, tipo, noturno)
    return {"valor_estimado": valor, "moeda": "BRL"}
