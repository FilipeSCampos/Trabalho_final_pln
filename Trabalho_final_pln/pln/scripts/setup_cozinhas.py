#!/usr/bin/env python3
"""Script para criar collections por tipo de cozinha e popular com receitas."""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

# Adicionar o diretório raiz ao path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_config
from src.document_processor import DocumentProcessor
from src.vector_store import QdrantVectorStore
from src.storage import StorageManager

config = get_config()


def normalize_collection_name(cozinha_name: str) -> str:
    """Normaliza o nome da cozinha para um nome de collection válido."""
    # Remover "Cozinha " do início se existir
    name = cozinha_name.replace("Cozinha ", "").strip()
    
    # Converter para minúsculas e substituir espaços e caracteres especiais por underscore
    name = name.lower()
    name = re.sub(r'[^\w\s-]', '', name)  # Remover caracteres especiais exceto underscore e hífen
    name = re.sub(r'[-\s]+', '_', name)  # Substituir espaços e hífens por underscore
    name = name.strip('_')  # Remover underscores no início/fim
    
    # Adicionar prefixo para garantir unicidade
    collection_name = f"cozinha_{name}"
    
    return collection_name


def get_cozinhas(receitas_dir: str) -> List[Dict[str, Any]]:
    """Retorna lista de pastas de cozinhas e seus arquivos."""
    receitas_path = Path(receitas_dir)
    
    if not receitas_path.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {receitas_dir}")
    
    cozinhas = []
    
    # Listar todas as subpastas (cozinhas)
    for item in receitas_path.iterdir():
        if item.is_dir():
            cozinha_name = item.name
            
            # Buscar arquivos .md nesta cozinha
            markdown_files = list(item.glob("*.md"))
            
            if markdown_files:
                collection_name = normalize_collection_name(cozinha_name)
                
                cozinhas.append({
                    'original_name': cozinha_name,
                    'collection_name': collection_name,
                    'folder_path': item,
                    'files': sorted(markdown_files),
                    'file_count': len(markdown_files)
                })
    
    return sorted(cozinhas, key=lambda x: x['original_name'])


def delete_all_cozinha_collections(vector_store: QdrantVectorStore) -> int:
    """Deleta todas as collections de cozinha existentes, incluindo corrompidas."""
    try:
        # Tentar listar collections - se falhar, pode ser que o Qdrant esteja com problemas
        try:
            collections = vector_store.list_collections()
        except Exception as e:
            print(f"⚠️  Erro ao listar collections: {e}")
            print(f"💡 Tentando deletar collections conhecidas diretamente...")
            # Lista de collections conhecidas baseada nas pastas
            known_collections = [
                'cozinha_americana', 'cozinha_angolana', 'cozinha_arabe', 'cozinha_belga',
                'cozinha_chinesa', 'cozinha_do_caucaso', 'cozinha_eslava', 'cozinha_eslovaca',
                'cozinha_finlandesa', 'cozinha_gabonesa', 'cozinha_irlandesa', 'cozinha_israelense',
                'cozinha_luxemburguesa', 'cozinha_maltesa', 'cozinha_portuguesa', 'cozinha_romena',
                'cozinha_suica', 'cozinha_turca'
            ]
            collections = [{'name': name} for name in known_collections]
        
        cozinha_collections = [
            c for c in collections 
            if c['name'].startswith('cozinha_')
        ]
        
        if not cozinha_collections:
            print(f"ℹ️  Nenhuma collection de cozinha encontrada para deletar")
            return 0
        
        deleted_count = 0
        failed_count = 0
        print(f"🗑️  Deletando {len(cozinha_collections)} collections de cozinha existentes...")
        
        for collection in cozinha_collections:
            collection_name = collection['name']
            try:
                # Tentar deletar usando o método padrão
                vector_store.delete_collection(collection_name)
                print(f"  ✅ Collection '{collection_name}' deletada")
                deleted_count += 1
            except Exception as e:
                error_msg = str(e)
                print(f"  ⚠️  Erro ao deletar '{collection_name}': {error_msg[:200]}")
                
                # Tentar deletar diretamente via client
                try:
                    vector_store._ensure_connection()
                    vector_store.client.delete_collection(collection_name)
                    print(f"  ✅ Collection '{collection_name}' deletada (método direto)")
                    deleted_count += 1
                except Exception as e2:
                    print(f"  ❌ Falha ao deletar '{collection_name}' mesmo com método direto")
                    failed_count += 1
        
        print(f"✅ {deleted_count} collections deletadas")
        if failed_count > 0:
            print(f"⚠️  {failed_count} collections não puderam ser deletadas")
            print(f"💡 Execute 'python scripts/fix_corrupted_collections.py' para tentar corrigir")
        
        return deleted_count
        
    except Exception as e:
        print(f"❌ Erro ao deletar collections: {e}")
        print(f"💡 Execute 'python scripts/fix_corrupted_collections.py' para tentar corrigir")
        return 0


