"""Testes das regras de negÃ³cio, sem bibliotecas externas."""
import tempfile
from pathlib import Path
import main


def executar_testes():
    assert main.telefone_valido('11999990000')
    assert not main.telefone_valido('123')
    assert main.prioridade(False, False, False) == 'normal'
    assert main.prioridade(True, False, False) == 'alta'
    assert main.prioridade(True, True, False) == 'critica'
    assert main.estimar_preco(100, 10, 'carro', False) == 145
    assert main.estimar_preco(100, 10, 'moto', False) == 123.25
    assert main.estimar_preco(100, 10, 'utilitario', True) == 234.9
    dados = main.vazio()
    dados['guincheiros'].append({'id': 1, 'nome': 'Teste', 'regiao': 'Centro',
        'tipo': 'carro', 'preco_base': 80, 'aprovado': True,
        'disponivel': True, 'avaliacoes': [4, 5]})
    assert len(main.disponiveis(dados, 'centro', 'carro')) == 1
    assert len(main.disponiveis(dados, 'centro', 'moto')) == 0
    assert main.media_avaliacoes(dados['guincheiros'][0]) == 4.5
    with tempfile.TemporaryDirectory() as pasta:
        original = main.ARQUIVO
        try:
            main.ARQUIVO = Path(pasta) / 'dados.json'
            assert main.salvar(dados)
            assert main.carregar() == dados
        finally:
            main.ARQUIVO = original
    # As transiÃ§Ãµes abaixo nÃ£o devem criar arquivos de dados na pasta do projeto.
    original_salvar = main.salvar
    main.salvar = lambda dados: True
    pedido = {'id': 1, 'status': 'pendente', 'proposta': None}
    dados['solicitacoes'].append(pedido)
    assert main.alterar_status(dados, pedido, 'aceito')
    assert not main.alterar_status(dados, pedido, 'concluido')
    assert main.alterar_status(dados, pedido, 'em_andamento')
    assert main.alterar_status(dados, pedido, 'concluido')
    main.salvar = original_salvar
    print('Todos os cenÃ¡rios de teste passaram.')


if __name__ == '__main__':
    executar_testes()
