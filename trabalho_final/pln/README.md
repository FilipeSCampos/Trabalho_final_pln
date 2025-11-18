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

#quando eu desço os containers "docker compose down" e subo novamente o qdrant todo corrompe, caso isso aconteca, é so rodar o setup_cozinhas
ele ja automaticamente deleta todas as collections corrompidas que existem.
```

### 5. Configurar n8n

1. Acesse http://localhost:5678
2. Faça login
3. Importe o workflow `agente-cozinha.json`:
   - Clique em "Workflows" → "Import from File"
   - Selecione `agente-cozinha.json`

### 6. Testes e Exemplos de perguntas

```python
Pergunta: Ola, o que voce pode me ajudar?

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
Pergunta: Monte para mim um cardapio completo misturando cozinha chinesa e arabe

Resposta:  Entradas e Canapés
- Palmito com caviar de tapioca (Chinês): Sagu de tapioca cozido até transparente, temperado com shoyu, servido com palmito em rodelas.
- Canapés Árabes: Baby falafel com molho de hortelã, pão pita crispy com coalhada seca e tomate cereja seco, bolinho de bacalhau com molho de pimenta, espetinho de frango e carne com pimentão 3 cores.
Saladas
- Salada de rúcula com alface roxa, muçarela de búfala, cebola roxa (Chinês).
- Salada Fatoush (Árabe): Mix de alface, tomate, pepino, rabanete e temperos típicos.
- Salada de tomate cereja com mix de folhas, sementes de romã e nozes (Árabe).
Sopas
- Sopa de lentilha vermelha com croutons de pão árabe, limão e molho de pimenta (Árabe).
- Sopa de grão de bico com tomate e batata acompanhada de croutons de pão folha (Árabe).
Pratos principais
- Guisado de sobrecoxa de frango com frutas secas acompanhado de purê de batatas cremoso com cebola e ervas (Árabe).
- Kabsa de frango (sobrecoxa assada com arroz basmati, passas e damasco) (Árabe).
- Carneiro cozido com legumes variados (berinjela, mini batata, mini cenoura) e arroz basmati (Árabe).
- Pratos chineses com molho agridoce, espetinhos e canapés diversos como espetinho de frango com pimentão 3 cores ao molho agridoce.
- Palmito com caviar de tapioca.
Acompanhamentos
Batatas rústicas assadas com tempero árabe (cominho e tomilho).
Legumes ao forno com ervas (tomilho, cominho).
Cuscuz marroquino (Árabe).
Sobremesas
- Baklava (Árabe).
- Kunefe (Árabe).
- Cheesecake de calda de damasco (Árabe).
- Verrine de creme inglês com frutas vermelhas e mini suspiros (Árabe).
- Frutas laminadas (melancia, melão, manga, abacaxi).
Os pratos listados são para eventos variados, para 4-6 pessoas em versões menores, podendo ser ajustado para maiores. Quer que eu detalhe o modo de preparo de algum prato?

Temos poucos dados de receitas chinesas, e muitos dados de receitas Árabes, porém se pedissimo para ele deixar uma opção de cada, o menu ficaria bem equilibrado entre as duas cozinhas.

Ativa somente as collections necessárias
```
<img width="1048" height="545" alt="image" src="https://github.com/user-attachments/assets/63628ada-2628-4560-8bc0-f67d9642d58e" />


