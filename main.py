"""Guincho Save Lives | Global Solution 2026/2 | FIAP.
Sistema de terminal acadÃªmico. Dados fictÃ­cios, sem conexÃ£o com o site.
ProgramaÃ§Ã£o estruturada: sem classes e sem list comprehensions.
"""
import json
import hashlib
import hmac
import secrets
import getpass
import math
import os
from datetime import datetime
from pathlib import Path

PASTA = Path(__file__).resolve().parent
ARQUIVO = PASTA / 'dados.json'
COMISSAO = 0.10
VALOR_KM = 4.50
STATUS = ('pendente', 'aceito', 'em_andamento', 'concluido', 'recusado', 'cancelado')
TIPOS = ('carro', 'moto', 'utilitario')


def agora():
    return datetime.now().strftime('%d/%m/%Y %H:%M')


def vazio():
    return {'clientes': [], 'guincheiros': [], 'solicitacoes': [], 'mensagens': [], 'eventos': []}


def carregar():
    if not ARQUIVO.exists():
        return vazio()
    try:
        with ARQUIVO.open('r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)
        if not isinstance(dados, dict):
            raise ValueError('Formato invÃ¡lido')
        for chave in vazio():
            if chave not in dados or not isinstance(dados[chave], list):
                dados[chave] = []
        return dados
    except (OSError, ValueError, TypeError) as erro:
        print(f'ERRO ao abrir dados.json: {erro}. Nenhum dado foi apagado.')
        print('Corrija o arquivo ou mova-o para outra pasta antes de reiniciar.')
        return None


def salvar(dados):
    """Grava primeiro em arquivo temporÃ¡rio para reduzir risco de perda de dados."""
    temporario = ARQUIVO.with_suffix('.tmp')
    try:
        with temporario.open('w', encoding='utf-8') as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)
        os.replace(temporario, ARQUIVO)
        return True
    except (OSError, TypeError) as erro:
        print(f'NÃ£o foi possÃ­vel salvar: {erro}')
        return False


def novo_id(registros):
    maior = 0
    for registro in registros:
        if registro['id'] > maior:
            maior = registro['id']
    return maior + 1


def buscar(registros, identificador):
    for registro in registros:
        if registro['id'] == identificador:
            return registro
    return None


def entrada(mensagem, limite=100):
    while True:
        valor = input(mensagem).strip()
        if 0 < len(valor) <= limite:
            return valor
        print(f'Informe entre 1 e {limite} caracteres.')


def opcional(mensagem, limite=200):
    return input(mensagem).strip()[:limite]


def inteiro(mensagem, minimo=0, maximo=None):
    while True:
        valor = input(mensagem).strip()
        try:
            numero = int(valor)
            if numero < minimo or (maximo is not None and numero > maximo):
                print('NÃºmero fora do intervalo permitido.')
            else:
                return numero
        except ValueError:
            print('Digite um nÃºmero inteiro vÃ¡lido.')


def decimal(mensagem, minimo=0, maximo=100000):
    while True:
        try:
            numero = float(input(mensagem).strip().replace(',', '.'))
            if math.isfinite(numero) and minimo <= numero <= maximo:
                return round(numero, 2)
            print('Valor fora do intervalo permitido.')
        except ValueError:
            print('Digite um valor numÃ©rico vÃ¡lido.')


def telefone_valido(telefone):
    numeros = ''
    for caractere in telefone:
        if caractere.isdigit():
            numeros += caractere
    return len(numeros) in (10, 11)


def telefone():
    while True:
        valor = entrada('Telefone com DDD (10 ou 11 dÃ­gitos): ', 20)
        if telefone_valido(valor):
            return valor
        print('Telefone invÃ¡lido. Exemplo fictÃ­cio: 11999990000.')


def confirmar(mensagem):
    return input(f'{mensagem} (S/N): ').strip().upper() == 'S'


