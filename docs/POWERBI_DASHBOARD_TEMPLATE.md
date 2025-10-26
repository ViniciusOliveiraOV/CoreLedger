# 📊 Template de Dashboard CoreLedger para Power BI

Este documento contém as configurações e medidas DAX recomendadas para criar um dashboard completo do CoreLedger no Power BI.

## 🔗 Configuração Inicial

### 1. Importar Dados
```
1. Abra Power BI Desktop
2. Obter Dados → Texto/CSV
3. Selecione os arquivos da pasta 'powerbi_exports':
   - accounts.csv
   - transactions.csv
   - monthly_summary.csv
   - cashflow_analysis.csv
   - kpis.csv
```

### 2. Relacionamentos
Configure os seguintes relacionamentos no modelo:
```
accounts[id] ↔ transactions[from_account_id] (Muitos para Um)
accounts[id] ↔ transactions[to_account_id] (Muitos para Um)
```

### 3. Campos Calculados (DAX)

#### Medidas Básicas
```dax
// Saldo Total Atual
Saldo Total = SUM(accounts[balance_numeric])

// Total de Contas Ativas
Contas Ativas = 
CALCULATE(
    COUNTROWS(accounts),
    accounts[balance_numeric] > 0
)

// Transações Este Mês
Transações Mês Atual = 
CALCULATE(
    COUNTROWS(transactions),
    MONTH(transactions[transaction_date]) = MONTH(TODAY()),
    YEAR(transactions[transaction_date]) = YEAR(TODAY())
)

// Volume de Depósitos
Volume Depósitos = 
CALCULATE(
    SUM(transactions[amount_numeric]),
    transactions[transaction_type] = "deposit"
)

// Volume de Saques
Volume Saques = 
CALCULATE(
    SUM(transactions[amount_numeric]),
    transactions[transaction_type] = "withdrawal"
)

// Fluxo Líquido
Fluxo Líquido = [Volume Depósitos] - [Volume Saques]

// Ticket Médio
Ticket Médio = 
DIVIDE(
    SUM(transactions[amount_numeric]),
    COUNTROWS(transactions),
    0
)
```

#### Medidas Avançadas
```dax
// Crescimento Mensal de Transações
Crescimento Transações MoM = 
VAR TransacoesAtual = [Transações Mês Atual]
VAR TransacoesAnterior = 
    CALCULATE(
        COUNTROWS(transactions),
        PREVIOUSMONTH(transactions[transaction_date])
    )
RETURN 
    DIVIDE(TransacoesAtual - TransacoesAnterior, TransacoesAnterior, 0)

// Concentração de Saldo (Top 3 contas)
Concentração Top 3 = 
VAR Top3Saldo = 
    CALCULATE(
        SUM(accounts[balance_numeric]),
        TOPN(3, accounts, accounts[balance_numeric], DESC)
    )
VAR SaldoTotal = SUM(accounts[balance_numeric])
RETURN 
    DIVIDE(Top3Saldo, SaldoTotal, 0)

// Última Transação
Última Transação = 
MAX(transactions[transaction_date])

// Dias Desde Última Transação
Dias Sem Transação = 
DATEDIFF([Última Transação], TODAY(), DAY)
```

#### Colunas Calculadas
```dax
// Na tabela accounts
Faixa Saldo = 
SWITCH(
    TRUE(),
    accounts[balance_numeric] >= 10000, "Alto (R$ 10K+)",
    accounts[balance_numeric] >= 1000, "Médio (R$ 1K-10K)",
    accounts[balance_numeric] > 0, "Baixo (R$ 0-1K)",
    "Zero"
)

// Na tabela transactions  
Período do Dia = 
VAR Hora = HOUR(transactions[created_at])
RETURN
SWITCH(
    TRUE(),
    Hora >= 6 && Hora < 12, "Manhã",
    Hora >= 12 && Hora < 18, "Tarde", 
    Hora >= 18 && Hora < 24, "Noite",
    "Madrugada"
)
```

## 📊 Layout do Dashboard

### Página 1: Visão Executiva

#### Cartões KPI (Topo)
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Saldo Total │ Total Contas│ Transações  │ Fluxo Líquido│
│   R$ 125K   │     28      │ Mês: 156    │   R$ 12.5K  │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

