"""API do Guincho Save Lives: cálculos e integração com o Java."""

import os
from typing import Literal

import httpx
from fastapi import (
    Body,
    FastAPI,
    HTTPException,
    Path,
    Query,
    Request,
    Response,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from main import estimar_preco
from employee_auth import login, require_employee


app = FastAPI(
    title="Guincho Save Lives",
    description="API Python integrada ao backend Java.",
    version="1.2.0",
)

JAVA_API_URL = os.getenv(
    "JAVA_API_URL", ""
).strip().rstrip("/")

origens = os.getenv(
    "CORS_ORIGINS",
    "https://viniciosalvees.github.io,http://localhost:5173",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origem.strip()
        for origem in origens.split(",")
        if origem.strip()
    ],
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Accept",
        "Content-Type",
        "Authorization",
    ],
)


@app.middleware("http")
async def private_employee_responses(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/funcionarios") or request.url.path == "/solicitacoes":
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        response.headers["Vary"] = "Authorization, Origin"
    return response


# --------------------------------------------------
# STATUS DO PYTHON
# --------------------------------------------------

@app.get("/", tags=["Status"])
def inicio():
    # Não testa a conexão do Java com o Oracle.
    return {
        "status": "online",
        "projeto": "Guincho Save Lives",
        "java_configurado": bool(JAVA_API_URL),
    }


# --------------------------------------------------
# CÁLCULO DE PREÇO
# --------------------------------------------------

@app.get("/estimativa", tags=["Estimativa"])
def estimativa(
    preco_base: float = Query(
        ge=20,
        le=10000,
        allow_inf_nan=False,
    ),
    km: float = Query(
        gt=0,
        le=1000,
        allow_inf_nan=False,
    ),
    tipo: Literal[
        "carro",
        "moto",
        "utilitario",
    ] = "carro",
    noturno: bool = False,
):
    valor = estimar_preco(
        preco_base,
        km,
        tipo,
        noturno,
    )

    return {
        "valor_estimado": valor,
        "moeda": "BRL",
    }


# --------------------------------------------------
# COMUNICAÇÃO COM O JAVA
# --------------------------------------------------

def chamar_java(request, rota, dados=None, *, forward_authorization=True):
    if not JAVA_API_URL:
        raise HTTPException(
            status_code=503,
            detail="Configure JAVA_API_URL na Render do Python.",
        )

    if not JAVA_API_URL.startswith("https://"):
        raise HTTPException(
            status_code=503,
            detail="JAVA_API_URL deve começar com https://.",
        )

    headers = {
        "Accept": "application/json",
    }

    autorizacao = request.headers.get("authorization")

    if autorizacao and forward_authorization:
        headers["Authorization"] = autorizacao

    argumentos = {
        "headers": headers,
        "params": list(request.query_params.multi_items()),
    }

    if dados is not None:
        argumentos["json"] = dados

    try:
        with httpx.Client(
            timeout=httpx.Timeout(
                60.0,
                connect=10.0,
            ),
            follow_redirects=False,
        ) as cliente:
            resposta = cliente.request(
                method=request.method,
                url=JAVA_API_URL + rota,
                **argumentos,
            )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="O Java demorou para responder. Tente novamente.",
        ) from None

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Não foi possível acessar o backend Java.",
        ) from None

    if resposta.status_code >= 400:
        # Evita expor detalhes internos de erros JDBC.
        codigo = (
            resposta.status_code
            if resposta.status_code < 500
            else 502
        )

        return JSONResponse(
            status_code=codigo,
            content={
                "erro": (
                    "O backend Java recusou ou não conseguiu "
                    "concluir a operação."
                ),
                "status_java": resposta.status_code,
            },
        )

    if resposta.status_code == 204:
        return Response(status_code=204)

    if not 200 <= resposta.status_code < 300:
        raise HTTPException(
            status_code=502,
            detail="O Java retornou um redirecionamento inesperado.",
        )

    try:
        conteudo = resposta.json()

    except ValueError:
        raise HTTPException(
            status_code=502,
            detail="O Java retornou uma resposta que não é JSON.",
        ) from None

    return JSONResponse(
        status_code=resposta.status_code,
        content=conteudo,
    )


# --------------------------------------------------
# CLIENTES
# --------------------------------------------------

@app.get("/clientes", tags=["Clientes"])
def listar_clientes(request: Request):
    return chamar_java(
        request,
        "/clientes",
    )


@app.post("/clientes", tags=["Clientes"])
def cadastrar_cliente(
    request: Request,
    dados: dict = Body(...),
):
    return chamar_java(
        request,
        "/clientes",
        dados,
    )


@app.get("/clientes/{identificador}", tags=["Clientes"])
def obter_cliente(
    request: Request,
    identificador: int = Path(gt=0),
):
    return chamar_java(
        request,
        f"/clientes/{identificador}",
    )


@app.put("/clientes/{identificador}", tags=["Clientes"])
def atualizar_cliente(
    request: Request,
    dados: dict = Body(...),
    identificador: int = Path(gt=0),
):
    return chamar_java(
        request,
        f"/clientes/{identificador}",
        dados,
    )


@app.delete("/clientes/{identificador}", tags=["Clientes"])
def excluir_cliente(
    request: Request,
    identificador: int = Path(gt=0),
):
    return chamar_java(
        request,
        f"/clientes/{identificador}",
    )


# --------------------------------------------------
# GUINCHEIROS
# --------------------------------------------------

@app.get("/guincheiros", tags=["Guincheiros"])
def listar_guincheiros(request: Request):
    return chamar_java(
        request,
        "/guincheiros",
    )


@app.post("/guincheiros", tags=["Guincheiros"])
def cadastrar_guincheiro(
    request: Request,
    dados: dict = Body(...),
):
    return chamar_java(
        request,
        "/guincheiros",
        dados,
    )


# --------------------------------------------------
# SOLICITAÇÕES
# --------------------------------------------------

@app.get("/solicitacoes", tags=["Solicitações"])
def listar_solicitacoes(request: Request):
    require_employee(request)
    return chamar_java(
        request,
        "/solicitacoes",
        forward_authorization=False,
    )


@app.post("/solicitacoes", tags=["Solicitações"])
def criar_solicitacao(
    request: Request,
    dados: dict = Body(...),
):
    return chamar_java(
        request,
        "/solicitacoes",
        dados,
    )


# O Python autentica o funcionário; o Java continua responsável pelos pedidos.
@app.post("/funcionarios/sessao", tags=["Funcionários"])
def iniciar_sessao(request: Request, dados: dict = Body(...)):
    return login(dados.get("pin"), request)


@app.get("/funcionarios/solicitacoes", tags=["Funcionários"])
def solicitacoes_funcionario(request: Request):
    require_employee(request)
    return chamar_java(request, "/solicitacoes", forward_authorization=False)


@app.delete("/funcionarios/sessao", status_code=204, tags=["Funcionários"])
def encerrar_sessao(request: Request):
    require_employee(request)
    # Tokens assinados expiram em dez minutos; o navegador descarta a sessão ao sair.
    return Response(status_code=204)