def selecionar(registros, mensagem='Informe o cÃ³digo: '):
    if not registros:
        print('Nenhum registro disponÃ­vel.')
        return None
    identificador = inteiro(mensagem, 1)
    registro = buscar(registros, identificador)
    if registro is None:
        print('CÃ³digo nÃ£o encontrado.')
    return registro


def registrar_evento(dados, pedido, descricao):
    dados['eventos'].append({'id': novo_id(dados['eventos']), 'pedido_id': pedido['id'],
                            'data': agora(), 'descricao': descricao})


def exibir_eventos(dados, pedido_id):
    print('\nHISTÃ“RICO DO CHAMADO')
    encontrado = False
    for evento in dados['eventos']:
        if evento['pedido_id'] == pedido_id:
            print(f"{evento['data']} | {evento['descricao']}")
            encontrado = True
    if not encontrado:
        print('Sem movimentaÃ§Ãµes registradas.')


def normalizar_telefone(valor):
    return ''.join(caractere for caractere in valor if caractere.isdigit())


def criar_hash(senha, sal=None):
    """PBKDF2 com sal individual; nunca guardar a senha em texto puro."""
    if sal is None:
        sal = secrets.token_hex(16)
    resultado = hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'),
                                    bytes.fromhex(sal), 600000)
    return f'pbkdf2_sha256$600000${sal}${resultado.hex()}'


def verificar_senha(senha, hash_salvo):
    try:
        algoritmo, iteracoes, sal, esperado = hash_salvo.split('$')
        if algoritmo != 'pbkdf2_sha256' or int(iteracoes) < 100000:
            return False
        calculado = hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'),
                                        bytes.fromhex(sal), int(iteracoes))
        return hmac.compare_digest(calculado, bytes.fromhex(esperado))
    except (ValueError, TypeError, AttributeError):
        return False


def senha_segura():
    while True:
        senha = getpass.getpass('Crie uma senha (mÃ­n. 8 caracteres, letras e nÃºmeros): ')
        if len(senha) < 8 or not any(c.isalpha() for c in senha) or not any(c.isdigit() for c in senha):
            print('A senha deve ter pelo menos 8 caracteres, uma letra e um nÃºmero.')
            continue
        if senha != getpass.getpass('Confirme a senha: '):
            print('As senhas nÃ£o conferem.')
            continue
        return criar_hash(senha)


def autenticar(dados, perfil):
    registros = dados['clientes'] if perfil == 'cliente' else dados['guincheiros']
    contato = normalizar_telefone(entrada('Telefone com DDD: ', 20))
    senha = getpass.getpass('Senha: ')
    for registro in registros:
        if normalizar_telefone(registro['telefone']) == contato:
            if verificar_senha(senha, registro.get('senha_hash', '')):
                print(f"Bem-vindo(a), {registro['nome']}!")
                return registro
            break
    print('Telefone ou senha invÃ¡lidos. Cadastros antigos sem senha precisam ser recriados com dados fictÃ­cios.')
    return None


def redefinir_senha(dados, perfil):
    """RedefiniÃ§Ã£o local exige a senha atual; nÃ£o simula recuperaÃ§Ã£o por SMS."""
    usuario = autenticar(dados, perfil)
    if usuario is None:
        return
    usuario['senha_hash'] = senha_segura()
    salvar(dados)
    print('Senha atualizada.')


def preparar_admin(dados):
    """Primeiro acesso: cÃ³digo de ativaÃ§Ã£o acadÃªmico e cadastro de senha prÃ³pria."""
    if dados.get('admin_hash'):
        return True
    print('\\nPRIMEIRO ACESSO DO ADMINISTRADOR')
    print('Use o cÃ³digo de ativaÃ§Ã£o informado ao grupo e cadastre sua senha.')
    print('O cÃ³digo de ativaÃ§Ã£o nÃ£o serÃ¡ a senha permanente.')
    codigo = getpass.getpass('CÃ³digo de ativaÃ§Ã£o (8 dÃ­gitos): ')
    codigo_esperado = os.environ.get('GUINCHO_ADMIN_SETUP_CODE', '12345678')
    if not hmac.compare_digest(codigo, codigo_esperado):
        print('CÃ³digo de ativaÃ§Ã£o invÃ¡lido.')
        return False
    dados['admin_hash'] = senha_segura()
    if not salvar(dados):
        dados.pop('admin_hash', None)
        return False
    print('Administrador configurado! Use a nova senha nos prÃ³ximos acessos.')
    return True


