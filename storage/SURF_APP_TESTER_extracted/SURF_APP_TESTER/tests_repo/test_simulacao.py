# Arquivo: tests_repo/test_simulacao.py
import pytest

# Simula um teste de Login que PASSA
def test_login_sucesso():
    assert 1 + 1 == 2

# Simula um teste de Checkout que FALHA (Defeito S1 - Crítico)
# O nome do teste contém "_S1_", que nosso parser vai detectar.
def test_checkout_S1_falha_critica():
    print("Tentando finalizar compra...")
    # Forçamos a falha para simular o bug
    assert False, "Erro Crítico: O botão de pagar não funciona!"

# Simula um teste de Perfil que FALHA (Defeito S2 - Médio)
def test_perfil_S2_falha_layout():
    # Forçamos falha
    assert "texto" == "imagem", "Erro Visual: Texto desalinhado"

# Simula mais testes passando para dar volume
def test_busca_produto():
    assert True

def test_filtro_categoria():
    assert True