def create_collection(vector_store: QdrantVectorStore, collection_name: str, 
                     embedding_model: str = None, description: str = "", 
                     delete_if_exists: bool = True) -> bool:
    """Cria uma collection no Qdrant. Se já existir e delete_if_exists=True, deleta e recria."""
    if embedding_model is None:
        embedding_model = config.DEFAULT_EMBEDDING_MODEL
    
    try:
        # Verificar se a collection já existe
        collections = vector_store.list_collections()
        existing_collections = [c['name'] for c in collections]
        
        if collection_name in existing_collections:
            if delete_if_exists:
                print(f"🗑️  Collection '{collection_name}' já existe, deletando...")
                try:
                    vector_store.delete_collection(collection_name)
                    print(f"  ✅ Collection '{collection_name}' deletada")
                except Exception as e:
                    print(f"  ⚠️  Erro ao deletar collection existente: {e}")
                    # Tentar continuar mesmo assim
            else:
                print(f"ℹ️  Collection '{collection_name}' já existe")
                return True
        
        # Criar nova collection
        print(f"🔧 Criando collection '{collection_name}' com modelo '{embedding_model}'...")
        vector_store.create_collection(
            collection_name=collection_name,
            embedding_model=embedding_model,
            description=description
        )
        print(f"✅ Collection '{collection_name}' criada com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar collection '{collection_name}': {e}")
        return False


def ensure_minio_folder(storage_manager: StorageManager, cozinha_name: str) -> bool:
    """Garante que a pasta da cozinha existe no MinIO."""
    try:
        # O MinIO não precisa criar pastas explicitamente, mas podemos verificar
        # se o storage está funcionando. A pasta será criada automaticamente
        # quando fizermos upload dos arquivos usando o 'topic' como prefixo.
        test_result = storage_manager.test_connection()
        
        if not test_result.get('connected', False):
            print(f"⚠️  Aviso: Storage não está conectado: {test_result.get('error', 'Erro desconhecido')}")
            return False
        
        print(f"✅ Storage conectado, pasta '{cozinha_name}' será criada automaticamente no upload")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar storage: {e}")
        return False


