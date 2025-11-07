# Solução para Collections Corrompidas no Qdrant

## 🚨 Problema

Collections ficam corrompidas com erro:
```
OutputTooSmall { ... }
Service internal error: task panicked
```

## ✅ Solução Rápida

### Opção 1: Limpar e Recriar (Recomendado)

```bash
# 1. Parar o Qdrant
docker-compose stop qdrant

# 2. Limpar o volume corrompido
# Linux/Mac:
rm -rf volumes/qdrant/*

# Windows PowerShell:
Remove-Item -Recurse -Force volumes\qdrant\*

# 3. Subir novamente
docker-compose up -d qdrant

# 4. Aguardar o Qdrant inicializar (30 segundos)
sleep 30

# 5. Recriar todas as collections
python scripts/setup_cozinhas.py
```

### Opção 2: Usar Script de Correção

```bash
# 1. Tentar corrigir collections corrompidas
python scripts/fix_corrupted_collections.py

# 2. Se não funcionar, forçar limpeza
python scripts/recreate_corrupted_collections.py

# 3. Recriar collections
python scripts/setup_cozinhas.py
```

### Opção 3: Reiniciar Qdrant Completamente

```bash
# 1. Parar tudo
docker-compose down

# 2. Limpar volume
rm -rf volumes/qdrant/*

# 3. Subir tudo
docker-compose up -d

# 4. Aguardar inicialização
sleep 30

# 5. Recriar collections
python scripts/setup_cozinhas.py
```

## 🔍 Verificar se Está Corrompido

```bash
# Verificar saúde das collections
python scripts/fix_corrupted_collections.py
```

## 💡 Prevenção

1. **Sempre use `docker-compose down` SEM `-v`**
2. **Faça backup antes de desligar:**
   ```bash
   python scripts/backup_qdrant_collections.py
   docker-compose down
   ```

3. **Use o script setup_cozinhas que sempre limpa antes de criar:**
   ```bash
   python scripts/setup_cozinhas.py
   ```

## 🛠️ Scripts Disponíveis

- `fix_corrupted_collections.py` - Detecta e tenta corrigir collections corrompidas
- `recreate_corrupted_collections.py` - Força deleção de todas as collections
- `setup_cozinhas.py` - Limpa e recria todas as collections do zero

## ⚠️ Se Nada Funcionar

Se os scripts não conseguirem deletar as collections:

1. **Reinicie o Qdrant:**
   ```bash
   docker-compose restart qdrant
   ```

2. **Limpe o volume manualmente:**
   ```bash
   docker-compose down
   rm -rf volumes/qdrant/*
   docker-compose up -d
   ```

3. **Recrie tudo:**
   ```bash
   python scripts/setup_cozinhas.py
   ```

