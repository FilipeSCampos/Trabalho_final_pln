# Guia de Persistência do Qdrant

## ⚠️ Problema Comum

Quando você executa `docker-compose down`, os dados do Qdrant podem ser perdidos se:
1. Você usar a flag `-v` (remove volumes): `docker-compose down -v`
2. O volume não estiver configurado corretamente
3. O Qdrant não conseguir escrever no volume

## ✅ Solução: Como Preservar os Dados

### 1. **SEMPRE use `docker-compose down` SEM a flag `-v`**

```bash
# ✅ CORRETO - Preserva os dados
docker-compose down

# ❌ ERRADO - Remove volumes e apaga todos os dados
docker-compose down -v
```

### 2. **Verificar se o volume existe e tem permissões**

```bash
# Verificar se a pasta existe
ls -la volumes/qdrant

# Se não existir, criar com permissões corretas
mkdir -p volumes/qdrant
chmod 755 volumes/qdrant
```

### 3. **Fazer Backup Antes de Desligar**

Sempre faça backup antes de desligar o Docker:

```bash
# Fazer backup das collections
python scripts/backup_qdrant_collections.py
```

O backup será salvo em `backups/qdrant/qdrant_backup_YYYYMMDD_HHMMSS.json`

### 4. **Restaurar de um Backup (se necessário)**

Se os dados foram perdidos, restaure do backup:

```bash
# Listar backups disponíveis
ls backups/qdrant/

# Restaurar do backup mais recente
python scripts/restore_qdrant_backup.py backups/qdrant/qdrant_backup_YYYYMMDD_HHMMSS.json
```

## 🔧 Configuração do Docker Compose

O `docker-compose.yml` já está configurado com:

```yaml
volumes:
  - ./volumes/qdrant:/qdrant/storage:rw
```

Isso garante que os dados sejam salvos em `./volumes/qdrant` no seu sistema.

## 📋 Checklist Antes de Desligar

- [ ] Fazer backup das collections: `python scripts/backup_qdrant_collections.py`
- [ ] Verificar que o backup foi criado: `ls backups/qdrant/`
- [ ] Usar `docker-compose down` (SEM `-v`)
- [ ] Verificar que a pasta `volumes/qdrant` ainda existe após desligar

## 🔍 Verificar Persistência

Após subir novamente, verifique se os dados estão lá:

```bash
# Verificar collections
curl http://localhost:6333/collections

# Ou usar o script Python
python -c "from src.vector_store import QdrantVectorStore; vs = QdrantVectorStore(); print([c['name'] for c in vs.list_collections()])"
```

## 🚨 Se os Dados Foram Perdidos

1. **Verificar se há backup:**
   ```bash
   ls backups/qdrant/
   ```

2. **Restaurar do backup:**
   ```bash
   python scripts/restore_qdrant_backup.py backups/qdrant/qdrant_backup_YYYYMMDD_HHMMSS.json
   ```

3. **Se não houver backup, recriar as collections:**
   ```bash
   python scripts/setup_cozinhas.py --skip-existing
   ```

## 💡 Dicas Importantes

1. **Sempre faça backup antes de desligar** - É a única garantia de não perder dados
2. **Nunca use `docker-compose down -v`** - Isso remove todos os volumes
3. **Verifique permissões** - O Qdrant precisa de permissão de escrita no volume
4. **Use volumes nomeados** (opcional) - Mais robusto que bind mounts:
   ```yaml
   volumes:
     - qdrant_data:/qdrant/storage
   
   volumes:
     qdrant_data:
   ```

## 🔄 Workflow Recomendado

```bash
# 1. Fazer backup
python scripts/backup_qdrant_collections.py

# 2. Desligar (SEM -v)
docker-compose down

# 3. Fazer manutenção/atualizações

# 4. Subir novamente
docker-compose up -d

# 5. Verificar se os dados estão lá
python -c "from src.vector_store import QdrantVectorStore; vs = QdrantVectorStore(); cols = vs.list_collections(); print(f'Collections: {len(cols)}')"
```

## 📝 Notas Técnicas

- O Qdrant salva dados em `/qdrant/storage` dentro do container
- O volume mapeia para `./volumes/qdrant` no host
- Os dados são salvos em formato binário pelo Qdrant
- Collections corrompidas geralmente indicam que o Qdrant não conseguiu escrever corretamente

