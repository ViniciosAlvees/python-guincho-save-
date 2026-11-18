# Guincho Save Lives | Python | FIAP Global Solution 2026/2

AplicaÃ§Ã£o acadÃªmica de **terminal**, independente do site e da API Java. Usa apenas a biblioteca padrÃ£o do Python. NÃ£o utiliza classes, orientaÃ§Ã£o a objetos ou list comprehensions.

## Executar

1. Instale Python 3.10 ou superior.
2. Abra a pasta no VS Code e execute `python main.py` (Windows: `py main.py`).
3. Para rodar os testes: `python testes.py`.
4. No primeiro acesso administrativo, digite o **cÃ³digo de ativaÃ§Ã£o 12345678** e crie uma senha pessoal forte. O cÃ³digo sÃ³ vale para a configuraÃ§Ã£o inicial. Em seguida, faÃ§a login com a senha criada. Ã‰ possÃ­vel alterÃ¡-la no menu do administrador. Para implantaÃ§Ãµes pÃºblicas, configure a variÃ¡vel de ambiente `GUINCHO_ADMIN_SETUP_CODE` com um cÃ³digo secreto e proteja o armazenamento.\n5. O arquivo `dados.json` Ã© criado automaticamente apÃ³s a primeira gravaÃ§Ã£o. Para comeÃ§ar do zero, faÃ§a uma cÃ³pia de seguranÃ§a e remova esse arquivo.

## DemonstraÃ§Ã£o sugerida

1. Entre em **Cliente** e cadastre um cliente com telefone fictÃ­cio.
2. Entre em **Guincheiro** e cadastre um profissional da mesma regiÃ£o, tipo `carro`.
3. Em **Administrador**, aprove o profissional.
4. Em **Guincheiro**, ative a disponibilidade.
5. Em **Cliente**, busque e solicite atendimento, veja estimativa e prioridade.
6. Negocie uma proposta entre cliente e profissional, aceite a proposta e o chamado.
7. Inicie e conclua o atendimento como guincheiro.
8. Avalie como cliente e abra o relatÃ³rio administrativo para ver a comissÃ£o.

## Regras principais

- O guincheiro sÃ³ aparece na busca se aprovado e disponÃ­vel.
- A busca filtra regiÃ£o e tipo de veÃ­culo; ordena por preÃ§o de saÃ­da e avaliaÃ§Ã£o.
- A estimativa usa preÃ§o de saÃ­da + R$ 4,50/km, multiplicadores demonstrativos de tipo de veÃ­culo e adicional noturno.
- A prioridade usa trÃªs respostas simples; risco imediato gera orientaÃ§Ã£o para procurar serviÃ§os de emergÃªncia.
- SÃ³ o cliente do pedido pode cancelar/avaliar; sÃ³ o profissional associado pode mudar o andamento.
- Estados: `pendente -> aceito -> em_andamento -> concluido`; pendente tambÃ©m pode ser recusado ou cancelado.
- Propostas precisam ser aceitas pela outra parte antes de o profissional aceitar o chamado.
- ComissÃ£o simulada: **10% do valor de serviÃ§os concluÃ­dos**. NÃ£o hÃ¡ cobranÃ§a nem pagamento real.
- HistÃ³rico e mensagens sÃ£o armazenados localmente, nÃ£o hÃ¡ WhatsApp, GPS ou chat em tempo real.

## LimitaÃ§Ãµes e seguranÃ§a

Este Ã© um protÃ³tipo para avaliaÃ§Ã£o acadÃªmica. Os cÃ³digos numÃ©ricos **nÃ£o sÃ£o autenticaÃ§Ã£o**; o administrador utiliza senha protegida por PBKDF2; os dados JSON nÃ£o sÃ£o criptografados. NÃ£o utilize informaÃ§Ãµes pessoais reais. NÃ£o hÃ¡ conexÃ£o automÃ¡tica com o site `gincho-save-lives.vercel.app` nem com o banco Oracle. As regras de preÃ§os e prioridades sÃ£o hipÃ³teses didÃ¡ticas, nÃ£o serviÃ§os reais.

## IA generativa

O ChatGPT foi usado para apoiar o planejamento, elaboraÃ§Ã£o e revisÃ£o do cÃ³digo e da documentaÃ§Ã£o. O grupo deve revisar, compreender, testar e declarar esse uso conforme as regras da FIAP.
\n## API informada pelo grupo\n\n`https://python-guincho-save.onrender.com` respondeu com status online e `java_configurado: true` na rota raiz. O cÃ³digo local apenas mostra essa referÃªncia, sem chamar endpoints ou modificar o serviÃ§o remoto. NÃ£o foi verificada documentaÃ§Ã£o de rotas nem credenciais de implantaÃ§Ã£o.\n