def autenticar_admin(dados):
    if not preparar_admin(dados):
        return False
    for tentativa in range(3):
        senha = getpass.getpass('Senha do administrador: ')
        if verificar_senha(senha, dados['admin_hash']):
            return True
        print(f'Senha incorreta. Tentativas restantes: {2 - tentativa}')
    return False


def alterar_senha_admin(dados):
    atual = getpass.getpass('Senha atual do administrador: ')
    if not verificar_senha(atual, dados.get('admin_hash', '')):
        print('Senha atual incorreta.')
        return
    novo_hash = senha_segura()
    anterior = dados['admin_hash']
    dados['admin_hash'] = novo_hash
    if salvar(dados):
        print('Senha administrativa alterada.')
    else:
        dados['admin_hash'] = anterior


def cadastrar_cliente(dados):
    print('\nCADASTRO DE CLIENTE')
    nome = entrada('Nome: ')
    contato = telefone()
    for cliente in dados['clientes']:
        if normalizar_telefone(cliente['telefone']) == normalizar_telefone(contato):
            print('JÃ¡ existe um cliente com esse telefone.')
            return
    cliente = {'id': novo_id(dados['clientes']), 'nome': nome, 'telefone': contato,
               'senha_hash': senha_segura()}
    dados['clientes'].append(cliente)
    if salvar(dados):
        print(f"Cliente cadastrado. Seu cÃ³digo de demonstraÃ§Ã£o Ã© {cliente['id']}.")


def cadastrar_guincheiro(dados):
    print('\nCADASTRO DE PROFISSIONAL')
    nome = entrada('Nome: ')
    contato = telefone()
    for profissional in dados['guincheiros']:
        if normalizar_telefone(profissional['telefone']) == normalizar_telefone(contato):
            print('Telefone jÃ¡ cadastrado para um profissional.')
            return
    regiao = entrada('RegiÃ£o de atendimento: ')
    print('VeÃ­culos: 1-Carro 2-Moto 3-UtilitÃ¡rio')
    tipo = TIPOS[inteiro('Tipo atendido: ', 1, 3) - 1]
    preco = decimal('PreÃ§o de saÃ­da (R$): ', 20, 10000)
    capacidade = decimal('Capacidade mÃ¡xima em toneladas: ', 0.1, 50)
    profissional = {'id': novo_id(dados['guincheiros']), 'nome': nome, 'telefone': contato,
                    'regiao': regiao, 'tipo': tipo, 'preco_base': preco, 'senha_hash': senha_segura(),
                    'capacidade_t': capacidade, 'aprovado': False, 'disponivel': False,
                    'avaliacoes': []}
    dados['guincheiros'].append(profissional)
    if salvar(dados):
        print(f"Cadastro #{profissional['id']} enviado para anÃ¡lise administrativa.")


def media_avaliacoes(profissional):
    notas = profissional['avaliacoes']
    if not notas:
        return 0
    return sum(notas) / len(notas)


def disponiveis(dados, regiao='', tipo=''):
    resultado = []
    for profissional in dados['guincheiros']:
        if not profissional['aprovado'] or not profissional['disponivel']:
            continue
        if regiao and regiao.casefold() not in profissional['regiao'].casefold():
            continue
        if tipo and tipo != profissional['tipo']:
            continue
        resultado.append(profissional)
    resultado.sort(key=lambda item: (item['preco_base'], -media_avaliacoes(item)))
    return resultado


def listar_profissionais(profissionais):
    if not profissionais:
        print('Nenhum guincheiro disponÃ­vel para o filtro informado.')
    for profissional in profissionais:
        print(f"#{profissional['id']} | {profissional['nome']} | {profissional['regiao']} | "
              f"{profissional['tipo']} | R$ {profissional['preco_base']:.2f} saÃ­da | "
              f"nota {media_avaliacoes(profissional):.1f}/5")


