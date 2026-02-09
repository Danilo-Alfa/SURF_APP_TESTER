# Arquivo: app/services/apk_analyzer.py
from androguard.core.apk import APK
from androguard.core.dex import DEX
from typing import Dict
import re

class ApkAnalyzer:
    @staticmethod
    def analisar_codigo(caminho_apk: str) -> Dict:
        """
        Realiza engenharia reversa no APK para validar segurança e qualidade.
        Versão Robusta: Trata erros individualmente para não quebrar a execução.
        """
        print(f"--- Iniciando Análise Estática (SAST) no APK: {caminho_apk} ---")
        
        # Inicializa estrutura do relatório com valores padrão
        relatorio_tecnico = {
            "app_name": "Desconhecido",
            "package": "Desconhecido",
            "version_code": "Desconhecido",
            "falhas_encontradas": []
        }

        try:
            apk = APK(caminho_apk)
        except Exception as e:
            print(f"ERRO CRÍTICO ao ler APK: {e}")
            return {"erro": f"Arquivo APK inválido ou corrompido: {str(e)}"}

        # 1. Extração de Metadados (Com proteção)
        try:
            relatorio_tecnico["app_name"] = apk.get_app_name() or "Nome não encontrado"
            relatorio_tecnico["package"] = apk.get_package() or "Pacote não encontrado"
            relatorio_tecnico["version_code"] = apk.get_androidversion_code() or "Versão desconhecida"
        except Exception as e:
            print(f"Aviso: Falha ao extrair metadados básicos: {e}")

        # 2. Validação de Manifesto (Configurações Técnicas)
        
        # VERIFICAÇÃO 1: Debuggable
        try:
            if apk.is_debuggable():
                relatorio_tecnico["falhas_encontradas"].append({
                    "tipo": "SEGURANÇA",
                    "severidade": "S1",
                    "mensagem": "O APK está com 'android:debuggable=true'. Permite engenharia reversa trivial."
                })
        except Exception as e:
            print(f"Erro ao verificar debuggable: {e}")

        # VERIFICAÇÃO 2: Permissões
        try:
            permissoes = apk.get_permissions() or []
            permissoes_perigosas = ["android.permission.READ_SMS", "android.permission.SEND_SMS", "android.permission.SYSTEM_ALERT_WINDOW", "android.permission.ACCESS_FINE_LOCATION"]
            for p in permissoes:
                if any(perigosa in p for perigosa in permissoes_perigosas):
                    relatorio_tecnico["falhas_encontradas"].append({
                        "tipo": "PRIVACIDADE",
                        "severidade": "S2",
                        "mensagem": f"Permissão perigosa detectada: {p}"
                    })
        except Exception as e:
            print(f"Erro ao verificar permissões: {e}")

        # VERIFICAÇÃO 3: Tráfego Cleartext (HTTP)
        try:
            # Tenta pegar atributo direto, se falhar, tenta via XML
            uses_cleartext = apk.get_element("application", "android:usesCleartextTraffic")
            if uses_cleartext and str(uses_cleartext).lower() == "true":
                 relatorio_tecnico["falhas_encontradas"].append({
                    "tipo": "SEGURANÇA",
                    "severidade": "S2",
                    "mensagem": "O App permite tráfego HTTP não criptografado (Cleartext Traffic)."
                })
        except Exception:
            pass # Atributo não encontrado geralmente significa que está seguro (false por padrão em APIs novas)

        # 3. Validação de Código Fonte (DEX)
        print("Escaneando código fonte extraído (DEX)...")
        patterns = {
            "Google API Key": r"AIza[0-9A-Za-z-_]{35}",
            "Generic API Key": r"(?i)apikey\s*=\s*['\"][a-zA-Z0-9_]{10,}['\"]",
            "AWS Access Key": r"AKIA[0-9A-Z]{16}"
        }

        try:
            dex_content_generator = apk.get_all_dex()
            for dex_bytes in dex_content_generator:
                try:
                    d = DEX(dex_bytes)
                    for s_obj in d.get_strings():
                        # Converte para string com segurança
                        try:
                            string_val = str(s_obj)
                        except:
                            continue # Pula strings binárias/ilegíveis

                        for nome_padrao, regex in patterns.items():
                            if len(string_val) < 200 and re.search(regex, string_val): # Limita tamanho para performance
                                relatorio_tecnico["falhas_encontradas"].append({
                                    "tipo": "VAZAMENTO DE DADOS",
                                    "severidade": "S1",
                                    "mensagem": f"{nome_padrao} encontrada exposta no código."
                                })
                                break # Achou uma ocorrência nessa string, vai para a próxima
                except Exception as dex_err:
                    print(f"Aviso: Erro ao processar um arquivo DEX específico: {dex_err}")
                    continue
        except Exception as e:
            print(f"Erro geral na análise DEX: {e}")

        return relatorio_tecnico