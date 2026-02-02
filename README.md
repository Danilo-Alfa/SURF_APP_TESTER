# Surf App Tester Platform

Plataforma de Testes de Qualidade (Quality Gate) para Aplicativos Android com análise estática (SAST), dinâmica (DAST) e geração de relatórios PDF.

---

## Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads/)
- **pip** - Gerenciador de pacotes Python (incluído com Python)

### Para testes em dispositivo físico (opcional)

- **Appium Server** - Para automação de testes mobile
- **Android SDK** - Para comunicação com dispositivos Android
- **Dispositivo Android** conectado via USB com modo desenvolvedor ativado

---

## Passo a Passo

### 1. Clonar o Repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd SURF_APP_TESTER
```

### 2. Criar Ambiente Virtual (Recomendado)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

As principais dependências instaladas são:

| Pacote | Função |
|--------|--------|
| fastapi | Framework web de alto desempenho |
| uvicorn | Servidor ASGI |
| androguard | Análise estática de APK |
| pytest | Framework de testes |
| reportlab | Geração de relatórios PDF |
| appium-python-client | Automação de testes mobile |

### 4. Executar o Servidor

```bash
python -m app.main
```

**Saída esperada:**
```
🚀 Iniciando Surf App Tester Platform...
📱 Front-end disponível em: http://localhost:8000
📚 API docs disponível em: http://localhost:8000/docs
```

### 5. Acessar a Aplicação

Abra o navegador e acesse:

- **Interface Web:** http://localhost:8000
- **Documentação da API:** http://localhost:8000/docs

---

## Como Usar

### Via Interface Web

1. Acesse http://localhost:8000
2. Arraste ou selecione um arquivo APK para upload
3. Aguarde a análise estática e dinâmica
4. Visualize o resultado do Quality Gate (Aprovado/Reprovado)
5. Baixe o relatório PDF gerado

### Via API

**Upload e Teste Completo:**
```bash
curl -X POST http://localhost:8000/executar-teste-apk \
  -F "file=@seu_app.apk"
```

**Verificar Status do Sistema:**
```bash
curl http://localhost:8000/api/system-status
```

**Ver Última Análise:**
```bash
curl http://localhost:8000/api/last-analysis
```

---

## Executar Testes

### Testes Simulados (Desenvolvimento)
```bash
pytest tests_repo --junitxml=resultado_real.xml
```

### Testes em Dispositivo Físico (Requer Appium)
```bash
pytest tests_mobile --junitxml=resultado_real.xml
```

---

## Estrutura do Projeto

```
SURF_APP_TESTER/
├── app/                        # Backend FastAPI
│   ├── main.py                 # Aplicação principal
│   ├── core/
│   │   └── quality_gate.py     # Lógica de aprovação/reprovação
│   ├── models/
│   │   └── schemas.py          # Schemas Pydantic
│   └── services/
│       ├── apk_analyzer.py     # Análise estática de APK
│       ├── test_runner.py      # Executor de testes
│       └── pdf_reporter.py     # Gerador de relatórios PDF
├── frontend/
│   └── index.html              # Interface React
├── tests_mobile/
│   └── test_android_apk.py     # Testes com Appium
├── tests_repo/
│   └── test_simulacao.py       # Testes simulados
├── storage/                    # APKs e PDFs gerados
├── requirements.txt            # Dependências
└── README.md                   # Este arquivo
```

---

## Critérios do Quality Gate

O aplicativo é **REPROVADO** automaticamente se:

| Critério | Limite |
|----------|--------|
| Taxa de execução dos testes | < 100% |
| Taxa de aprovação | < 90% |
| Defeitos críticos (S1) | > 0 |
| Defeitos médios (S2) | > 5 |
| Concentração de falhas por área | > 5% |

---

## Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Interface web |
| GET | `/api/system-status` | Status dos serviços |
| GET | `/api/stats` | Estatísticas dos testes |
| POST | `/executar-teste-apk` | Ciclo completo de teste |
| POST | `/api/upload-apk` | Upload de APK |
| GET | `/api/analysis-status/{filename}` | Status da análise |
| GET | `/api/last-analysis` | Última análise realizada |

---

## Solução de Problemas

### Erro: "No module named 'app'"
Certifique-se de estar no diretório raiz do projeto e execute com:
```bash
python -m app.main
```

### Erro: "Port 8000 already in use"
Encerre o processo que está usando a porta ou altere a porta no arquivo `app/main.py`.

### Erro ao instalar androguard
No Windows, pode ser necessário instalar o Visual C++ Build Tools:
```bash
pip install --upgrade pip setuptools wheel
pip install androguard
```

---

## Tecnologias Utilizadas

- **Backend:** Python 3, FastAPI, Uvicorn
- **Frontend:** React 18 (SPA)
- **Análise de APK:** Androguard
- **Testes:** Pytest, Appium
- **Relatórios:** ReportLab (PDF)

---

## Licença

Este projeto é de uso interno.
