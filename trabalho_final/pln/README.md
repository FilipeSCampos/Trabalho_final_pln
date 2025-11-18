# Setup Inicial - Primeira Vez

### 1. Clonar o Repositório

```bash
git clone [URL-DO-SEU-REPOSITORIO]
cd projeto_pln/Trabalho_final_pln/trabalho_final/pln
```
### 2. Configurar Variáveis de Ambiente

```bash
configurar .env

# Editar .env e adicionar suas chaves
# IMPORTANTE: Adicionar OPENAI_API_KEY (obrigatório)
nano .env  # ou use seu editor preferido
```

**Variáveis obrigatórias:**
- `OPENAI_API_KEY` - Sua chave da OpenAI (obrigatório)

**Variáveis opcionais:**
- `GEMINI_API_KEY` - Chave do Google Gemini (opcional)


### 3. Subir os Containers

```bash
# Opção 1: Manual
docker compose up -d
```

### 4. Popular o Qdrant

```bash
python scripts/setup_cozinhas.py
```

### 5. Configurar n8n

1. Acesse http://localhost:5678
2. Faça login
3. Importe o workflow `agente-cozinha.json`:
   - Clique em "Workflows" → "Import from File"
   - Selecione `agente-cozinha.json`


