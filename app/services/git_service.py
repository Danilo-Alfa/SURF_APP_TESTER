# Arquivo: app/services/git_service.py
import os
import shutil
from git import Repo

class GitService:
    @staticmethod
    def preparar_repositorio(url: str, branch: str = "main") -> str:
        """
        Clona o repositório ou atualiza se já existir.
        Retorna o caminho da pasta onde o código está.
        """
        # Define uma pasta temporária segura
        nome_pasta = url.split("/")[-1].replace(".git", "")
        caminho_destino = os.path.join("storage", "repos", nome_pasta)
        
        # Se a pasta já existe, removemos para garantir um clone limpo (fresh start)
        # Em produção real, poderíamos fazer apenas um 'git pull' para ser mais rápido.
        if os.path.exists(caminho_destino):
            try:
                shutil.rmtree(caminho_destino)
            except PermissionError:
                print("Aviso: Não foi possível limpar a pasta antiga. Tentando usar a existente.")

        print(f"--- Clonando repositório: {url} (Branch: {branch}) ---")
        try:
            Repo.clone_from(url, caminho_destino, branch=branch)
            print("Clone realizado com sucesso!")
            return caminho_destino
        except Exception as e:
            print(f"Erro crítico ao clonar git: {e}")
            raise e