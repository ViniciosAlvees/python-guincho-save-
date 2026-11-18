"""Guincho Save Lives | Global Solution 2026/2 | FIAP.
Sistema de terminal acadêmico. Dados fictícios, sem conexão com o site.
Programação estruturada: sem classes e sem list comprehensions.
"""
import json
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
            raise ValueError('Formato inválido')
        for chave in vazio():
            if chave not in dados or not isinstance(dados[chave], list):
                dados[chave] = []
        return dados
    except (OSError, ValueError, TypeError) as erro:
        print(f'ERRO ao abrir dados.json: {erro}. Nenhum dado foi apagado.')
        print('Corrija o arquivo ou mova-o para outra pasta antes de reiniciar.')
        return None


def salvar(dados):
    """Grava primeiro em arquivo temporário para reduzir risco de perda de dados."""
    temporario = ARQUIVO.with_suffix('.tmp')
    try:
        with temporario.open('w', encoding='utf-8') as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)
        os.replace(temporario, ARQUIVO)
        return True
    except (OSError, TypeError) as erro:
        print(f'Não foi possível salvar: {erro}')
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
                print('Número fora do intervalo permitido.')
            else:
                return numero
        except ValueError:
            print('Digite um número inteiro válido.')


def decimal(mensagem, minimo=0, maximo=100000):
    while True:
        try:
            numero = float(input(mensagem).strip().replace(',', '.'))
            if math.isfinite(numero) and minimo <= numero <= maximo:
                return round(numero, 2)
            print('Valor fora do intervalo permitido.')
        except ValueError:
            print('Digite um valor numérico válido.')


def telefone_valido(telefone):
    numeros = ''
    for caractere in telefone:
        if caractere.isdigit():
            numeros += caractere
    return len(numeros) in (10, 11)


def telefone():
    while True:
        valor = entrada('Telefone com DDD (10 ou 11 dígitos): ', 20)
        if telefone_valido(valor):
            return valor
        print('Telefone inválido. Exemplo fictício: 11999990000.')


def confirmar(mensagem):
    return input(f'{mensagem} (S/N): ').strip().upper() == 'S'


def selecionar(registros, mensagem='Informe o código: '):
    if not registros:
        print('Nenhum registro disponível.')
        return None
    identificador = inteiro(mensagem, 1)
    registro = buscar(registros, identificador)
    if registro is None:
        print('Código não encontrado.')
    return registro


def registrar_evento(dados, pedido, descricao):
    dados['eventos'].append({'id': novo_id(dados['eventos']), 'pedido_id': pedido['id'],
                            'data': agora(), 'descricao': descricao})


def exibir_eventos(dados, pedido_id):
    print('\nHISTÓRICO DO CHAMADO')
    encontrado = False
    for evento in dados['eventos']:
        if evento['pedido_id'] == pedido_id:
            print(f"{evento['data']} | {evento['descricao']}")
            encontrado = True
    if not encontrado:
        print('Sem movimentações registradas.')


def cadastrar_cliente(dados):
    print('\nCADASTRO DE CLIENTE')
    nome = entrada('Nome: ')
    contato = telefone()
    for cliente in dados['clientes']:
        if cliente['telefone'] == contato:
            print('Já existe um cliente com esse telefone.')
            return
    cliente = {'id': novo_id(dados['clientes']), 'nome': nome, 'telefone': contato}
    dados['clientes'].append(cliente)
    if salvar(dados):
        print(f"Cliente cadastrado. Seu código de demonstração é {cliente['id']}.")


