#!/usr/bin/env python3
"""Script para recriar collections corrompidas do zero."""

import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_store import QdrantVectorStore
from src.config import get_config

config = get_config()


def force_delete_all_cozinha_collections():
    """Força a deleção de todas as collections de cozinha usando múltiplos métodos."""
    
    print(f"{'='*80}")
    print(f"🗑️  LIMPEZA FORÇADA DE COLLECTIONS")
    print(f"{'='*80}\n")
    
    vector_store = QdrantVectorStore()
    
    # Lista conhecida de collections de cozinha
    known_collections = [
        'cozinha_americana', 'cozinha_angolana', 'cozinha_arabe', 'cozinha_belga',
        'cozinha_chinesa', 'cozinha_do_caucaso', 'cozinha_eslava', 'cozinha_eslovaca',
        'cozinha_finlandesa', 'cozinha_gabonesa', 'cozinha_irlandesa', 'cozinha_israelense',
        'cozinha_luxemburguesa', 'cozinha_maltesa', 'cozinha_portuguesa', 'cozinha_romena',
        'cozinha_suica', 'cozinha_turca'
    ]
    
    deleted_count = 0
    
    for collection_name in known_collections:
        print(f"🗑️  Tentando deletar: {collection_name}")
        
        # Método 1: Via vector_store
        try:
            vector_store.delete_collection(collection_name)
            print(f"  ✅ Deletada (método padrão)")
            deleted_count += 1
            continue
        except:
            pass
        
        # Método 2: Via client direto
        try:
            vector_store._ensure_connection()
            vector_store.client.delete_collection(collection_name)
            print(f"  ✅ Deletada (método direto)")
            deleted_count += 1
            continue
        except:
            pass
        
        # Método 3: Via HTTP
        try:
            import requests
            qdrant_url = f"http://{config.QDRANT_HOST}:{config.QDRANT_PORT}"
            headers = {}
            if config.QDRANT_API_KEY:
                headers['api-key'] = config.QDRANT_API_KEY
            
            response = requests.delete(
                f"{qdrant_url}/collections/{collection_name}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 404]:
                print(f"  ✅ Deletada (método HTTP)")
                deleted_count += 1
                continue
        except:
            pass
        
        print(f"  ⚠️  Não foi possível deletar (pode não existir)")
    
    print(f"\n✅ {deleted_count} collections processadas")
    print(f"\n💡 Se ainda houver problemas, reinicie o Qdrant:")
    print(f"   docker-compose restart qdrant")
    print(f"   ou")
    print(f"   docker-compose down && rm -rf volumes/qdrant/* && docker-compose up -d")


if __name__ == '__main__':
    force_delete_all_cozinha_collections()

