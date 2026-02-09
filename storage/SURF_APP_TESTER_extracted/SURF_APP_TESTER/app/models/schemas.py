# Arquivo: app/models/schemas.py
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict
from enum import Enum

class FaseTeste(str, Enum):
    E2E = "E2E"
    UAT = "UAT"

class OrigemApp(str, Enum):
    APK_UPLOAD = "upload"
    GITHUB = "github"

# Dados que chegam no pedido de teste
class ExecutionRequest(BaseModel):
    fase: FaseTeste
    origem: OrigemApp
    github_url: Optional[str] = None
    github_branch: Optional[str] = "main"
    device_name: str = "Android Emulator"

# Dados simulados do resultado dos testes (input para o Gate)
class TestResultInput(BaseModel):
    total_testes: int
    executados: int
    aprovados: int
    defeitos_s1: int
    defeitos_s2: int
    falhas_por_area: Dict[str, int] # Ex: {"Login": 2, "Checkout": 1}

# Resposta final da API
class QualityGateResponse(BaseModel):
    aprovado: bool
    fase_atual: str
    proxima_fase: Optional[str]
    mensagem: str
    detalhes_reprovacao: List[str]
    report_pdf_path: str