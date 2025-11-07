#!/usr/bin/env python3
"""Script para detectar e corrigir collections corrompidas no Qdrant."""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Adicionar o diretório raiz ao path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_store import QdrantVectorStore
from src.config import get_config

config = get_config()


def check_collection_health(vector_store: QdrantVectorStore, collection_name: str) -> Dict[str, Any]:
    """Verifica a saúde de uma collection."""
    result = {
        'name': collection_name,
        'healthy': False,
        'error': None,
        'can_delete': False
    }
    
    try:
        # Tentar obter metadata
        try:
            metadata = vector_store._get_collection_metadata(collection_name)
            if metadata:
                result['metadata'] = metadata
        except Exception as e:
            result['error'] = f"Erro ao obter metadata: {str(e)[:200]}"
            result['can_delete'] = True
            return result
        
        # Tentar contar documentos
        try:
            counts = vector_store._get_real_document_count(collection_name)
            result['document_count'] = counts.get('documents', 0)
            result['chunk_count'] = counts.get('chunks', 0)
        except Exception as e:
            result['error'] = f"Erro ao contar documentos: {str(e)[:200]}"
            result['can_delete'] = True
            return result
        
        # Se chegou aqui, a collection está saudável
        result['healthy'] = True
        return result
        
    except Exception as e:
        result['error'] = f"Erro geral: {str(e)[:200]}"
        result['can_delete'] = True
        return result


def delete_corrupted_collection(vector_store: QdrantVectorStore, collection_name: str) -> bool:
    """Tenta deletar uma collection corrompida usando métodos diferentes."""
    try:
        # Método 1: Usar o método padrão
        try:
            vector_store.delete_collection(collection_name)
            print(f"  ✅ Collection '{collection_name}' deletada (método padrão)")
            return True
        except Exception as e1:
            print(f"  ⚠️  Método padrão falhou: {str(e1)[:200]}")
            
            # Método 2: Deletar diretamente via client
            try:
                vector_store._ensure_connection()
                vector_store.client.delete_collection(collection_name)
                print(f"  ✅ Collection '{collection_name}' deletada (método direto)")
                return True
            except Exception as e2:
                print(f"  ⚠️  Método direto falhou: {str(e2)[:200]}")
                
                # Método 3: Tentar deletar via API HTTP direta
                try:
                    import requests
                    qdrant_url = f"http://{config.QDRANT_HOST}:{config.QDRANT_PORT}"
                    headers = {}
                    if config.QDRANT_API_KEY:
                        headers['api-key'] = config.QDRANT_API_KEY
                    
                    response = requests.delete(
                        f"{qdrant_url}/collections/{collection_name}",
                        headers=headers,
                        timeout=30
                    )
                    
                    if response.status_code in [200, 404]:
                        print(f"  ✅ Collection '{collection_name}' deletada (método HTTP)")
                        return True
                    else:
                        print(f"  ⚠️  Método HTTP retornou: {response.status_code}")
                        return False
                except Exception as e3:
                    print(f"  ❌ Método HTTP falhou: {str(e3)[:200]}")
                    return False
    
    except Exception as e:
        print(f"  ❌ Erro ao deletar collection '{collection_name}': {e}")
        return False


def fix_corrupted_collections(force_recreate_all: bool = False):
    """Detecta e corrige collections corrompidas."""
    
    print(f"{'='*80}")
    print(f"🔧 CORREÇÃO DE COLLECTIONS CORROMPIDAS")
    print(f"{'='*80}\n")
    
    vector_store = QdrantVectorStore()
    
    # Listar todas as collections
    print("🔍 Listando todas as collections...")
    try:
        all_collections = vector_store.list_collections()
        print(f"✅ {len(all_collections)} collections encontradas\n")
    except Exception as e:
        print(f"❌ Erro ao listar collections: {e}")
        print(f"💡 Tentando limpar volume do Qdrant...")
        print(f"   Execute: docker-compose down && rm -rf volumes/qdrant/* && docker-compose up -d")
        return
    
    # Filtrar apenas collections de cozinha
    cozinha_collections = [
        c for c in all_collections 
        if c['name'].startswith('cozinha_')
    ]
    
    if not cozinha_collections:
        print("ℹ️  Nenhuma collection de cozinha encontrada")
        return
    
    print(f"📋 Verificando {len(cozinha_collections)} collections de cozinha...\n")
    
    # Verificar saúde de cada collection
    corrupted = []
    healthy = []
    
    for collection in cozinha_collections:
        collection_name = collection['name']
        print(f"🔍 Verificando: {collection_name}")
        
        health = check_collection_health(vector_store, collection_name)
        
        if health['healthy']:
            print(f"  ✅ Saudável: {health.get('document_count', 0)} documentos, {health.get('chunk_count', 0)} chunks")
            healthy.append(collection_name)
        else:
            print(f"  ❌ CORROMPIDA: {health.get('error', 'Erro desconhecido')}")
            corrupted.append({
                'name': collection_name,
                'error': health.get('error', 'Erro desconhecido'),
                'can_delete': health.get('can_delete', False)
            })
    
    print(f"\n{'='*80}")
    print(f"📊 RESUMO")
    print(f"{'='*80}")
    print(f"✅ Collections saudáveis: {len(healthy)}")
    print(f"❌ Collections corrompidas: {len(corrupted)}")
    
    if not corrupted and not force_recreate_all:
        print(f"\n✅ Todas as collections estão saudáveis!")
        return
    
    # Deletar collections corrompidas
    if corrupted or force_recreate_all:
        print(f"\n{'='*80}")
        print(f"🗑️  DELETANDO COLLECTIONS")
        print(f"{'='*80}")
        
        collections_to_delete = [c['name'] for c in corrupted] if not force_recreate_all else [c['name'] for c in cozinha_collections]
        
        deleted_count = 0
        failed_count = 0
        
        for collection_name in collections_to_delete:
            print(f"\n🗑️  Deletando: {collection_name}")
            if delete_corrupted_collection(vector_store, collection_name):
                deleted_count += 1
            else:
                failed_count += 1
                print(f"  ⚠️  Não foi possível deletar '{collection_name}' automaticamente")
                print(f"  💡 Tente deletar manualmente via API ou reinicie o Qdrant")
        
        print(f"\n{'='*80}")
        print(f"📊 RESULTADO DA LIMPEZA")
        print(f"{'='*80}")
        print(f"✅ Deletadas: {deleted_count}")
        print(f"❌ Falhas: {failed_count}")
        
        if failed_count > 0:
            print(f"\n⚠️  Algumas collections não puderam ser deletadas automaticamente.")
            print(f"💡 Soluções:")
            print(f"   1. Reinicie o Qdrant: docker-compose restart qdrant")
            print(f"   2. Limpe o volume: docker-compose down && rm -rf volumes/qdrant/* && docker-compose up -d")
            print(f"   3. Execute este script novamente após reiniciar")
        else:
            print(f"\n✅ Todas as collections corrompidas foram deletadas!")
            print(f"💡 Execute 'python scripts/setup_cozinhas.py' para recriar as collections")


def main():
    """Função principal do script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Detectar e corrigir collections corrompidas no Qdrant'
    )
    parser.add_argument(
        '--force-recreate-all',
        action='store_true',
        help='Forçar recriação de todas as collections de cozinha (deleta todas)'
    )
    
    args = parser.parse_args()
    
    try:
        fix_corrupted_collections(force_recreate_all=args.force_recreate_all)
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️ Processo interrompido pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro fatal: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

