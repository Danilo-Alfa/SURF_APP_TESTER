import os
import pytest
import xml.etree.ElementTree as ET

class TestRunner:
    @staticmethod
    def executar_testes(caminho_testes: str) -> dict:
        """
        Executa os testes com Pytest e analisa o XML de resultados.
        Retorna um dicionário com métricas e detalhes das falhas.
        """
        # Define onde salvar o XML
        os.makedirs("storage", exist_ok=True)
        arquivo_xml = os.path.join("storage", "test_results.xml")
        
        # Remove XML antigo se existir para evitar leitura de cache
        if os.path.exists(arquivo_xml):
            try:
                os.remove(arquivo_xml)
            except:
                pass
            
        print(f"--- Executando testes em: {caminho_testes} ---")
        
        # Executa o Pytest gerando o relatório XML
        pytest.main([
            caminho_testes,
            "-v",
            f"--junitxml={arquivo_xml}",
            "-p", "no:warnings"
        ])
        
        return TestRunner._analisar_xml(arquivo_xml)

    @staticmethod
    def _analisar_xml(caminho_xml: str) -> dict:
        resultados = {
            "total_testes": 0, "executados": 0, "aprovados": 0, "falhas": 0,
            "defeitos_s1": 0, "defeitos_s2": 0, "falhas_por_area": {},
            "lista_falhas": [], # Lista detalhada para o PDF
            "lista_testes": [],  # Lista completa para o Frontend
            "sugestao_ia": None # Campo para IA preencher
        }
        
        if not os.path.exists(caminho_xml):
            return resultados
            
        try:
            tree = ET.parse(caminho_xml)
            root = tree.getroot()
            
            # Busca todas as suítes de teste
            testsuites = root.findall(".//testsuite") or [root]
            
            for suite in testsuites:
                resultados["total_testes"] += int(suite.attrib.get("tests", 0))
                resultados["falhas"] += int(suite.attrib.get("failures", 0)) + int(suite.attrib.get("errors", 0))
                
                for case in suite.findall("testcase"):
                    nome = case.attrib.get("name", "unnamed")
                    classe = case.attrib.get("classname", "unknown")
                    
                    # Verifica se houve falha ou erro
                    failure = case.find("failure")
                    error = case.find("error")
                    elem = failure if failure is not None else error
                    
                    status = "APROVADO"
                    msg = ""
                    detalhes = ""

                    # Captura a descrição do teste (stdout)
                    system_out = case.find("system-out")
                    descricao = "Sem descrição disponível."
                    
                    if system_out is not None and system_out.text:
                        # Procura por linhas que começam com DESC:
                        lines = system_out.text.split('\n')
                        desc_lines = [line.replace("DESC:", "").strip() for line in lines if "DESC:" in line]
                        if desc_lines:
                            descricao = " ".join(desc_lines)

                    if elem is not None:
                        status = "REPROVADO"
                        msg = elem.attrib.get("message", "Erro sem mensagem")
                        detalhes = elem.text or ""
                        severidade = "S1" if "[S1]" in msg or "S1" in nome else ("S2" if "[S2]" in msg else "S3")
                        
                        if severidade == "S1": resultados["defeitos_s1"] += 1
                        elif severidade == "S2": resultados["defeitos_s2"] += 1
                        
                        resultados["lista_falhas"].append({
                            "teste": nome, "classe": classe, "mensagem": msg,
                            "severidade": severidade, "detalhes": detalhes.strip(),
                            "descricao": descricao, # Adicionado para o relatório executivo
                            "analise_ia": "Aguardando integração com LLM..." # Placeholder
                        })
                    
                    # Adiciona à lista completa de testes para o front
                    resultados["lista_testes"].append({
                        "name": nome,
                        "classname": classe,
                        "status": status,
                        "message": msg,
                        "details": detalhes,
                        "description": descricao
                    })
            
            resultados["executados"] = resultados["total_testes"]
            resultados["aprovados"] = resultados["total_testes"] - resultados["falhas"]

            # Simulação de uma IA analisando o contexto geral (Futuro: Chamar API OpenAI/Gemini aqui)
            if resultados["falhas"] > 0:
                # Lógica Dinâmica: Gera o texto baseado nas falhas REAIS encontradas
                topicos = []
                for f in resultados["lista_falhas"]:
                    m = f['mensagem'].lower()
                    if "debug" in m: topicos.append("Segurança Crítica (Debug Ativo)")
                    elif "assinatura" in m: topicos.append("Integridade do APK (Não assinado)")
                    elif "backup" in m: topicos.append("Proteção de Dados (Backup Aberto)")
                    elif "export" in m: topicos.append("Superfície de Ataque (Activities Expostas)")
                    elif "performance" in m or "frames" in m: topicos.append("Performance (Jank/Lentidão)")
                
                # Remove duplicatas e pega os top 3
                topicos = list(set(topicos))[:3]
                resumo_falhas = ", ".join(topicos)
                
                resultados["sugestao_ia"] = (
                    f"<b>Analise Inteligente:</b> O Quality Gate reprovou o build principalmente devido a: <b>{resumo_falhas}</b>. "
                    "Recomendamos priorizar as falhas marcadas como [S1] pois bloqueiam o lançamento na loja. "
                    "Verifique o Manifesto Android para fechar as brechas de segurança identificadas."
                )
            else:
                resultados["sugestao_ia"] = "<b>Analise Inteligente:</b> Parabens! O build passou em todos os criterios de qualidade e seguranca. Pronto para UAT."

        except Exception as e:
            print(f"Erro ao analisar XML: {e}")
            
        return resultados