def estimar_preco(preco_base, km, tipo, horario_noturno):
    """SimulaÃ§Ã£o didÃ¡tica; nÃ£o representa tabela de preÃ§os real."""
    multiplicador = 1.0
    if tipo == 'utilitario':
        multiplicador = 1.35
    elif tipo == 'moto':
        multiplicador = 0.85
    subtotal = (preco_base + km * VALOR_KM) * multiplicador
    if horario_noturno:
        subtotal *= 1.20
    return round(subtotal, 2)


def prioridade(rodovia, risco, passageiros):
    pontos = 0
    if rodovia:
        pontos += 2
    if risco:
        pontos += 3
    if passageiros:
        pontos += 1
    if pontos >= 4:
        return 'critica'
    if pontos >= 2:
        return 'alta'
    return 'normal'


def solicitar(dados, cliente):
    print('\nSOLICITAR GUINCHO')
    regiao = entrada('RegiÃ£o do veÃ­culo: ')
    print('1-Carro 2-Moto 3-UtilitÃ¡rio')
    tipo = TIPOS[inteiro('Tipo de veÃ­culo: ', 1, 3) - 1]
    encontrados = disponiveis(dados, regiao, tipo)
    listar_profissionais(encontrados)
    if not encontrados:
        return
    profissional = selecionar(encontrados, 'CÃ³digo do profissional escolhido: ')
    if profissional is None:
        return
    origem = entrada('EndereÃ§o ou referÃªncia de origem (fictÃ­cio): ', 150)
    destino = entrada('Destino do transporte (fictÃ­cio): ', 150)
    problema = entrada('Problema no veÃ­culo: ', 150)
    km = decimal('DistÃ¢ncia estimada do transporte (km): ', 0.1, 1000)
    noturno = confirmar('Atendimento noturno?')
    rodovia = confirmar('VeÃ­culo parado em rodovia ou via rÃ¡pida?')
    risco = confirmar('Existe risco imediato Ã  seguranÃ§a?')
    passageiros = confirmar('HÃ¡ passageiros precisando de apoio?')
    nivel = prioridade(rodovia, risco, passageiros)
    if risco:
        print('ATENÃ‡ÃƒO: em perigo imediato, afaste-se da via quando seguro e acione os serviÃ§os de emergÃªncia adequados.')
        print('Este protÃ³tipo nÃ£o substitui atendimento emergencial.')
    valor = estimar_preco(profissional['preco_base'], km, tipo, noturno)
    print(f'PreÃ§o ilustrativo: R$ {valor:.2f} | prioridade: {nivel}')
    if not confirmar('Registrar solicitaÃ§Ã£o?'):
        return
    pedido = {'id': novo_id(dados['solicitacoes']), 'cliente_id': cliente['id'],
              'guincheiro_id': profissional['id'], 'regiao': regiao, 'tipo': tipo,
              'origem': origem, 'destino': destino, 'problema': problema,
              'km_estimado': km, 'noturno': noturno, 'prioridade': nivel,
              'valor': valor, 'proposta': None, 'proponente': None,
              'status': 'pendente', 'avaliado': False, 'criado_em': agora()}
    dados['solicitacoes'].append(pedido)
    registrar_evento(dados, pedido, 'SolicitaÃ§Ã£o criada; aguardando profissional')
    if salvar(dados):
        print(f"Chamado #{pedido['id']} registrado.")


def mostrar_pedidos(pedidos):
    if not pedidos:
        print('Nenhum chamado encontrado.')
    for pedido in pedidos:
        print(f"#{pedido['id']} | {pedido['status']} | prioridade {pedido['prioridade']} | "
              f"{pedido['tipo']} | R$ {pedido['valor']:.2f} | "
              f"cliente #{pedido['cliente_id']} / profissional #{pedido['guincheiro_id']}")


