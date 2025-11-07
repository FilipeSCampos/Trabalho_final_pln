# ⚠️ Como Evitar Perda de Dados do Qdrant

## 🚨 Problema

Quando você executa `docker-compose down`, as collections podem ficar vazias se os volumes forem removidos.

## ✅ Solução: Usar Comandos Corretos

### ❌ NUNCA use:
```bash
docker-compose down -v    # Remove volumes e DESTRÓI todos os dados!
```

### ✅ Use estes comandos:

```bash
# Parar containers (mantém volumes)
docker-compose stop

# OU parar e remover containers (mantém volumes)
docker-compose down

# Reiniciar
docker-compose up -d
```

## 📦 Fazer Backup Regular

### Backup Rápido (Metadados)
```bash
python scripts/backup_qdrant.py backup
```

### Backup Completo (Volume Inteiro)
```bash
# Linux/Mac
./scripts/backup_qdrant.sh

# Windows
python scripts/backup_qdrant.py backup
```

## 🔄 Restaurar Dados

Se você perdeu os dados:

1. **Verificar se há backup**:
   ```bash
   python scripts/backup_qdrant.py list
   ```

2. **Restaurar backup**:
   ```bash
   # Linux/Mac
   ./scripts/restore_qdrant_from_backup.sh backups/qdrant/qdrant_volume_backup_*.tar.gz
   ```

## 🔍 Verificar Status dos Dados

```bash
# Ver se o volume tem dados
ls -la volumes/qdrant/collections

# Ver collections no Qdrant
curl http://localhost:5000/api/collections

# Ver logs do Qdrant
docker-compose logs qdrant
```

## 💡 Dicas Importantes

1. **Sempre faça backup antes de fazer `down`**:
   ```bash
   python scripts/backup_qdrant.py backup
   docker-compose down
   ```

2. **Use `stop` ao invés de `down`** quando possível:
   ```bash
   docker-compose stop    # Apenas pausa, não remove nada
   docker-compose start   # Reinicia tudo
   ```

3. **Verificar permissões do volume**:
   ```bash
   # Garantir que a pasta existe e tem permissões corretas
   mkdir -p volumes/qdrant
   chmod -R 755 volumes/qdrant
   ```

## 🛠️ Comandos Úteis

```bash
# Ver volumes do Docker
docker volume ls

# Verificar se o volume está montado
docker inspect qdrant | grep -A 10 Mounts

# Forçar salvamento do Qdrant (antes de parar)
docker-compose exec qdrant qdrant-cli --url http://localhost:6333 collections list
```

## 📝 Checklist Antes de Fazer `docker-compose down`

- [ ] Fazer backup: `python scripts/backup_qdrant.py backup`
- [ ] Verificar se há dados: `ls volumes/qdrant/collections`
- [ ] Usar `docker-compose down` SEM `-v`
- [ ] Após reiniciar, verificar: `curl http://localhost:5000/api/collections`

