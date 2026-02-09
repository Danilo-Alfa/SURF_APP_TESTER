# Arquivo: app/services/test_runner.py
import subprocess
import os
import sys  # <--- Importante adicionar isso
import xml.etree.ElementTree as ET

class TestRunner:
    @staticmethod
    def executar_testes(caminho_testes: str) -> dict:
        result_file = "resultado_real.xml"
        if os.path.exists(result_file):
            os.remove(result_file)

        # MUDANÇA AQUI: Em vez de chamar apenas "pytest", chamamos o Python atual
        # Isso garante que ele use as bibliotecas instaladas no 'venv' (como o Appium)
        cmd = [sys.executable, "-m", "pytest", caminho_testes, f"--junitxml={result_file}"]
        
        print(f"--- Disparando testes: {caminho_testes} ---")
        try:
            subprocess.run(cmd, check=False)
        except Exception as e:
            print(f"Erro crítico no subprocess: {e}")

        if not os.path.exists(result_file):
            print("ERRO: O Pytest não gerou resultados.")
            return None
            
        return TestRunner._ler_xml(result_file)

    # ... (o resto do arquivo continua igual)

    @staticmethod
    def _ler_xml(xml_path: str) -> dict:
        # ... (Mantenha a mesma função _ler_xml que já tínhamos, ela não muda)
        tree = ET.parse(xml_path)
        root = tree.getroot()
        ts = root if root.tag == 'testsuite' else root.find('testsuite')
        
        # Lógica de contagem S1/S2 igualzinha a anterior
        total = int(ts.attrib.get('tests', 0))
        failures = int(ts.attrib.get('failures', 0))
        errors = int(ts.attrib.get('errors', 0))
        skipped = int(ts.attrib.get('skipped', 0))
        
        s1 = 0; s2 = 0; areas = {}
        for case in ts.findall('testcase'):
            if case.find('failure') is not None or case.find('error') is not None:
                nome = case.attrib.get('name', '')
                classname = case.attrib.get('classname', '')
                if "S1" in nome: s1 += 1
                elif "S2" in nome: s2 += 1
                else: s2 += 1
                area = classname.split('.')[-1]
                areas[area] = areas.get(area, 0) + 1

        return {
            "total_testes": total, "executados": total - skipped,
            "aprovados": total - failures - errors - skipped,
            "defeitos_s1": s1, "defeitos_s2": s2, "falhas_por_area": areas
        }