def process_cozinha(
    cozinha_info: Dict[str, Any],
    vector_store: QdrantVectorStore,
    document_processor: DocumentProcessor,
    storage_manager: StorageManager,
    embedding_model: str = None,
    enhance: bool = True,
    skip_existing: bool = False
) -> Dict[str, Any]:
    """Processa uma cozinha completa: cria collection, pasta MinIO e insere receitas."""
    
    cozinha_name = cozinha_info['original_name']
    collection_name = cozinha_info['collection_name']
    files = cozinha_info['files']
    
    print(f"\n{'='*80}")
    print(f"🍳 PROCESSANDO COZINHA: {cozinha_name}")
    print(f"{'='*80}")
    print(f"📁 Collection: {collection_name}")
    print(f"📄 Arquivos: {len(files)}")
    print(f"{'='*80}\n")
    
    results = {
        'cozinha': cozinha_name,
        'collection': collection_name,
        'success': False,
        'files_processed': 0,
        'files_success': 0,
        'files_error': 0,
        'errors': []
    }
    
    try:
        # 1. Criar collection no Qdrant (já deleta se existir)
        print(f"📦 Passo 1/4: Criando collection no Qdrant...")
        if not create_collection(vector_store, collection_name, embedding_model, 
                                description=f"Receitas da {cozinha_name}",
                                delete_if_exists=True):
            results['errors'].append("Falha ao criar collection")
            return results
        
        # 2. Verificar/garantir pasta no MinIO
        print(f"\n📦 Passo 2/4: Verificando storage MinIO...")
        if not ensure_minio_folder(storage_manager, cozinha_name):
            print(f"⚠️  Continuando mesmo com problema no storage...")
        
        # 3. Verificar arquivos já inseridos se skip_existing
        files_to_process = files
        if skip_existing:
            print(f"\n📦 Passo 3/4: Verificando arquivos já inseridos...")
            try:
                existing_docs = vector_store.list_collection_documents(collection_name)
                existing_names = {doc.get('file_name', doc.get('name', '')) for doc in existing_docs}
                
                files_to_process = [
                    f for f in files 
                    if f.name not in existing_names
                ]
                skipped = len(files) - len(files_to_process)
                
                if skipped > 0:
                    print(f"⏭️  {skipped} arquivos já inseridos, serão pulados")
                print(f"📝 {len(files_to_process)} arquivos para processar")
            except Exception as e:
                print(f"⚠️  Erro ao verificar arquivos existentes: {str(e)[:200]}")
                print(f"⚠️  Continuando sem pular arquivos...")
                files_to_process = files
        
        if not files_to_process:
            print(f"\n✅ Todos os arquivos desta cozinha já foram inseridos!")
            results['success'] = True
            return results
        
        # 4. Processar e inserir cada arquivo
        print(f"\n📦 Passo 4/4: Processando e inserindo {len(files_to_process)} arquivos...")
        
        for i, file_path in enumerate(files_to_process, 1):
            print(f"\n[{i}/{len(files_to_process)}] Processando: {file_path.name}")
            
            try:
                # Processar documento
                print(f"  🔧 Processando documento...")
                result = document_processor.process_document(
                    file_path=str(file_path),
                    enhance=enhance
                )
                print(f"  ✅ Documento processado: {len(result['chunks'])} chunks criados")
                
                # Upload para storage (usando cozinha_name como topic)
                print(f"  📤 Fazendo upload para MinIO...")
                upload_result = storage_manager.upload_document(
                    file_path=str(file_path),
                    topic=cozinha_name  # Usar nome da cozinha como pasta no MinIO
                )
                print(f"  ✅ Upload concluído: {upload_result['object_name']}")
                
                # Adicionar metadados aos chunks
                print(f"  🏷️  Adicionando metadados aos chunks...")
                for chunk in result['chunks']:
                    chunk.metadata['minio_path'] = upload_result['original_path']
                    chunk.metadata['minio_object'] = upload_result['object_name']
                    chunk.metadata['file_name'] = file_path.name
                    chunk.metadata['cozinha'] = cozinha_name
                    chunk.metadata['cozinha_type'] = cozinha_name
                
                # Inserir no Qdrant
                print(f"  💾 Inserindo {len(result['chunks'])} chunks no Qdrant...")
                success = vector_store.insert_documents(
                    collection_name=collection_name,
                    documents=result['chunks']
                )
                
                if success:
                    print(f"  ✅ {file_path.name} inserido com sucesso!")
                    results['files_success'] += 1
                else:
                    raise Exception("Falha ao inserir documentos no Qdrant")
                
                results['files_processed'] += 1
                
            except Exception as e:
                error_msg = f"Erro ao processar {file_path.name}: {str(e)}"
                print(f"  ❌ {error_msg}")
                results['errors'].append(error_msg)
                results['files_error'] += 1
                results['files_processed'] += 1
                import traceback
                traceback.print_exc()
        
        # Verificar resultado final
        if results['files_error'] == 0:
            results['success'] = True
            print(f"\n✅ Cozinha '{cozinha_name}' processada com sucesso!")
        else:
            print(f"\n⚠️  Cozinha '{cozinha_name}' processada com {results['files_error']} erros")
        
        # Mostrar estatísticas da collection
        try:
            collections = vector_store.list_collections()
            collection_info = next((c for c in collections if c['name'] == collection_name), None)
            if collection_info:
                print(f"\n📊 Collection '{collection_name}':")
                print(f"   - Documentos únicos: {collection_info.get('document_count', 0)}")
                print(f"   - Total de chunks: {collection_info.get('chunk_count', 0)}")
        except Exception as e:
            print(f"⚠️  Erro ao obter estatísticas: {e}")
        
        return results
        
    except Exception as e:
        error_msg = f"Erro fatal ao processar cozinha '{cozinha_name}': {str(e)}"
        print(f"\n❌ {error_msg}")
        results['errors'].append(error_msg)
        import traceback
        traceback.print_exc()
        return results