def pedidos_de(dados, campo, identificador):
    encontrados = []
    for pedido in dados['solicitacoes']:
        if pedido[campo] == identificador:
            encontrados.append(pedido)
    return encontrados


def pedido_autorizado(dados, campo, identificador):
    encontrados = pedidos_de(dados, campo, identificador)
    mostrar_pedidos(encontrados)
    if not encontrados:
        return None
    return selecionar(encontrados, 'NÃºmero do chamado: ')


def negociar(dados, pedido, perfil):
    if pedido['status'] != 'pendente':
        print('NegociaÃ§Ã£o permitida somente em chamados pendentes.')
        return
    if pedido['proposta'] is not None:
        print(f"Proposta atual: R$ {pedido['proposta']:.2f}, enviada por {pedido['proponente']}.")
        if pedido['proponente'] != perfil:
            print('1-Aceitar proposta 2-Fazer contraproposta 0-Voltar')
            opcao = input('OpÃ§Ã£o: ').strip()
            if opcao == '1':
                pedido['valor'] = pedido['proposta']
                pedido['proposta'] = None
                pedido['proponente'] = None
                registrar_evento(dados, pedido, f'Proposta aceita por {perfil}')
                salvar(dados)
                print('PreÃ§o acordado. Aguardando aceite do chamado pelo guincheiro.')
                return
            if opcao != '2':
                return
        else:
            print('Aguarde contraproposta ou resposta da outra parte.')
            return
    valor = decimal('Novo valor proposto (R$): ', 20, 100000)
    pedido['proposta'] = valor
    pedido['proponente'] = perfil
    registrar_evento(dados, pedido, f'{perfil} enviou proposta de R$ {valor:.2f}')
    salvar(dados)
    print('Proposta registrada. A outra parte precisa aceitar ou contrapropor.')


def mensagens(dados, pedido, perfil):
    print('\nMENSAGENS LOCAIS DO CHAMADO (nÃ£o Ã© chat em tempo real)')
    for mensagem in dados['mensagens']:
        if mensagem['pedido_id'] == pedido['id']:
            print(f"{mensagem['data']} | {mensagem['perfil']}: {mensagem['texto']}")
    if pedido['status'] in ('cancelado', 'recusado', 'concluido'):
        print('Chamado encerrado. Mensagens somente para consulta.')
        return
    texto = opcional('Escreva uma mensagem (Enter para voltar): ', 300)
    if texto:
        dados['mensagens'].append({'id': novo_id(dados['mensagens']), 'pedido_id': pedido['id'],
                                   'perfil': perfil, 'texto': texto, 'data': agora()})
        salvar(dados)
        print('Mensagem salva no computador.')


def avaliar(dados, pedido):
    if pedido['status'] != 'concluido' or pedido['avaliado']:
        print('Somente chamados concluÃ­dos e ainda nÃ£o avaliados podem receber nota.')
        return
    nota = inteiro('Nota de 1 a 5: ', 1, 5)
    comentario = opcional('ComentÃ¡rio (opcional): ', 200)
    profissional = buscar(dados['guincheiros'], pedido['guincheiro_id'])
    if profissional is None:
        print('Profissional nÃ£o encontrado.')
        return
    profissional['avaliacoes'].append(nota)
    pedido['avaliado'] = True
    pedido['comentario'] = comentario
    registrar_evento(dados, pedido, f'Avaliado com nota {nota}/5')
    salvar(dados)
    print('Obrigado pela avaliaÃ§Ã£o!')


def alterar_status(dados, pedido, novo_status):
    permitidos = {'pendente': ('aceito', 'recusado', 'cancelado'),
                  'aceito': ('em_andamento',), 'em_andamento': ('concluido',)}
    if novo_status not in permitidos.get(pedido['status'], ()):
        print(f"NÃ£o Ã© possÃ­vel passar de {pedido['status']} para {novo_status}.")
        return False
    if novo_status == 'aceito' and pedido['proposta'] is not None:
        print('Existe uma proposta em aberto. Resolva a negociaÃ§Ã£o primeiro.')
        return False
    pedido['status'] = novo_status
    registrar_evento(dados, pedido, f'Status alterado para {novo_status}')
    salvar(dados)
    print(f'Status atualizado: {novo_status}.')
    return True


