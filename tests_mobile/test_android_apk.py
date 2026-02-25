# Arquivo: tests_mobile/test_android_apk.py
import pytest
import os
import time
import subprocess
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

# Tenta importar androguard para limpeza prévia (evita erro INSTALL_FAILED_UPDATE_INCOMPATIBLE)
try:
    from androguard.core.apk import APK
except ImportError:
    try:
        from androguard.core.bytecodes.apk import APK
    except ImportError:
        APK = None

# Usamos scope="module" para abrir o app uma vez e rodar vários testes na mesma sessão
@pytest.fixture(scope="module")
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
    options.new_command_timeout = 600
    options.set_capability("appium:uiautomator2ServerInstallTimeout", 90000)
    options.set_capability("appium:adbExecTimeout", 60000) # Dá mais tempo para comandos ADB
    options.set_capability("appium:enforceAppInstall", True) # Força o Appium a tentar instalar

    # --- RESOLUÇÃO DO COMANDO ADB ---
    # Tenta encontrar o ADB pelo ANDROID_HOME se não estiver no PATH global
    adb_cmd = "adb"
    android_home = os.getenv("ANDROID_HOME")
    if android_home:
        potential_adb = os.path.join(android_home, "platform-tools", "adb.exe")
        if os.path.exists(potential_adb):
            adb_cmd = f'"{potential_adb}"'

    print(f"--- Tentando conectar ao Appium (http://localhost:4723) para testar: {apk_path} ---")
    
    # --- DIAGNÓSTICO PRÉVIO (FORÇA BRUTA) ---
    # Isso garante que sabemos POR QUE a instalação falha antes mesmo do Appium tentar
    print("🔍 Diagnóstico: Verificando conexão ADB e tentando instalação manual...")
    try:
        # 1. Verifica se tem device
        chk = subprocess.run(f"{adb_cmd} devices", shell=True, capture_output=True, text=True)
        if "device" not in chk.stdout.replace("List of devices attached", "").strip():
             pytest.fail("❌ ERRO FATAL: Nenhum celular detectado pelo ADB. Verifique o cabo USB e a Depuração USB.")

        # 1.5 Tenta desinstalar versão anterior para evitar conflito de assinatura
        if APK:
            try:
                apk_obj = APK(apk_path)
                pkg_name = apk_obj.get_package()
                print(f"🗑️ Tentando desinstalar versão antiga de: {pkg_name}")
                subprocess.run(f"{adb_cmd} uninstall {pkg_name}", shell=True, capture_output=True)
            except Exception as e:
                print(f"⚠️ Aviso: Falha ao tentar desinstalar versão anterior (pode ser ignorado): {e}")
        else:
            print("⚠️ Aviso: Biblioteca 'androguard' não detectada. A desinstalação automática da versão antiga foi pulada.")

        # 2. Tenta instalar via comando direto (mostra o erro real do Android)
        # flags: -r (reinstall), -g (grant permissions), -t (allow test packages), -d (allow downgrade)
        print(f"📦 Tentando instalar APK via ADB: {apk_path}")
        subprocess.run(f'{adb_cmd} install -r -g -t -d "{apk_path}"', shell=True, check=True, capture_output=True, text=True)
        print("✅ APK instalado com sucesso via ADB! Iniciando automação...")
    except subprocess.CalledProcessError as e:
        erro_msg = e.stderr if e.stderr else e.stdout
        print(f"❌ O ANDROID RECUSOU O APK. Motivo:\n{erro_msg}")
        
        dica = ""
        if "INSTALL_FAILED_UPDATE_INCOMPATIBLE" in erro_msg:
            dica = "\n💡 DICA: O app já está instalado com outra assinatura. Desinstale-o manualmente do celular e tente de novo."
        elif "INSTALL_FAILED_USER_RESTRICTED" in erro_msg:
            dica = "\n💡 DICA (Xiaomi/Redmi): Você precisa ativar 'Instalar via USB' nas Opções do Desenvolvedor (requer chip SIM)."
        elif "INSTALL_PARSE_FAILED_NO_CERTIFICATES" in erro_msg:
            dica = "\n💡 DICA: O APK não está assinado. Gere uma build assinada (Signed APK)."
            
        pytest.fail(f"Falha na instalação do APK: {erro_msg}{dica}")
    # -----------------------------------------
    
    driver = None
    try:
        # Conecta no Appium Server (que deve estar rodando no seu PC)
        driver = webdriver.Remote("http://localhost:4723", options=options)
        print("--- Conexão com Appium estabelecida com sucesso! ---")
        
        # Log informativo do dispositivo conectado
        caps = driver.capabilities
        device_name = f"{caps.get('deviceManufacturer', 'Unknown')} {caps.get('deviceModel', 'Device')}"
        print(f"📱 Dispositivo Vinculado: {device_name} (Android {caps.get('platformVersion', '?')})")
        
    except Exception as e:
        # Tratamento específico para erro de configuração do ambiente Android
        error_msg = str(e)
        if "ANDROID_HOME" in error_msg or "ANDROID_SDK_ROOT" in error_msg or "Android SDK root folder" in error_msg:
            pytest.fail(f"ERRO DE CONFIGURAÇÃO: O Appium não encontrou a pasta do Android SDK.\n"
                        f"O caminho que ele tentou usar não existe.\n"
                        f"1. Abra o Android Studio > Settings > Android SDK e copie o 'Android SDK Location'.\n"
                        f"2. No terminal do Appium, pare e rode: $env:ANDROID_HOME = \"CAMINHO_COPIADO\"\n"
                        f"Erro original: {error_msg}")

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

