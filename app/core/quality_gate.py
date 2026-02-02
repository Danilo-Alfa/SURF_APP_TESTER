# Arquivo: app/core/quality_gate.py
from typing import Dict, List, Tuple

class QualityGateEvaluator:
    @staticmethod
    def avaliar_e2e_para_uat(
        total: int, exec: int, aprovados: int, 
        s1: int, s2: int, areas: Dict[str, int]
    ) -> Tuple[bool, List[str]]:
        
        motivos = []
        
        # Cálculos
        perc_execucao = (exec / total * 100) if total > 0 else 0
        perc_aprovacao = (aprovados / exec * 100) if exec > 0 else 0
        
        # Regras da Imagem (E2E > UAT)
        if perc_execucao < 100:
            motivos.append(f"Execução incompleta: {perc_execucao:.1f}% (Meta: 100%)")
            
        if perc_aprovacao < 90:
            motivos.append(f"Aprovação baixa: {perc_aprovacao:.1f}% (Meta: 90%)")
            
        if s1 > 0:
            motivos.append(f"BLOQUEANTE: {s1} defeitos Críticos (S1) encontrados.")
            
        if s2 > 5:
            motivos.append(f"Excesso de defeitos Médios (S2): {s2} (Máx: 5)")
            
        # Regra de concentração (5%)
        limite = total * 0.05
        for area, qtd in areas.items():
            if qtd > limite:
                motivos.append(f"Concentração de falhas na área '{area}': {qtd} (Limite: {limite:.1f})")

        aprovado = len(motivos) == 0
        return aprovado, motivos