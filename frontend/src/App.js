import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  ResponsiveContainer,
  LineChart,
  Line
} from 'recharts';

const API_BASE = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws';

// Color palette
const COLORS = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c'];

function App() {
  const [dashboardData, setDashboardData] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [ws, setWs] = useState(null);
  const [loading, setLoading] = useState(true);

  // Transaction form states
  const [transactionForm, setTransactionForm] = useState({
    type: 'deposit',
    accountId: '',
    toAccountId: '',
    amount: '',
    description: ''
  });

  // New account form
  const [newAccount, setNewAccount] = useState({
    name: '',
    initialBalance: 0
  });

  // WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      const websocket = new WebSocket(WS_URL);
      
      websocket.onopen = () => {
        console.log('WebSocket connected');
        setWsConnected(true);
        setWs(websocket);
      };

      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'dashboard_update') {
            setDashboardData(data.data);
            setLoading(false);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      websocket.onclose = () => {
        console.log('WebSocket disconnected');
        setWsConnected(false);
        setWs(null);
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        setWsConnected(false);
      };
    };

    connectWebSocket();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  // Initial data load (fallback if WebSocket fails)
  useEffect(() => {
    if (!wsConnected) {
      loadDashboardData();
    }
  }, [wsConnected]);

  const loadDashboardData = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/dashboard`);
      setDashboardData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      setLoading(false);
    }
  };

  const handleTransaction = async (e) => {
    e.preventDefault();
    
    try {
      const endpoint = `${API_BASE}/api/transactions/${transactionForm.type}`;
      const payload = {
        account_id: transactionForm.accountId,
        amount: parseFloat(transactionForm.amount),
        description: transactionForm.description
      };

      if (transactionForm.type === 'transfer') {
        payload.from_account_id = transactionForm.accountId;
        payload.to_account_id = transactionForm.toAccountId;
      }

      await axios.post(endpoint, payload);
      
      // Reset form
      setTransactionForm({
        type: 'deposit',
        accountId: '',
        toAccountId: '',
        amount: '',
        description: ''
      });

      alert('Transaction completed successfully!');
    } catch (error) {
      console.error('Transaction failed:', error);
      alert('Transaction failed: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleCreateAccount = async (e) => {
    e.preventDefault();
    
    try {
      await axios.post(`${API_BASE}/api/accounts`, {
        name: newAccount.name,
        initial_balance: parseFloat(newAccount.initialBalance) || 0
      });

      setNewAccount({ name: '', initialBalance: 0 });
      alert('Account created successfully!');
    } catch (error) {
      console.error('Account creation failed:', error);
      alert('Account creation failed: ' + (error.response?.data?.detail || error.message));
    }
  };

  const simulateRandomTransaction = async () => {
    try {
      await axios.post(`${API_BASE}/api/simulate/random-transaction`);
    } catch (error) {
      console.error('Simulation failed:', error);
      alert('Simulation failed: ' + (error.response?.data?.detail || error.message));
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString('pt-BR');
  };

  if (loading) {
    return (
      <div className="app">
        <div className="loading">
          <h2>Carregando CoreLedger...</h2>
          <p>Conectando aos dados em tempo real...</p>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="app">
        <div className="loading">
          <h2>Erro ao carregar dados</h2>
          <p>Verifique se a API está rodando na porta 8000</p>
          <button onClick={loadDashboardData} className="btn">
            Tentar Novamente
          </button>
        </div>
      </div>
    );
  }

  const { kpis, charts } = dashboardData;

  // Prepare chart data
  const pieData = charts.transaction_types.map((item, index) => ({
    name: item.type === 'deposit' ? 'Depósitos' : 
          item.type === 'withdrawal' ? 'Saques' : 
          item.type === 'transfer' ? 'Transferências' : item.type,
    value: item.count,
    color: COLORS[index % COLORS.length]
  }));

  // Balance distribution data
  const balanceData = charts.accounts.map(account => ({
    name: account.name.length > 10 ? account.name.substring(0, 10) + '...' : account.name,
    balance: account.balance
  }));

  // Recent transactions timeline data
  const timelineData = charts.recent_transactions
    .slice(0, 7)
    .reverse()
    .map((transaction, index) => ({
      index: index + 1,
      amount: transaction.amount,
      type: transaction.type,
      time: new Date(transaction.created_at).toLocaleTimeString('pt-BR', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    }));

  return (
    <div className="app">
      {/* Connection Status */}
      <div className={`connection-status ${wsConnected ? 'connected' : 'disconnected'}`}>
        {wsConnected ? '🟢 Conectado em tempo real' : '🔴 Offline'}
      </div>

      {/* Header */}
      <div className="header">
        <h1>🏦 CoreLedger Dashboard</h1>
        <p>Sistema Bancário em Tempo Real • {formatDateTime(kpis.timestamp)}</p>
      </div>

      {/* KPI Cards */}
      <div className="kpi-cards">
        <div className="kpi-card">
          <div className="kpi-label">Patrimônio Total</div>
          <div className="kpi-value" style={{color: '#2ecc71'}}>
            {formatCurrency(kpis.total_balance)}
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Total de Contas</div>
          <div className="kpi-value" style={{color: '#3498db'}}>
            {kpis.total_accounts}
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Transações Hoje</div>
          <div className="kpi-value" style={{color: '#f39c12'}}>
            {kpis.today_transactions}
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Transações do Mês</div>
          <div className="kpi-value" style={{color: '#9b59b6'}}>
            {kpis.month_transactions}
          </div>
        </div>
      </div>

      {/* Transaction Form */}
      <div className="transaction-form">
        <h3>Nova Transação</h3>
        <form onSubmit={handleTransaction}>
          <div className="form-row">
            <div className="form-group">
              <label>Tipo de Transação</label>
              <select 
                value={transactionForm.type} 
                onChange={(e) => setTransactionForm({...transactionForm, type: e.target.value})}
              >
                <option value="deposit">Depósito</option>
                <option value="withdrawal">Saque</option>
                <option value="transfer">Transferência</option>
              </select>
            </div>
            <div className="form-group">
              <label>Conta {transactionForm.type === 'transfer' ? 'Origem' : ''}</label>
              <select 
                value={transactionForm.accountId} 
                onChange={(e) => setTransactionForm({...transactionForm, accountId: e.target.value})}
                required
              >
                <option value="">Selecione uma conta</option>
                {charts.accounts.map(account => (
                  <option key={account.id} value={account.id}>
                    {account.name} - {formatCurrency(account.balance)}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            {transactionForm.type === 'transfer' && (
              <div className="form-group">
                <label>Conta Destino</label>
                <select 
                  value={transactionForm.toAccountId} 
                  onChange={(e) => setTransactionForm({...transactionForm, toAccountId: e.target.value})}
                  required
                >
                  <option value="">Selecione conta destino</option>
                  {charts.accounts
                    .filter(account => account.id !== transactionForm.accountId)
                    .map(account => (
                    <option key={account.id} value={account.id}>
                      {account.name} - {formatCurrency(account.balance)}
                    </option>
                  ))}
                </select>
              </div>
            )}
            <div className="form-group">
              <label>Valor</label>
              <input
                type="number"
                step="0.01"
                value={transactionForm.amount}
                onChange={(e) => setTransactionForm({...transactionForm, amount: e.target.value})}
                required
                placeholder="0.00"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Descrição (opcional)</label>
            <input
              type="text"
              value={transactionForm.description}
              onChange={(e) => setTransactionForm({...transactionForm, description: e.target.value})}
              placeholder="Descrição da transação..."
            />
          </div>

          <div className="form-row">
            <button type="submit" className="btn btn-success">
              Executar {transactionForm.type === 'deposit' ? 'Depósito' : 
                       transactionForm.type === 'withdrawal' ? 'Saque' : 'Transferência'}
            </button>
            <button type="button" onClick={simulateRandomTransaction} className="btn btn-warning">
              🎲 Simular Transação Aleatória
            </button>
          </div>
        </form>
      </div>

      {/* New Account Form */}
      <div className="transaction-form">
        <h3>Nova Conta</h3>
        <form onSubmit={handleCreateAccount}>
          <div className="form-row">
            <div className="form-group">
              <label>Nome da Conta</label>
              <input
                type="text"
                value={newAccount.name}
                onChange={(e) => setNewAccount({...newAccount, name: e.target.value})}
                required
                placeholder="Nome do titular..."
              />
            </div>
            <div className="form-group">
              <label>Saldo Inicial</label>
              <input
                type="number"
                step="0.01"
                value={newAccount.initialBalance}
                onChange={(e) => setNewAccount({...newAccount, initialBalance: e.target.value})}
                placeholder="0.00"
              />
            </div>
          </div>
          <button type="submit" className="btn">
            Criar Conta
          </button>
        </form>
      </div>

      {/* Dashboard Charts */}
      <div className="dashboard">
        {/* Transaction Types Pie Chart */}
        {pieData.length > 0 && (
          <div className="chart-container">
            <div className="chart-title">Distribuição por Tipo de Transação</div>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({name, value}) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Account Balances Bar Chart */}
        {balanceData.length > 0 && (
          <div className="chart-container">
            <div className="chart-title">Saldos por Conta</div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={balanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis tickFormatter={(value) => `R$ ${value}`} />
                <Tooltip formatter={(value) => formatCurrency(value)} />
                <Bar dataKey="balance" fill="#3498db" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Recent Transactions Timeline */}
        {timelineData.length > 0 && (
          <div className="chart-container">
            <div className="chart-title">Últimas Transações</div>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={timelineData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis tickFormatter={(value) => `R$ ${value}`} />
                <Tooltip 
                  formatter={(value) => [formatCurrency(value), 'Valor']}
                  labelFormatter={(label) => `Hora: ${label}`}
                />
                <Line 
                  type="monotone" 
                  dataKey="amount" 
                  stroke="#2ecc71" 
                  strokeWidth={2}
                  dot={{ fill: '#2ecc71', strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Accounts Table */}
        <div className="chart-container">
          <div className="chart-title">Todas as Contas</div>
          <table className="accounts-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Nome</th>
                <th>Saldo</th>
                <th>Criado em</th>
              </tr>
            </thead>
            <tbody>
              {charts.accounts.map(account => (
                <tr key={account.id}>
                  <td>{account.id}</td>
                  <td>{account.name}</td>
                  <td style={{color: account.balance >= 0 ? '#2ecc71' : '#e74c3c'}}>
                    {formatCurrency(account.balance)}
                  </td>
                  <td>
                    {account.created_at ? formatDateTime(account.created_at) : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default App;