def cadastrar_guincheiro(dados):
    print('\nCADASTRO DE PROFISSIONAL')
    nome = entrada('Nome: ')
    contato = telefone()
    for profissional in dados['guincheiros']:
        if profissional['telefone'] == contato:
            print('Telefone já cadastrado para um profissional.')
            return
    regiao = entrada('Região de atendimento: ')
    print('Veículos: 1-Carro 2-Moto 3-Utilitário')
    tipo = TIPOS[inteiro('Tipo atendido: ', 1, 3) - 1]
    preco = decimal('Preço de saída (R$): ', 20, 10000)
    capacidade = decimal('Capacidade máxima em toneladas: ', 0.1, 50)
    profissional = {'id': novo_id(dados['guincheiros']), 'nome': nome, 'telefone': contato,
                    'regiao': regiao, 'tipo': tipo, 'preco_base': preco,
                    'capacidade_t': capacidade, 'aprovado': False, 'disponivel': False,
                    'avaliacoes': []}
    dados['guincheiros'].append(profissional)
    if salvar(dados):
        print(f"Cadastro #{profissional['id']} enviado para análise administrativa.")


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
        print('Nenhum guincheiro disponível para o filtro informado.')
    for profissional in profissionais:
        print(f"#{profissional['id']} | {profissional['nome']} | {profissional['regiao']} | "
              f"{profissional['tipo']} | R$ {profissional['preco_base']:.2f} saída | "
              f"nota {media_avaliacoes(profissional):.1f}/5")


def estimar_preco(preco_base, km, tipo, horario_noturno):
    """Simulação didática; não representa tabela de preços real."""
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


def solicitar(dados):
    print('\nSOLICITAR GUINCHO')
    for cliente in dados['clientes']:
        print(f"#{cliente['id']} | {cliente['nome']}")
    cliente = selecionar(dados['clientes'], 'Seu código de cliente: ')
    if cliente is None:
        return
    regiao = entrada('Região do veículo: ')
    print('1-Carro 2-Moto 3-Utilitário')
    tipo = TIPOS[inteiro('Tipo de veículo: ', 1, 3) - 1]
    encontrados = disponiveis(dados, regiao, tipo)
    listar_profissionais(encontrados)
    if not encontrados:
        return
    profissional = selecionar(encontrados, 'Código do profissional escolhido: ')
    if profissional is None:
        return
    origem = entrada('Endereço ou referência de origem (fictício): ', 150)
    destino = entrada('Destino do transporte (fictício): ', 150)
    problema = entrada('Problema no veículo: ', 150)
    km = decimal('Distância estimada do transporte (km): ', 0.1, 1000)
    noturno = confirmar('Atendimento noturno?')
    rodovia = confirmar('Veículo parado em rodovia ou via rápida?')
    risco = confirmar('Existe risco imediato à segurança?')
    passageiros = confirmar('Há passageiros precisando de apoio?')
    nivel = prioridade(rodovia, risco, passageiros)
    if risco:
        print('ATENÇÃO: em perigo imediato, afaste-se da via quando seguro e acione os serviços de emergência adequados.')
        print('Este protótipo não substitui atendimento emergencial.')
    valor = estimar_preco(profissional['preco_base'], km, tipo, noturno)
    print(f'Preço ilustrativo: R$ {valor:.2f} | prioridade: {nivel}')
    if not confirmar('Registrar solicitação?'):
        return
    pedido = {'id': novo_id(dados['solicitacoes']), 'cliente_id': cliente['id'],
              'guincheiro_id': profissional['id'], 'regiao': regiao, 'tipo': tipo,
              'origem': origem, 'destino': destino, 'problema': problema,
              'km_estimado': km, 'noturno': noturno, 'prioridade': nivel,
              'valor': valor, 'proposta': None, 'proponente': None,
              'status': 'pendente', 'avaliado': False, 'criado_em': agora()}
    dados['solicitacoes'].append(pedido)
    registrar_evento(dados, pedido, 'Solicitação criada; aguardando profissional')
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
    return selecionar(encontrados, 'Número do chamado: ')


