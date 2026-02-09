# Arquivo: app/main.py
import shutil
import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.models.schemas import ExecutionRequest, TestResultInput, QualityGateResponse, FaseTeste
from app.services.test_runner import TestRunner
from app.core.quality_gate import QualityGateEvaluator
from app.services.pdf_reporter import PDFReporter
from app.services.apk_analyzer import ApkAnalyzer

app = FastAPI(title="PyQualityGate Platform")

# Configurar CORS para permitir requisições do front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos do frontend
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Rota raiz para servir o index.html
@app.get("/")
async def read_root():
    """Serve a página principal do front-end"""
    frontend_path = "frontend/index.html"
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"message": "Front-end não encontrado. Crie a pasta 'frontend' e adicione o index.html"}

# Nova rota para obter status do sistema
@app.get("/api/system-status")
async def get_system_status():
    """Retorna o status atual do sistema"""
    return {
        "status": "active",
        "services": {
            "apk_analyzer": "online",
            "test_runner": "online",
            "quality_gate": "online",
            "pdf_reporter": "online"
        }
    }

# Nova rota para obter estatísticas
@app.get("/api/stats")
async def get_stats():
    """Retorna estatísticas gerais do sistema"""
    # Aqui você pode implementar lógica real para buscar do banco de dados
    return {
        "testsRun": 47,
        "passed": 44,
        "failed": 3,
        "coverage": 87
    }

@app.post("/executar-teste-apk")
async def upload_e_testar(
    arquivo: UploadFile = File(...),
    fase: str = Form("E2E")
):
    """
    Endpoint principal que realiza o ciclo completo:
    1. Upload do APK
    2. Análise Estática de Código (Segurança)
    3. Testes Dinâmicos (Simulação)
    4. Quality Gate (Aprovação/Reprovação)
    5. Geração de PDF
    """
    
    # 1. SALVAR O APK
    os.makedirs("storage", exist_ok=True)
    caminho_apk = os.path.join("storage", arquivo.filename)
    
    with open(caminho_apk, "wb") as buffer:
        shutil.copyfileobj(arquivo.file, buffer)
    
    print(f"APK recebido e salvo em: {caminho_apk}")
    
    # --- NOVA ETAPA: ANÁLISE ESTÁTICA DO CÓDIGO (SAST) ---
    print("Iniciando Análise de Código e Segurança...")
    resultado_codigo = ApkAnalyzer.analisar_codigo(caminho_apk)
    
    # Extrai falhas do código para somar no Quality Gate
    falhas_codigo = resultado_codigo.get("falhas_encontradas", [])
    s1_codigo = sum(1 for f in falhas_codigo if f['severidade'] == 'S1')
    s2_codigo = sum(1 for f in falhas_codigo if f['severidade'] == 'S2')
    
    print(f"Análise de Código concluída. S1: {s1_codigo}, S2: {s2_codigo}")

    # 2. CONFIGURAR AMBIENTE E RODAR TESTES DINÂMICOS (DAST)
    os.environ["TARGET_APK_PATH"] = os.path.abspath(caminho_apk)
    caminho_testes = "tests_mobile" 
    
    # Rodamos o TestRunner
    resultados_testes = TestRunner.executar_testes(caminho_testes)
    
    if not resultados_testes:
        # Fallback se o teste falhar em gerar XML
        resultados_testes = {
            "total_testes": 0, "executados": 0, "aprovados": 0,
            "defeitos_s1": 0, "defeitos_s2": 0, "falhas_por_area": {}
        }

    # 3. UNIFICAR OS RESULTADOS (CÓDIGO + TESTES)
    total_s1 = resultados_testes['defeitos_s1'] + s1_codigo
    total_s2 = resultados_testes['defeitos_s2'] + s2_codigo
    
    # Adiciona as falhas de código na lista de "motivos" do Quality Gate
    motivos_codigo = [f"[CÓDIGO] {f['mensagem']}" for f in falhas_codigo]

    # 4. QUALITY GATE & RELATÓRIO
    aprovado, motivos_gate = QualityGateEvaluator.avaliar_e2e_para_uat(
        resultados_testes['total_testes'], 
        resultados_testes['executados'], 
        resultados_testes['aprovados'],
        total_s1, # Soma total de defeitos críticos
        total_s2, 
        resultados_testes['falhas_por_area']
    )
    
    # Junta todos os motivos
    todos_motivos = motivos_codigo + motivos_gate
    
    # Garante reprovação se houver falha de código crítica
    if s1_codigo > 0:
        aprovado = False

    pdf = PDFReporter.gerar(resultados_testes, aprovado, todos_motivos, fase)

    return {
        "arquivo": arquivo.filename,
        "analise_estatica": {
            "debuggable": "Sim (FALHA)" if s1_codigo > 0 else "Não (OK)",
            "falhas_identificadas": falhas_codigo
        },
        "analise_dinamica": resultados_testes,
        "status_final": "APROVADO" if aprovado else "REPROVADO",
        "relatorio_pdf": pdf
    }

# Rota alternativa compatível com o front-end
@app.post("/api/upload-apk")
async def upload_apk_api(arquivo: UploadFile = File(...)):
    """
    Endpoint simplificado para upload de APK via front-end
    Retorna resposta em formato JSON adequado para a interface
    """
    try:
        # Salvar o APK
        os.makedirs("storage", exist_ok=True)
        caminho_apk = os.path.join("storage", arquivo.filename)
        
        with open(caminho_apk, "wb") as buffer:
            shutil.copyfileobj(arquivo.file, buffer)
        
        file_size = os.path.getsize(caminho_apk)
        file_size_mb = round(file_size / (1024 * 1024), 2)
        
        return JSONResponse({
            "success": True,
            "message": "APK uploaded successfully",
            "filename": arquivo.filename,
            "size": f"{file_size_mb} MB",
            "path": caminho_apk
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error uploading APK: {str(e)}"
            }
        )

# Rota para obter status da análise em tempo real
@app.get("/api/analysis-status/{filename}")
async def get_analysis_status(filename: str):
    """
    Retorna o status atual da análise de um APK específico
    """
    # Aqui você pode implementar lógica para verificar o progresso real
    # Por enquanto, retorna um exemplo
    return {
        "filename": filename,
        "analyses": [
            {
                "name": "SAST Analysis",
                "status": "completed",
                "progress": 100,
                "service": "apk_analyzer.py"
            },
            {
                "name": "Mobile Tests",
                "status": "running",
                "progress": 65,
                "service": "test_runner.py"
            },
            {
                "name": "Quality Gate",
                "status": "pending",
                "progress": 0,
                "service": "quality_gate.py"
            }
        ]
    }

# Bloco para iniciar via 'python -m app.main'
if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando Surf App Tester Platform...")
    print("📱 Front-end disponível em: http://localhost:8000")
    print("📚 API docs disponível em: http://localhost:8000/docs")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)