def area_cliente(dados):
    while True:
        print('\n=== CLIENTE ===')
        print('1-Cadastrar 2-Entrar 3-Alterar senha 0-Voltar')
        opcao = input('OpÃ§Ã£o: ').strip()
        if opcao == '1':
            cadastrar_cliente(dados)
        elif opcao == '3':
            redefinir_senha(dados, 'cliente')
        elif opcao == '2':
            cliente = autenticar(dados, 'cliente')
            if cliente:
                menu_cliente(dados, cliente)
        elif opcao == '0':
            return
        else:
            print('OpÃ§Ã£o invÃ¡lida.')


def menu_cliente(dados, cliente):
    while True:
        print(f"\n=== CLIENTE: {cliente['nome']} ===")
        print('1-Buscar guincheiros 2-Solicitar 3-Meus chamados 4-Negociar')
        print('5-Mensagens 6-Cancelar 7-Avaliar 8-HistÃ³rico 0-Sair da conta')
        opcao = input('OpÃ§Ã£o: ').strip()
        match opcao:
            case '1':
                regiao = opcional('RegiÃ£o (Enter para todas): ')
                listar_profissionais(disponiveis(dados, regiao))
            case '2':
                solicitar(dados, cliente)
            case '3':
                mostrar_pedidos(pedidos_de(dados, 'cliente_id', cliente['id']))
            case '4' | '5' | '6' | '7' | '8':
                pedido = pedido_autorizado(dados, 'cliente_id', cliente['id'])
                if pedido is None:
                    continue
                match opcao:
                    case '4': negociar(dados, pedido, 'cliente')
                    case '5': mensagens(dados, pedido, 'cliente')
                    case '6': alterar_status(dados, pedido, 'cancelado')
                    case '7': avaliar(dados, pedido)
                    case '8': exibir_eventos(dados, pedido['id'])
            case '0':
                return
            case _:
                print('OpÃ§Ã£o invÃ¡lida.')


def area_guincheiro(dados):
    while True:
        print('\n=== GUINCHEIRO ===')
        print('1-Cadastrar 2-Entrar 3-Alterar senha 0-Voltar')
        opcao = input('OpÃ§Ã£o: ').strip()
        if opcao == '1':
            cadastrar_guincheiro(dados)
        elif opcao == '2':
            profissional = autenticar(dados, 'guincheiro')
            if profissional:
                if profissional['aprovado']:
                    menu_guincheiro(dados, profissional)
                else:
                    print('Cadastro aguardando aprovaÃ§Ã£o administrativa.')
        elif opcao == '3':
            redefinir_senha(dados, 'guincheiro')
        elif opcao == '0':
            return
        else:
            print('OpÃ§Ã£o invÃ¡lida.')


def menu_guincheiro(dados, profissional):
    while True:
        print(f"\n=== GUINCHEIRO: {profissional['nome']} ===")
        print('1-Disponibilidade 2-Meus chamados 3-Aceitar 4-Recusar')
        print('5-Iniciar 6-Concluir 7-Negociar 8-Mensagens 9-HistÃ³rico 0-Sair da conta')
        opcao = input('OpÃ§Ã£o: ').strip()
        if opcao == '0':
            return
        if opcao == '1':
            profissional['disponivel'] = not profissional['disponivel']
            salvar(dados)
            print(f"Disponibilidade: {'ativa' if profissional['disponivel'] else 'inativa'}")
            continue
        if opcao == '2':
            mostrar_pedidos(pedidos_de(dados, 'guincheiro_id', profissional['id']))
            continue
        if opcao not in ('3', '4', '5', '6', '7', '8', '9'):
            print('OpÃ§Ã£o invÃ¡lida.')
            continue
        pedido = pedido_autorizado(dados, 'guincheiro_id', profissional['id'])
        if pedido is None:
            continue
        match opcao:
            case '3': alterar_status(dados, pedido, 'aceito')
            case '4': alterar_status(dados, pedido, 'recusado')
            case '5': alterar_status(dados, pedido, 'em_andamento')
            case '6': alterar_status(dados, pedido, 'concluido')
            case '7': negociar(dados, pedido, 'guincheiro')
            case '8': mensagens(dados, pedido, 'guincheiro')
            case '9': exibir_eventos(dados, pedido['id'])