def negociar(dados, pedido, perfil):
    if pedido['status'] != 'pendente':
        print('Negociação permitida somente em chamados pendentes.')
        return
    if pedido['proposta'] is not None:
        print(f"Proposta atual: R$ {pedido['proposta']:.2f}, enviada por {pedido['proponente']}.")
        if pedido['proponente'] != perfil:
            print('1-Aceitar proposta 2-Fazer contraproposta 0-Voltar')
            opcao = input('Opção: ').strip()
            if opcao == '1':
                pedido['valor'] = pedido['proposta']
                pedido['proposta'] = None
                pedido['proponente'] = None
                registrar_evento(dados, pedido, f'Proposta aceita por {perfil}')
                salvar(dados)
                print('Preço acordado. Aguardando aceite do chamado pelo guincheiro.')
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
    print('\nMENSAGENS LOCAIS DO CHAMADO (não é chat em tempo real)')
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
        print('Somente chamados concluídos e ainda não avaliados podem receber nota.')
        return
    nota = inteiro('Nota de 1 a 5: ', 1, 5)
    comentario = opcional('Comentário (opcional): ', 200)
    profissional = buscar(dados['guincheiros'], pedido['guincheiro_id'])
    if profissional is None:
        print('Profissional não encontrado.')
        return
    profissional['avaliacoes'].append(nota)
    pedido['avaliado'] = True
    pedido['comentario'] = comentario
    registrar_evento(dados, pedido, f'Avaliado com nota {nota}/5')
    salvar(dados)
    print('Obrigado pela avaliação!')


def alterar_status(dados, pedido, novo_status):
    permitidos = {'pendente': ('aceito', 'recusado', 'cancelado'),
                  'aceito': ('em_andamento',), 'em_andamento': ('concluido',)}
    if novo_status not in permitidos.get(pedido['status'], ()):
        print(f"Não é possível passar de {pedido['status']} para {novo_status}.")
        return False
    if novo_status == 'aceito' and pedido['proposta'] is not None:
        print('Existe uma proposta em aberto. Resolva a negociação primeiro.')
        return False
    pedido['status'] = novo_status
    registrar_evento(dados, pedido, f'Status alterado para {novo_status}')
    salvar(dados)
    print(f'Status atualizado: {novo_status}.')
    return True


def area_cliente(dados):
    while True:
        print('\n=== CLIENTE ===')
        print('1-Cadastrar 2-Buscar guincheiros 3-Solicitar 4-Meus chamados 5-Negociar')
        print('6-Mensagens 7-Cancelar 8-Avaliar 9-Histórico do chamado 0-Voltar')
        match input('Opção: ').strip():
            case '1':
                cadastrar_cliente(dados)
            case '2':
                regiao = opcional('Região (Enter para todas): ')
                listar_profissionais(disponiveis(dados, regiao))
            case '3':
                solicitar(dados)
            case '4' | '5' | '6' | '7' | '8' | '9' as opcao:
                cliente = selecionar(dados['clientes'], 'Seu código: ')
                if cliente is None:
                    continue
                if opcao == '4':
                    mostrar_pedidos(pedidos_de(dados, 'cliente_id', cliente['id']))
                    continue
                pedido = pedido_autorizado(dados, 'cliente_id', cliente['id'])
                if pedido is None:
                    continue
                match opcao:
                    case '5': negociar(dados, pedido, 'cliente')
                    case '6': mensagens(dados, pedido, 'cliente')
                    case '7': alterar_status(dados, pedido, 'cancelado')
                    case '8': avaliar(dados, pedido)
                    case '9': exibir_eventos(dados, pedido['id'])
            case '0':
                return
            case _:
                print('Opção inválida.')


