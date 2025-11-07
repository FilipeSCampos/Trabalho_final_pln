#!/usr/bin/env python3
"""Script para fazer backup das collections do Qdrant antes de desligar o Docker."""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Adicionar o diretório raiz ao path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_store import QdrantVectorStore

def backup_collections(output_dir: str = None) -> str:
    """Faz backup de todas as collections do Qdrant."""
    
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "backups" / "qdrant"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Criar nome do arquivo com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = output_dir / f"qdrant_backup_{timestamp}.json"
    
    print(f"🔍 Conectando ao Qdrant...")
    vector_store = QdrantVectorStore()
    
    print(f"📋 Listando collections...")
    collections = vector_store.list_collections()
    
    if not collections:
        print("⚠️  Nenhuma collection encontrada!")
        return None
    
    backup_data = {
        "timestamp": timestamp,
        "datetime": datetime.now().isoformat(),
        "collections_count": len(collections),
        "collections": []
    }
    
    print(f"💾 Fazendo backup de {len(collections)} collections...")
    
    for collection in collections:
        collection_name = collection['name']
        print(f"  📦 Backup da collection: {collection_name}")
        
        try:
            # Listar documentos da collection
            documents = vector_store.list_collection_documents(collection_name, limit=10000)
            
            collection_data = {
                "name": collection_name,
                "embedding_model": collection.get('embedding_model', 'unknown'),
                "description": collection.get('description', ''),
                "document_count": collection.get('document_count', 0),
                "chunk_count": collection.get('chunk_count', 0),
                "documents": documents
            }
            
            backup_data["collections"].append(collection_data)
            print(f"    ✅ {len(documents)} documentos salvos")
            
        except Exception as e:
            print(f"    ❌ Erro ao fazer backup da collection {collection_name}: {e}")
            collection_data = {
                "name": collection_name,
                "error": str(e),
                "documents": []
            }
            backup_data["collections"].append(collection_data)
    
    # Salvar backup
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Backup concluído!")
    print(f"📄 Arquivo salvo em: {backup_file}")
    print(f"📊 Total: {len(collections)} collections, {sum(c.get('document_count', 0) for c in collections)} documentos")
    
    return str(backup_file)


def main():
    """Função principal do script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Fazer backup das collections do Qdrant'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Diretório para salvar o backup (padrão: backups/qdrant)'
    )
    
    args = parser.parse_args()
    
    print(f"{'='*80}")
    print(f"💾 BACKUP DAS COLLECTIONS DO QDRANT")
    print(f"{'='*80}\n")
    
    try:
        backup_file = backup_collections(args.output_dir)
        
        if backup_file:
            print(f"\n{'='*80}")
            print(f"✅ BACKUP CONCLUÍDO COM SUCESSO!")
            print(f"{'='*80}")
            print(f"\n💡 Para restaurar, use o script restore_qdrant_backup.py")
        else:
            sys.exit(1)
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️ Backup interrompido pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro fatal: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