#### Visualizações Principais
```
┌─────────────────────┬───────────────────────────────────┐
│                     │                                   │
│  Evolução do Saldo  │     Transações por Tipo           │
│  (Gráfico de Linha) │     (Gráfico de Pizza)            │
│                     │                                   │
├─────────────────────┼───────────────────────────────────┤
│                     │                                   │
│ Top 10 Contas       │   Volume por Mês                  │
│ (Tabela)            │   (Gráfico de Barras)             │
│                     │                                   │
└─────────────────────┴───────────────────────────────────┘
```

### Página 2: Análise de Transações

#### Filtros (Lateral Esquerda)
- Slicer: Período (Últimos 30/90/365 dias)
- Slicer: Tipo de Transação
- Slicer: Faixa de Valor

#### Visualizações
```
┌─────────────────────────────────────────────────────────┐
│           Transações por Dia da Semana                  │
│           (Gráfico de Barras Horizontal)                │
├─────────────────────┬───────────────────────────────────┤
│                     │                                   │
│ Distribuição por    │    Horário das Transações         │
│ Valor (Histograma)  │    (Gráfico de Calor)             │
│                     │                                   │
├─────────────────────┴───────────────────────────────────┤
│              Detalhes das Transações                    │
│              (Tabela com Filtros)                       │
└─────────────────────────────────────────────────────────┘
```

### Página 3: Análise de Contas

#### Visualizações
```
┌─────────────────────┬───────────────────────────────────┐
│                     │                                   │
│ Distribuição de     │   Contas por Categoria            │
│ Saldos (Histograma) │   (Gráfico de Rosca)              │
│                     │                                   │
├─────────────────────┼───────────────────────────────────┤
│                     │                                   │
│ Saldo vs Atividade  │   Ranking de Contas               │
│ (Gráfico Dispersão) │   (Tabela)                        │
│                     │                                   │
└─────────────────────┴───────────────────────────────────┘
```

## 🎨 Configurações de Formatação

### Cores Sugeridas
```
Primary: #2E86AB (Azul corporativo)
Secondary: #A23B72 (Rosa escuro)
Success: #F18F01 (Laranja)
Danger: #C73E1D (Vermelho)
Background: #F8F9FA (Cinza claro)
```

### Formatação de Números
```
Valores Monetários: R$ #,##0.00
Percentuais: 0.00%
Números Inteiros: #,##0
```

### Títulos e Fontes
```
Título Principal: Segoe UI, 18pt, Bold
Subtítulos: Segoe UI, 14pt, Semibold
Texto Normal: Segoe UI, 11pt, Regular
```

## 🔄 Configurações de Atualização

### Power BI Desktop
1. Dados → Atualizar
2. Configure fonte de dados para pasta 'powerbi_exports'
3. Agende atualização automática se necessário

### Power BI Service
```
1. Publique o relatório no workspace
2. Configure Gateway (se necessário)
3. Agende atualização:
   - Frequência: Diária
   - Horário: 06:00
   - Fuso: Brasília (UTC-3)
```

## 📱 Configuração Mobile

### Layout Mobile-Friendly
- Use visualizações empilhadas verticalmente
- Cartões KPI no topo
- Gráficos com rótulos grandes
- Tabelas com colunas essenciais apenas

### Configurações Responsivas
```
Largura mínima: 320px
Orientação: Portrait preferencial
Touch-friendly: Botões > 44px
```

## 🚀 Dicas Avançadas

### Performance
1. Use medidas em vez de colunas calculadas quando possível
2. Configure relacionamentos bidirecionais apenas se necessário
3. Use DirectQuery para dados muito grandes
4. Implemente row-level security se necessário

### Interatividade
1. Configure drill-through entre páginas
2. Use bookmarks para cenários diferentes
3. Implemente tooltips personalizados
4. Configure ações de URL para links externos

### Alertas e Monitoramento
1. Configure alertas para KPIs críticos
2. Use Q&A para consultas em linguagem natural
3. Implemente comentários colaborativos
4. Configure export automático de relatórios

## 📧 Compartilhamento

### Distribuição
```
1. Workspace corporativo
2. App dedicado do CoreLedger
3. Embed em portal interno
4. Email automático de relatórios
```

### Permissões Sugeridas
- **Admins**: Edição total
- **Gestores**: Visualização + comentários
- **Usuários**: Visualização apenas
- **Externos**: Acesso restrito por RLS

---

Este template fornece uma base sólida para criar dashboards profissionais com os dados do CoreLedger. Customize conforme suas necessidades específicas! 📊✨