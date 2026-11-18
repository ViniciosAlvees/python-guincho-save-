# API Python na Vercel

A aplicação web é a instância `app` do FastAPI em `api.py`. O arquivo `main.py` contém o programa de terminal e a função de cálculo importada pela API.

O `pyproject.toml` define explicitamente `api:app` como entrypoint da Vercel, Python 3.12 e as dependências da API. A Vercel prioriza esse arquivo quando ele existe; por isso as dependências também precisam estar declaradas nele. O `requirements.txt` mantém as mesmas versões para instalação via pip e outros provedores. Atualizar os dois arquivos juntos ao alterar bibliotecas.

Na Vercel, selecionar o preset **FastAPI** e a raiz do repositório. Não usar `python main.py` como comando de build ou de inicialização.

Variáveis de ambiente:

- `JAVA_API_URL`: URL HTTPS do backend Java, sem barra final. Necessária para as rotas de clientes, guincheiros e solicitações; a estimativa não depende do Java.
- `CORS_ORIGINS`: origens permitidas, separadas por vírgula. Para o frontend atual, incluir `https://gincho-save-lives.vercel.app`.
- `EMPLOYEE_PIN_HASH` e `EMPLOYEE_SESSION_SECRET`: Secrets somente no servidor para o acesso de funcionários. Gere com `python configure_employee.py`, configure no ambiente de produção e publique novamente. Consulte [o contrato e os limites das sessões](EMPLOYEE_ACCESS.md).

Após publicar, verificar `GET /`, `GET /openapi.json` e `GET /estimativa?preco_base=180&km=10&tipo=carro&noturno=false`. O exemplo deve retornar `{"valor_estimado":225.0,"moeda":"BRL"}`.

O status `java_configurado: true` apenas confirma que a variável foi definida; não comprova conexão com Java/Oracle. A API não usa `dados.json` para persistência. Esse arquivo pertence somente ao programa de terminal.