def main():
    """Função principal do script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Criar collections por tipo de cozinha e popular com receitas'
    )
    parser.add_argument(
        '--receitas-dir',
        type=str,
        default='receitas_aumentadas',
        help='Diretório contendo as pastas de cozinhas (padrão: receitas_aumentadas)'
    )
    parser.add_argument(
        '--embedding-model',
        type=str,
        default=None,
        help=f'Modelo de embedding a usar (padrão: {config.DEFAULT_EMBEDDING_MODEL})'
    )
    parser.add_argument(
        '--no-enhance',
        action='store_true',
        help='Não usar LLM para melhorar o texto (mais rápido, mas menos formatado)'
    )
    parser.add_argument(
        '--skip-existing',
        action='store_true',
        help='Pular arquivos que já foram inseridos'
    )
    parser.add_argument(
        '--cozinha',
        type=str,
        default=None,
        help='Processar apenas uma cozinha específica (nome da pasta)'
    )
    
    args = parser.parse_args()
    
    # Resolver caminho do diretório de receitas
    receitas_dir = Path(__file__).parent.parent / args.receitas_dir
    
    print(f"{'='*80}")
    print(f"🚀 CONFIGURAÇÃO DE COZINHAS E INSERÇÃO DE RECEITAS")
    print(f"{'='*80}")
    print(f"📁 Diretório: {receitas_dir}")
    print(f"🎨 Melhorar com LLM: {not args.no_enhance}")
    print(f"⏭️  Pular existentes: {args.skip_existing}")
    if args.cozinha:
        print(f"🎯 Cozinha específica: {args.cozinha}")
    print(f"{'='*80}\n")
    
    try:
        # Obter lista de cozinhas
        print(f"🔍 Buscando cozinhas em {receitas_dir}...")
        cozinhas = get_cozinhas(str(receitas_dir))
        
        if not cozinhas:
            print(f"❌ Nenhuma cozinha encontrada em {receitas_dir}")
            sys.exit(1)
        
        # Filtrar por cozinha específica se solicitado
        if args.cozinha:
            cozinhas = [c for c in cozinhas if c['original_name'] == args.cozinha]
            if not cozinhas:
                print(f"❌ Cozinha '{args.cozinha}' não encontrada")
                print(f"\n📋 Cozinhas disponíveis:")
                all_cozinhas = get_cozinhas(str(receitas_dir))
                for c in all_cozinhas:
                    print(f"   - {c['original_name']}")
                sys.exit(1)
        
        print(f"✅ Encontradas {len(cozinhas)} cozinhas:")
        for cozinha in cozinhas:
            print(f"   - {cozinha['original_name']}: {cozinha['file_count']} arquivos → collection '{cozinha['collection_name']}'")
        
        # Inicializar serviços
        print(f"\n🔧 Inicializando serviços...")
        vector_store = QdrantVectorStore()
        document_processor = DocumentProcessor()
        storage_manager = StorageManager()
        print(f"✅ Serviços inicializados")
        
        # Deletar todas as collections de cozinha existentes antes de criar novas
        print(f"\n{'='*80}")
        print(f"🗑️  LIMPEZA DE COLLECTIONS EXISTENTES")
        print(f"{'='*80}")
        deleted_count = delete_all_cozinha_collections(vector_store)
        if deleted_count > 0:
            print(f"✅ {deleted_count} collections antigas foram deletadas")
        print(f"{'='*80}\n")
        
        # Processar cada cozinha
        print(f"\n{'='*80}")
        print(f"📦 PROCESSANDO {len(cozinhas)} COZINHAS")
        print(f"{'='*80}\n")
        
        all_results = []
        total_success = 0
        total_errors = 0
        
        for i, cozinha_info in enumerate(cozinhas, 1):
            print(f"\n{'#'*80}")
            print(f"# [{i}/{len(cozinhas)}]")
            print(f"{'#'*80}")
            
            result = process_cozinha(
                cozinha_info=cozinha_info,
                vector_store=vector_store,
                document_processor=document_processor,
                storage_manager=storage_manager,
                embedding_model=args.embedding_model,
                enhance=not args.no_enhance,
                skip_existing=args.skip_existing
            )
            
            all_results.append(result)
            
            if result['success']:
                total_success += 1
            else:
                total_errors += 1
        
        # Resumo final
        print(f"\n{'='*80}")
        print(f"📊 RESUMO FINAL")
        print(f"{'='*80}")
        print(f"✅ Cozinhas processadas com sucesso: {total_success}/{len(cozinhas)}")
        print(f"❌ Cozinhas com erros: {total_errors}/{len(cozinhas)}")
        
        total_files_processed = sum(r['files_processed'] for r in all_results)
        total_files_success = sum(r['files_success'] for r in all_results)
        total_files_error = sum(r['files_error'] for r in all_results)
        
        print(f"\n📄 Arquivos:")
        print(f"   - Processados: {total_files_processed}")
        print(f"   - Sucesso: {total_files_success}")
        print(f"   - Erros: {total_files_error}")
        
        if total_files_error > 0:
            print(f"\n❌ Erros encontrados:")
            for result in all_results:
                if result['errors']:
                    print(f"\n   Cozinha: {result['cozinha']}")
                    for error in result['errors']:
                        print(f"      - {error}")
        
        # Listar todas as collections criadas
        print(f"\n📋 Collections criadas:")
        try:
            collections = vector_store.list_collections()
            for collection in collections:
                if collection['name'].startswith('cozinha_'):
                    print(f"   - {collection['name']}: {collection.get('document_count', 0)} documentos, {collection.get('chunk_count', 0)} chunks")
        except Exception as e:
            print(f"⚠️  Erro ao listar collections: {e}")
        
        print(f"\n{'='*80}")
        print(f"✅ PROCESSO CONCLUÍDO!")
        print(f"{'='*80}\n")
        
        # Retornar código de saída apropriado
        sys.exit(0 if total_errors == 0 and total_files_error == 0 else 1)
        
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

