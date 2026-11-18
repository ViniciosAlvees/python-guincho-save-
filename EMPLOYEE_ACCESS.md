# Acesso de funcionários do site

O PIN do programa de terminal é independente do site. A API Python agora oferece:

- `POST /funcionarios/sessao`, JSON `{"pin": "..."}`: valida o PIN privado e devolve `token` e `expiresAt`.
- `GET /funcionarios/solicitacoes`, com `Authorization: Bearer ...`: consulta `/solicitacoes` no Java após validar a sessão. O token Python não é enviado ao Java.
- `DELETE /funcionarios/sessao`: confirma a saída; o frontend apaga o token da memória.
- `GET /solicitacoes` também exige sessão; a criação pública de solicitações continua disponível.

O frontend utiliza o proxy `/api/python` da própria origem. Login, erros e pedidos usam `Cache-Control: no-store`. Nenhum PIN fica no bundle, no Git, em URL ou no armazenamento do navegador.

## Configuração privada

Execute `python configure_employee.py`, informe o PIN desejado e configure os valores gerados como Secrets **somente no projeto Python**, no ambiente de produção da Vercel:

- `EMPLOYEE_PIN_HASH`: PBKDF2-HMAC-SHA256, 600.000 iterações e salt aleatório.
- `EMPLOYEE_SESSION_SECRET`: chave aleatória para assinar as sessões.

Faça um novo deploy após configurar as variáveis. Ausência ou formato inválido fecha o acesso com HTTP 503; PIN incorreto retorna 401. Não defina essas variáveis com prefixo `VITE_`.

As sessões assinadas duram dez minutos e funcionam entre instâncias serverless, sem depender de arquivos ou de dicionários de sessões em memória. Sair ou recarregar remove o token do navegador. **Um token copiado anteriormente continua válido até expirar**; revogação individual imediata exige um armazenamento compartilhado de sessões. Alterar o hash do PIN ou a chave e publicar novamente invalida todas as sessões.

O limite adicional de cinco tentativas por cinco minutos é por endereço de conexão e por instância. Ele não substitui uma regra distribuída de rate limiting na infraestrutura. Os testes locais verificam essa limitação, expiração, adulteração, falta de configuração e proteção das consultas.

O Java continua independente: erro de banco retorna 502/504; uma futura exigência de credencial própria no Java precisará de integração entre servidores. A proteção desta API não restringe a URL direta do Java, administrada em outro repositório.

## Testes

```bash
python -m pip install -r requirements.txt
python -m unittest test_employee_api.py -v
python testes.py
```
