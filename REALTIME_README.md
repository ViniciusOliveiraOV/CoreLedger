# 🚀 CoreLedger Real-Time Dashboard

## ⚡ Como Executar o Sistema Completo

### 1. 🖥️ Backend (API FastAPI)

```bash
# Ativar ambiente virtual
.venv\Scripts\activate

# Instalar dependências (se não instalou ainda)
pip install fastapi uvicorn[standard] websockets

# Executar API
python api/main.py
```

**API rodará em:** `http://localhost:8000`

### 2. 🌐 Frontend (React)

```bash
# Ir para pasta do frontend
cd frontend

# Instalar dependências do Node.js
npm install

# Executar desenvolvimento
npm start
```

**Frontend rodará em:** `http://localhost:3000`

### 3. 🎯 Acessar o Dashboard

1. **Abra o navegador** em `http://localhost:3000`
2. **Dashboard em tempo real** com WebSocket
3. **Crie contas** e **faça transações**
4. **Veja atualizações automáticas** nos gráficos

## 🔧 Funcionalidades Implementadas

### ✅ **Backend (FastAPI + WebSocket)**
- **REST API** completa para operações bancárias
- **WebSocket** para atualizações em tempo real
- **Endpoints**: contas, depósitos, saques, transferências
- **Simulador** de transações aleatórias
- **CORS** configurado para React

### ✅ **Frontend (React + Recharts)**
- **Dashboard executivo** em tempo real
- **4 KPIs principais** (saldo, contas, transações)
- **Gráficos dinâmicos**: Pizza, Barras, Linha
- **Formulários** para criar contas e transações
- **Tabela** com todas as contas
- **Status de conexão** WebSocket

### ✅ **Atualizações em Tempo Real**
- **WebSocket** conecta automaticamente
- **Reconexão automática** se desconectar
- **Broadcast** para todos os clientes conectados
- **Gráficos atualizam** instantaneamente

## 📊 **Visualizações Disponíveis**

### 📈 **KPIs Executivos:**
- 💰 **Patrimônio Total** (soma de todos os saldos)
- 👥 **Total de Contas** (quantidade de contas)
- 📅 **Transações Hoje** (atividade diária)
- 📊 **Transações do Mês** (atividade mensal)

### 📉 **Gráficos Dinâmicos:**
- 🥧 **Pizza**: Distribuição por tipo de transação
- 📊 **Barras**: Saldos por conta individual
- 📈 **Linha**: Timeline das últimas transações
- 📋 **Tabela**: Lista completa de contas

## 🎮 **Como Testar**

### **1. Criar Dados de Teste:**
1. **Crie algumas contas** com saldos diferentes
2. **Faça depósitos, saques, transferências**
3. **Use o botão "Simular Transação"** para gerar dados aleatórios

### **2. Ver Atualizações em Tempo Real:**
1. **Abra 2 abas** do navegador
2. **Faça uma transação** em uma aba
3. **Veja atualizar automaticamente** na outra aba

### **3. Testar WebSocket:**
- **Status de conexão** no canto superior direito
- **Verde**: Conectado em tempo real
- **Vermelho**: Offline (reconectará automaticamente)

## 🔧 **API Endpoints Disponíveis**

### **REST API:**
```
GET  /api/dashboard          # Dados completos do dashboard
GET  /api/accounts           # Lista de contas
POST /api/accounts           # Criar nova conta
POST /api/transactions/deposit    # Fazer depósito
POST /api/transactions/withdrawal # Fazer saque  
POST /api/transactions/transfer   # Transferência
POST /api/simulate/random-transaction # Simular transação
```

### **WebSocket:**
```
WS   /ws                     # Conexão em tempo real
```

## 🎨 **Tecnologias Utilizadas**

### **Backend:**
- **FastAPI** - API REST moderna
- **WebSocket** - Comunicação em tempo real
- **SQLite** - Banco de dados existente
- **Uvicorn** - Servidor ASGI

### **Frontend:**
- **React 18** - Interface moderna
- **Recharts** - Gráficos responsivos
- **Axios** - Cliente HTTP
- **WebSocket API** - Tempo real
- **CSS Grid/Flexbox** - Layout responsivo

## 🚀 **Próximas Funcionalidades**

- [ ] **Autenticação** com JWT
- [ ] **Múltiplos usuários** simultâneos
- [ ] **Histórico** de transações paginado
- [ ] **Relatórios** em PDF
- [ ] **Alertas** personalizáveis
- [ ] **Dark mode** toggle
- [ ] **Mobile app** com React Native
- [ ] **Backup automático** dos dados

## 🔥 **Destaques Técnicos**

- **Zero configuração** - Funciona out-of-the-box
- **Real-time updates** - WebSocket nativo
- **Responsive design** - Funciona mobile/desktop
- **Error handling** - Reconexão automática
- **Clean code** - Arquitetura modular
- **Type safety** - Validação de dados

**Execute e veja a mágica acontecer! ✨**