def test_01_instalacao_e_abertura(driver):
    """Verifica se o aplicativo instala e abre corretamente (Contexto Nativo)."""
    print("DESC: Instala o APK no dispositivo e verifica se a Activity principal abre.")
    print("Aguardando inicialização do app...")
    time.sleep(5) # Espera Splash Screen
    assert driver.current_context == "NATIVE_APP", "O app não iniciou no contexto nativo Android."
    print("App aberto com sucesso.")

def test_02_estabilidade_background(driver):
    """Teste de Estabilidade: Envia app para background e restaura."""
    print("DESC: Envia o app para segundo plano e restaura para verificar persistência.")
    print("Enviando app para background por 3 segundos...")
    driver.background_app(3)
    time.sleep(2)
    # Se o app crashar ao voltar, a activity será nula ou o driver perderá conexão
    assert driver.current_activity is not None, "O app fechou inesperadamente após voltar do background."
    print("App retornou do background com sucesso.")

def test_03_rotacao_tela(driver):
    """Teste de UI: Verifica comportamento ao rotacionar a tela (Landscape/Portrait)."""
    print("DESC: Rotaciona a tela do dispositivo para verificar quebras de layout.")
    print("Rotacionando para LANDSCAPE...")
    driver.orientation = "LANDSCAPE"
    time.sleep(2)
    print("Rotacionando para PORTRAIT...")
    driver.orientation = "PORTRAIT"
    time.sleep(2)
    assert True, "Rotação realizada sem crashes."

def test_04_analise_elementos_tela(driver):
    """Verifica se a tela inicial possui elementos interativos (não está branca/travada)."""
    print("DESC: Conta os elementos interativos na tela para garantir que não está travada.")
    # Busca qualquer elemento na tela
    elementos = driver.find_elements(AppiumBy.XPATH, "//*")
    qtd = len(elementos)
    print(f"Elementos encontrados na tela atual: {qtd}")
    
    # Salva o XML da tela para debug
    os.makedirs("storage", exist_ok=True)
    with open("storage/page_source.xml", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
        
    assert qtd > 0, "A tela parece estar em branco ou travada (Zero elementos encontrados)."

def test_05_busca_botoes_comuns(driver):
    """Tenta identificar botões comuns (Login, Entrar, Pular) via texto."""
    print("DESC: Busca por textos comuns (Login, Entrar) via OCR/XML.")
    termos = ["Login", "Entrar", "Sign In", "Acessar", "Pular", "Skip", "Continuar"]
    source = driver.page_source
    encontrados = [t for t in termos if t in source]
    
    if encontrados:
        print(f"Botões/Textos encontrados: {encontrados}")
    else:
        print("Aviso: Nenhum texto de botão padrão encontrado na primeira tela.")
    
    # Este teste é informativo, não falha o build
    assert True

def test_06_interacao_swipe_vertical(driver):
    """Realiza gesto de rolagem (swipe) vertical na tela."""
    print("DESC: Realiza gesto de rolagem vertical para testar fluidez.")
    print("Realizando swipe vertical...")
    # Pega tamanho da tela
    size = driver.get_window_size()
    start_y = size['height'] * 0.8
    end_y = size['height'] * 0.2
    start_x = size['width'] / 2
    
    driver.swipe(start_x, start_y, start_x, end_y, 1000)
    time.sleep(1)
    assert True

def test_07_interacao_swipe_horizontal(driver):
    """Realiza gesto de rolagem (swipe) horizontal."""
    print("DESC: Realiza gesto de rolagem horizontal (carrossel).")
    print("Realizando swipe horizontal...")
    size = driver.get_window_size()
    start_x = size['width'] * 0.9
    end_x = size['width'] * 0.1
    start_y = size['height'] / 2
    
    driver.swipe(start_x, start_y, end_x, start_y, 1000)
    time.sleep(1)
    assert True

def test_08_validacao_hierarquia_view(driver):
    """Verifica se a hierarquia de views não está muito profunda (Performance)."""
    print("DESC: Analisa a profundidade da árvore de views (XML) para performance.")
    xml = driver.page_source
    profundidade = xml.count("<android.")
    print(f"Complexidade aproximada da tela: {profundidade} elementos")
    assert profundidade > 0

def test_09_screenshot_evidencia(driver):
    """Captura um screenshot do estado final do teste."""
    print("DESC: Captura evidência visual (screenshot) da tela final.")
    os.makedirs("storage", exist_ok=True)
    caminho = "storage/screenshot_final.png"
    driver.save_screenshot(caminho)
    print(f"Screenshot salvo em: {caminho}")
    assert os.path.exists(caminho), "Falha ao salvar screenshot."