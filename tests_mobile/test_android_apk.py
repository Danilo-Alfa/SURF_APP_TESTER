# Arquivo: tests_mobile/test_android_apk.py
import pytest
import os
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

@pytest.fixture(scope="function")
def driver():
    # 1. Pega o caminho do APK que o PyQualityGate salvou
    apk_path = os.getenv("TARGET_APK_PATH")
    
    if not apk_path:
        pytest.fail("ERRO: Caminho do APK não encontrado. Faça o upload pela plataforma primeiro.")

    # 2. Configurações para Celular Físico
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    
    # "Android Device" é genérico, serve para qualquer celular plugado no USB
    options.device_name = "Android Device" 
    
    # O APK que você fez upload será instalado no seu celular automaticamente
    options.app = apk_path
    
    # False = Reinstala o app se necessário, mas tenta manter dados
    options.no_reset = False 
    
    # Aceita permissões (Câmera, Localização) automaticamente para o teste não travar
    options.auto_grant_permissions = True
    
    # Aumenta o tempo limite de instalação (Celulares físicos as vezes demoram mais que emuladores)
    options.set_capability("appium:uiautomator2ServerInstallTimeout", 60000)

    print("--- Tentando conectar ao celular físico via USB... ---")
    
    driver = None
    try:
        # Conecta no Appium Server (que deve estar rodando no seu PC)
        driver = webdriver.Remote("http://localhost:4723", options=options)
    except Exception as e:
        pytest.fail(f"FALHA DE CONEXÃO: Não foi possível falar com o celular. \n"
                    f"1. Verifique o cabo USB.\n"
                    f"2. Verifique se a Depuração USB está ligada.\n"
                    f"3. Verifique se o Appium Server está rodando.\n"
                    f"Erro detalhado: {e}")

    yield driver # Entrega o controle do celular para o teste
    
    # Ao final, encerra a sessão
    if driver:
        driver.quit()

# --- OS TESTES (O que o celular vai fazer sozinho) ---

def test_validar_abertura_app(driver):
    """
    Teste Básico: O aplicativo abre e chega na tela nativa?
    """
    print("Verificando se o app abriu...")
    driver.implicitly_wait(10) # Espera até 10s o app carregar
    
    # Se o contexto for NATIVE_APP, o app abriu corretamente
    assert driver.current_context == "NATIVE_APP"

def test_simulacao_falha_S1(driver):
    """
    Este teste serve para testar o Quality Gate.
    Ele tenta clicar em um botão que não existe, gerando uma falha S1 (Crítica).
    """
    print("Tentando encontrar botão inexistente (Simulação de erro)...")
    try:
        # Tenta achar um ID que sabemos que não existe
        driver.find_element(AppiumBy.ID, "botao_fantasma_que_nao_existe")
    except:
        # Reporta falha S1 para a plataforma pegar
        pytest.fail("Erro Crítico (S1): Elemento vital não encontrado na tela.")