def relatorio(dados):
    print('\n=== INDICADORES DO PROJETO ===')
    print(f"Clientes: {len(dados['clientes'])} | Guincheiros: {len(dados['guincheiros'])}")
    print(f"SolicitaÃ§Ãµes: {len(dados['solicitacoes'])}")
    faturamento = 0
    valores = []
    for status in STATUS:
        total = 0
        for pedido in dados['solicitacoes']:
            if pedido['status'] == status:
                total += 1
                if status == 'concluido':
                    faturamento += pedido['valor']
                    valores.append(pedido['valor'])
        print(f'{status}: {total}')
    comissao = round(faturamento * COMISSAO, 2)
    print(f'Valor bruto concluÃ­do: R$ {faturamento:.2f}')
    print(f'ComissÃ£o simulada ({COMISSAO:.0%}): R$ {comissao:.2f}')
    print(f'Repasse simulado aos profissionais: R$ {faturamento - comissao:.2f}')
    if valores:
        print(f'TÃ­quete mÃ©dio: R$ {sum(valores) / len(valores):.2f}')
        print(f'Menor/maior serviÃ§o: R$ {min(valores):.2f} / R$ {max(valores):.2f}')
    regioes = set()
    for profissional in dados['guincheiros']:
        if profissional['aprovado'] and profissional['disponivel']:
            regioes.add(profissional['regiao'].title())
    print(f"RegiÃµes ativas: {', '.join(sorted(regioes)) or 'nenhuma'}")


def area_administrador(dados):
    if not autenticar_admin(dados):
        print('Acesso negado.')
        return
    while True:
        print('\n=== ADMINISTRADOR ===')
        print('1-Cadastros pendentes 2-Aprovar profissional 3-RelatÃ³rios 4-Todos os chamados 5-Alterar senha 0-Voltar')
        match input('OpÃ§Ã£o: ').strip():
            case '1':
                for profissional in dados['guincheiros']:
                    if not profissional['aprovado']:
                        print(f"#{profissional['id']} | {profissional['nome']} | {profissional['regiao']}")
            case '2':
                profissional = selecionar(dados['guincheiros'], 'CÃ³digo profissional: ')
                if profissional and confirmar('Aprovar este cadastro?'):
                    profissional['aprovado'] = True
                    salvar(dados)
                    print('Cadastro aprovado.')
            case '3': relatorio(dados)
            case '4': mostrar_pedidos(dados['solicitacoes'])
            case '5': alterar_senha_admin(dados)
            case '0': return
            case _: print('OpÃ§Ã£o invÃ¡lida.')


def main():
    dados = carregar()
    if dados is None:
        return
    print('GUINCHO SAVE LIVES | GLOBAL SOLUTION | PROTÃ“TIPO DE TERMINAL')
    print('API de referÃªncia: https://python-guincho-save.onrender.com (sem integraÃ§Ã£o automÃ¡tica)')
    print('Utilize apenas dados fictÃ­cios. NÃ£o hÃ¡ pagamentos, GPS ou atendimento real.')
    while True:
        print('\n=== MENU PRINCIPAL ===')
        print('1-Cliente 2-Guincheiro 3-Administrador 0-Sair')
        match input('OpÃ§Ã£o: ').strip():
            case '1': area_cliente(dados)
            case '2': area_guincheiro(dados)
            case '3': area_administrador(dados)
            case '0':
                print('Programa encerrado. AtÃ© logo!')
                return
            case _: print('OpÃ§Ã£o invÃ¡lida.')


if __name__ == '__main__':
    main()
