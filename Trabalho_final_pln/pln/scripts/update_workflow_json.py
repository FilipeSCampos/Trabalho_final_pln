#!/usr/bin/env python3
"""Script para atualizar o workflow JSON com nós Qdrant para cada cozinha."""

import json
import re
import uuid
from pathlib import Path


def normalize_collection_name(cozinha_name: str) -> str:
    """Normaliza o nome da cozinha para um nome de collection válido."""
    name = cozinha_name.replace("Cozinha ", "").strip()
    name = name.lower()
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '_', name)
    name = name.strip('_')
    return f"cozinha_{name}"


def normalize_display_name(cozinha_name: str) -> str:
    """Converte nome da cozinha para nome de exibição."""
    name = cozinha_name.replace("Cozinha ", "")
    return f"Cozinha {name}"


def create_qdrant_node(collection_name: str, display_name: str, position: list) -> dict:
    """Cria um nó Qdrant para uma collection."""
    node_name = f"Qdrant-{display_name.replace(' ', '-').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ç', 'c')}"
    
    return {
        "parameters": {
            "mode": "retrieve-as-tool",
            "toolDescription": f"Coleção de receitas da {display_name}. Utilize esta coleção para buscar receitas específicas desta cozinha quando a pergunta mencionar ou for relacionada a esta culinária.",
            "qdrantCollection": {
                "__rl": True,
                "value": collection_name,
                "mode": "list",
                "cachedResultName": collection_name
            },
            "topK": 10,
            "options": {}
        },
        "type": "@n8n/n8n-nodes-langchain.vectorStoreQdrant",
        "typeVersion": 1.3,
        "position": position,
        "id": str(uuid.uuid4()),
        "name": node_name,
        "credentials": {
            "qdrantApi": {
                "id": "BnA6YfulHBHX72eS",
                "name": "QdrantApi account"
            }
        }
    }


def main():
    # Lista de cozinhas baseada nas pastas
    cozinhas = [
        "Cozinha Americana",
        "Cozinha Angolana",
        "Cozinha Árabe",
        "Cozinha Belga",
        "Cozinha Chinesa",
        "Cozinha do Cáucaso",
        "Cozinha Eslava",
        "Cozinha Eslovaca",
        "Cozinha Finlandesa",
        "Cozinha Gabonesa",
        "Cozinha Irlandesa",
        "Cozinha Israelense",
        "Cozinha Luxemburguesa",
        "Cozinha Maltesa",
        "Cozinha Portuguesa",
        "Cozinha Romena",
        "Cozinha Suíça",
        "Cozinha Turca"
    ]
    
    # Carregar workflow
    workflow_path = Path(__file__).parent / "agent-proxy_final.json"
    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)
    
    # Encontrar nó de embedding e agente
    emb_node = None
    agente_node = None
    for node in workflow['nodes']:
        if node['name'] == 'EmbOpenAI-full':
            emb_node = node
        if node['name'] == 'Agente OpenAI':
            agente_node = node
    
    if not emb_node or not agente_node:
        print("❌ Nós necessários não encontrados!")
        return
    
    # Criar nós Qdrant para cada cozinha
    start_x = 2080  # Posição X inicial (depois do receitas-openai)
    start_y = 672   # Posição Y inicial
    spacing_y = 160
    max_per_column = 8
    
    new_nodes = []
    qdrant_node_names = []
    
    for i, cozinha in enumerate(sorted(cozinhas)):
        collection_name = normalize_collection_name(cozinha)
        display_name = normalize_display_name(cozinha)
        
        column = i // max_per_column
        row = i % max_per_column
        x = start_x + (column * 320)
        y = start_y + (row * spacing_y)
        
        qdrant_node = create_qdrant_node(collection_name, display_name, [x, y])
        new_nodes.append(qdrant_node)
        qdrant_node_names.append(qdrant_node['name'])
        
        print(f"✅ Criado nó para {collection_name} -> {qdrant_node['name']}")
    
    # Adicionar nós ao workflow
    workflow['nodes'].extend(new_nodes)
    
    # Adicionar conexões
    connections = workflow['connections']
    
    # 1. Embedding -> cada nó Qdrant
    emb_node_name = emb_node['name']
    if emb_node_name not in connections:
        connections[emb_node_name] = {}
    if 'ai_embedding' not in connections[emb_node_name]:
        connections[emb_node_name]['ai_embedding'] = []
    
    # Adicionar conexões para cada novo nó (preservando a existente)
    for qdrant_node_name in qdrant_node_names:
        connections[emb_node_name]['ai_embedding'].append([{
            "node": qdrant_node_name,
            "type": "ai_embedding",
            "index": 0
        }])
    
    # 2. Cada nó Qdrant -> Agente OpenAI
    agente_node_name = agente_node['name']
    if agente_node_name not in connections:
        connections[agente_node_name] = {}
    if 'ai_tool' not in connections[agente_node_name]:
        connections[agente_node_name]['ai_tool'] = []
    
    for qdrant_node_name in qdrant_node_names:
        connections[agente_node_name]['ai_tool'].append([{
            "node": qdrant_node_name,
            "type": "ai_tool",
            "index": 0
        }])
    
    # Salvar workflow atualizado
    output_path = workflow_path.parent / "agent-proxy_final_with_cozinhas.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Workflow atualizado!")
    print(f"📄 Arquivo salvo em: {output_path}")
    print(f"📊 Total de nós Qdrant adicionados: {len(new_nodes)}")
    print(f"\n💡 Importe o arquivo '{output_path.name}' no n8n")


if __name__ == '__main__':
    main()

