#!/usr/bin/env python3
"""Script para verificar se a persistência do Qdrant está funcionando corretamente."""

import os
import sys
from pathlib import Path

def verify_volume_setup():
    """Verifica se o volume do Qdrant está configurado corretamente."""
    
    volume_path = Path(__file__).parent.parent / "volumes" / "qdrant"
    
    print(f"{'='*80}")
    print(f"🔍 VERIFICAÇÃO DE PERSISTÊNCIA DO QDRANT")
    print(f"{'='*80}\n")
    
    # 1. Verificar se a pasta existe
    print(f"1️⃣ Verificando pasta do volume...")
    if volume_path.exists():
        print(f"   ✅ Pasta existe: {volume_path}")
    else:
        print(f"   ❌ Pasta não existe: {volume_path}")
        print(f"   🔧 Criando pasta...")
        volume_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Pasta criada")
    
    # 2. Verificar permissões
    print(f"\n2️⃣ Verificando permissões...")
    if os.access(volume_path, os.W_OK):
        print(f"   ✅ Permissão de escrita: OK")
    else:
        print(f"   ❌ Sem permissão de escrita!")
        print(f"   💡 Execute: chmod -R 755 {volume_path}")
    
    # 3. Verificar conteúdo
    print(f"\n3️⃣ Verificando conteúdo do volume...")
    files = list(volume_path.rglob("*"))
    if files:
        print(f"   ✅ {len(files)} arquivos/pastas encontrados")
        print(f"   📁 Estrutura:")
        for item in sorted(volume_path.iterdir())[:10]:  # Mostrar primeiros 10
            size = ""
            if item.is_file():
                size = f" ({item.stat().st_size} bytes)"
            print(f"      - {item.name}{size}")
        if len(files) > 10:
            print(f"      ... e mais {len(files) - 10} itens")
    else:
        print(f"   ⚠️  Volume vazio (normal se for a primeira vez)")
    
    # 4. Verificar conexão com Qdrant
    print(f"\n4️⃣ Verificando conexão com Qdrant...")
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from src.vector_store import QdrantVectorStore
        
        vector_store = QdrantVectorStore()
        collections = vector_store.list_collections()
        
        print(f"   ✅ Conectado ao Qdrant")
        print(f"   📊 Collections encontradas: {len(collections)}")
        
        if collections:
            print(f"   📋 Lista de collections:")
            for col in collections:
                doc_count = col.get('document_count', 0)
                chunk_count = col.get('chunk_count', 0)
                print(f"      - {col['name']}: {doc_count} documentos, {chunk_count} chunks")
        else:
            print(f"   ⚠️  Nenhuma collection encontrada")
    
    except Exception as e:
        print(f"   ❌ Erro ao conectar: {e}")
        print(f"   💡 Certifique-se de que o Qdrant está rodando: docker-compose up -d qdrant")
    
    # 5. Recomendações
    print(f"\n5️⃣ Recomendações:")
    print(f"   ✅ Use 'docker-compose down' SEM a flag '-v'")
    print(f"   ✅ Faça backup regular: python scripts/backup_qdrant_collections.py")
    print(f"   ✅ Verifique o arquivo PERSISTENCIA_QDRANT.md para mais detalhes")
    
    print(f"\n{'='*80}")
    print(f"✅ Verificação concluída!")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    verify_volume_setup()

