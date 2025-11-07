#!/usr/bin/env python3
"""Script para restaurar collections do Qdrant a partir de um backup."""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Adicionar o diretório raiz ao path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_store import QdrantVectorStore
from src.document_processor import DocumentProcessor
from src.storage import StorageManager
from langchain_core.documents import Document

def restore_collections(backup_file: str, recreate_collections: bool = True):
    """Restaura collections do Qdrant a partir de um backup."""
    
    backup_path = Path(backup_file)
    
    if not backup_path.exists():
        raise FileNotFoundError(f"Arquivo de backup não encontrado: {backup_file}")
    
    print(f"📖 Lendo backup: {backup_path}")
    with open(backup_path, 'r', encoding='utf-8') as f:
        backup_data = json.load(f)
    
    print(f"📊 Backup de {backup_data['datetime']}")
    print(f"📦 {backup_data['collections_count']} collections encontradas\n")
    
    vector_store = QdrantVectorStore()
    
    for collection_data in backup_data['collections']:
        collection_name = collection_data['name']
        
        if 'error' in collection_data:
            print(f"⚠️  Pulando {collection_name}: {collection_data['error']}")
            continue
        
        print(f"🔄 Restaurando collection: {collection_name}")
        
        try:
            # Verificar se a collection existe
            collections = vector_store.list_collections()
            collection_exists = any(c['name'] == collection_name for c in collections)
            
            if collection_exists and recreate_collections:
                print(f"  ⚠️  Collection já existe. Pulando...")
                print(f"  💡 Use --force para recriar (isso apagará dados existentes)")
                continue
            
            if not collection_exists:
                # Criar collection
                embedding_model = collection_data.get('embedding_model', 'openai')
                description = collection_data.get('description', '')
                
                print(f"  🔧 Criando collection com modelo '{embedding_model}'...")
                vector_store.create_collection(
                    collection_name=collection_name,
                    embedding_model=embedding_model,
                    description=description
                )
            
            # Restaurar documentos
            documents_data = collection_data.get('documents', [])
            
            if documents_data:
                print(f"  📄 Restaurando {len(documents_data)} documentos...")
                
                # Converter dados do backup para Documents
                all_chunks = []
                for doc_data in documents_data:
                    chunks_data = doc_data.get('chunks', [])
                    for chunk_data in chunks_data:
                        doc = Document(
                            page_content=chunk_data.get('content', ''),
                            metadata={
                                'file_name': doc_data.get('file_name', ''),
                                'chunk_index': chunk_data.get('chunk_index', 0),
                                'minio_path': doc_data.get('minio_path', ''),
                                'cozinha': doc_data.get('cozinha', ''),
                                'cozinha_type': doc_data.get('cozinha_type', '')
                            }
                        )
                        all_chunks.append(doc)
                
                if all_chunks:
                    # Inserir em lotes
                    batch_size = 100
                    for i in range(0, len(all_chunks), batch_size):
                        batch = all_chunks[i:i+batch_size]
                        vector_store.insert_documents(
                            collection_name=collection_name,
                            documents=batch
                        )
                        print(f"    ✅ Lote {i//batch_size + 1}: {len(batch)} chunks inseridos")
                
                print(f"  ✅ {collection_name} restaurada com sucesso!")
            else:
                print(f"  ⚠️  Nenhum documento para restaurar")
        
        except Exception as e:
            print(f"  ❌ Erro ao restaurar {collection_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✅ Restauração concluída!")


def main():
    """Função principal do script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Restaurar collections do Qdrant a partir de um backup'
    )
    parser.add_argument(
        'backup_file',
        type=str,
        help='Caminho do arquivo de backup JSON'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Recriar collections mesmo se já existirem (apaga dados existentes)'
    )
    
    args = parser.parse_args()
    
    print(f"{'='*80}")
    print(f"🔄 RESTAURAÇÃO DAS COLLECTIONS DO QDRANT")
    print(f"{'='*80}\n")
    
    try:
        restore_collections(args.backup_file, recreate_collections=not args.force)
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️ Restauração interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro fatal: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