def area_guincheiro(dados):
    while True:
        print('\n=== GUINCHEIRO ===')
        print('1-Cadastrar 2-Disponibilidade 3-Meus chamados 4-Aceitar 5-Recusar')
        print('6-Iniciar atendimento 7-Concluir 8-Negociar 9-Mensagens 10-Histórico 0-Voltar')
        opcao = input('Opção: ').strip()
        if opcao == '0':
            return
        if opcao == '1':
            cadastrar_guincheiro(dados)
            continue
        profissional = selecionar(dados['guincheiros'], 'Seu código profissional: ')
        if profissional is None:
            continue
        if not profissional['aprovado']:
            print('Cadastro aguardando aprovação administrativa.')
            continue
        if opcao == '2':
            profissional['disponivel'] = not profissional['disponivel']
            salvar(dados)
            print(f"Disponibilidade: {'ativa' if profissional['disponivel'] else 'inativa'}")
            continue
        if opcao == '3':
            mostrar_pedidos(pedidos_de(dados, 'guincheiro_id', profissional['id']))
            continue
        pedido = pedido_autorizado(dados, 'guincheiro_id', profissional['id'])
        if pedido is None:
            continue
        match opcao:
            case '4': alterar_status(dados, pedido, 'aceito')
            case '5': alterar_status(dados, pedido, 'recusado')
            case '6': alterar_status(dados, pedido, 'em_andamento')
            case '7': alterar_status(dados, pedido, 'concluido')
            case '8': negociar(dados, pedido, 'guincheiro')
            case '9': mensagens(dados, pedido, 'guincheiro')
            case '10': exibir_eventos(dados, pedido['id'])
            case _: print('Opção inválida.')


def relatorio(dados):
    print('\n=== INDICADORES DO PROJETO ===')
    print(f"Clientes: {len(dados['clientes'])} | Guincheiros: {len(dados['guincheiros'])}")
    print(f"Solicitações: {len(dados['solicitacoes'])}")
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
    print(f'Valor bruto concluído: R$ {faturamento:.2f}')
    print(f'Comissão simulada ({COMISSAO:.0%}): R$ {comissao:.2f}')
    print(f'Repasse simulado aos profissionais: R$ {faturamento - comissao:.2f}')
    if valores:
        print(f'Tíquete médio: R$ {sum(valores) / len(valores):.2f}')
        print(f'Menor/maior serviço: R$ {min(valores):.2f} / R$ {max(valores):.2f}')
    regioes = set()
    for profissional in dados['guincheiros']:
        if profissional['aprovado'] and profissional['disponivel']:
            regioes.add(profissional['regiao'].title())
    print(f"Regiões ativas: {', '.join(sorted(regioes)) or 'nenhuma'}")


def area_administrador(dados):
    print('AVISO: área administrativa didática, sem autenticação. Não usar com dados reais.')
    while True:
        print('\n=== ADMINISTRADOR ===')
        print('1-Cadastros pendentes 2-Aprovar profissional 3-Relatórios 4-Todos os chamados 0-Voltar')
        match input('Opção: ').strip():
            case '1':
                for profissional in dados['guincheiros']:
                    if not profissional['aprovado']:
                        print(f"#{profissional['id']} | {profissional['nome']} | {profissional['regiao']}")
            case '2':
                profissional = selecionar(dados['guincheiros'], 'Código profissional: ')
                if profissional and confirmar('Aprovar este cadastro?'):
                    profissional['aprovado'] = True
                    salvar(dados)
                    print('Cadastro aprovado.')
            case '3': relatorio(dados)
            case '4': mostrar_pedidos(dados['solicitacoes'])
            case '0': return
            case _: print('Opção inválida.')


def main():
    dados = carregar()
    if dados is None:
        return
    print('GUINCHO SAVE LIVES | GLOBAL SOLUTION | PROTÓTIPO DE TERMINAL')
    print('Utilize apenas dados fictícios. Não há pagamentos, GPS ou atendimento real.')
    while True:
        print('\n=== MENU PRINCIPAL ===')
        print('1-Cliente 2-Guincheiro 3-Administrador 0-Sair')
        match input('Opção: ').strip():
            case '1': area_cliente(dados)
            case '2': area_guincheiro(dados)
            case '3': area_administrador(dados)
            case '0':
                print('Programa encerrado. Até logo!')
                return
            case _: print('Opção inválida.')


if __name__ == '__main__':
    main()
