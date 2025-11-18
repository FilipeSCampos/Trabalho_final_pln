# Setup Inicial - Primeira Vez

### 1. Clonar o Repositório

```bash
git clone 
cd projeto_pln/Trabalho_final_pln/trabalho_final/pln
```
### 2. Configurar Variáveis de Ambiente

```bash
configurar .env
# IMPORTANTE: Adicionar OPENAI_API_KEY (obrigatório)
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

### 6. Testes

```python
pergunta: Ola, o que voce pode me ajudar?

Resposta: "Olá! Posso te ajudar oferecendo uma variedade de receitas completas, detalhadas e organizadas, provenientes das coleções de culinária disponíveis nos seus documentos. Tenho receitas de diversas culinárias como:
- Cozinha Finlandesa: pratos com salmão defumado, filé de robalo, crème brûlée, brownie finlandês, molhos especiais, entre outros.
- Cozinha Israelense: pratos com pão pita, falafel, shakshuka, hummus, saladas frescas, sobremesas como baklava e cheesecake com calda de damasco.
- Cozinha Belga: pratos robustos com ingredientes como batatas, cerveja e frutos do mar.
- Cozinha Eslovaca: pratos tradicionais como Kapustnica (sopa de repolho), goulash, schnitzel, acompanhados de bolinhos de batata e tortas.
- Cozinha Romena: pratos variados com uso de legumes, carnes e sobremesas típicas.
- Cozinha Árabe: com pães, pastas, carnes com especiarias e doces como baklava.

Ativa todas as collections da RAG
```
<img width="1048" height="541" alt="image" src="https://github.com/user-attachments/assets/d2b8b448-402e-4bf8-bd1f-c20987440b80" />

```python
pergunta: Monte para mim um cardapio completo misturando cozinha chinesa e arabe


