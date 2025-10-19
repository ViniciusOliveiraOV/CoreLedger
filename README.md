# 🏦 CoreLedger - Sistema Bancário Multilíngue

Um sistema bancário completo desenvolvido em Python com suporte a múltiplos idiomas, interface interativa via terminal e persistência de dados em SQLite.

## 🌟 Características Principais

### 💰 Sistema Bancário Completo
- **Gestão de Contas**: Criação, visualização e exclusão de contas bancárias
- **Operações Financeiras**: Depósitos, saques e transferências entre contas
- **Precisão Monetária**: Utiliza `decimal.Decimal` para evitar erros de ponto flutuante
- **Persistência de Dados**: Armazenamento seguro em banco SQLite com transações ACID
- **Histórico Completo**: Rastreamento detalhado de todas as transações

### 🌍 Suporte Multilíngue Universal
- **20+ Idiomas Suportados**: Inglês, Espanhol, Francês, Alemão, Chinês, Japonês, Coreano, Árabe, Hindi e mais
- **Detecção Automática**: Detecta automaticamente o idioma do sistema
- **Seleção Interativa**: Interface amigável para escolha manual do idioma
- **Persistência de Preferências**: Salva automaticamente sua escolha de idioma
- **Localização Completa**: Símbolos de moeda, formatos de data e terminologia bancária

### 🖥️ Interface Interativa
- **Menu Intuitivo**: Navegação fácil com emojis e formatação colorida
- **Validação de Entrada**: Verificações robustas para todas as entradas do usuário
- **Confirmações de Segurança**: Proteção contra operações acidentais
- **Feedback Visual**: Mensagens claras de sucesso, erro e status

## 📋 Pré-requisitos

### Software Necessário
- **Python 3.8+** (recomendado Python 3.9 ou superior)
- **pip** (gerenciador de pacotes do Python)
- **Git** (para clonar o repositório)

### Sistema Operacional
- **Windows 10/11** (testado)
- **macOS 10.15+** (compatível)
- **Linux Ubuntu 18.04+** (compatível)

## 🚀 Instalação e Execução Local

### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/CoreLedger.git
cd CoreLedger
```

### 2. Crie um Ambiente Virtual (Recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as Dependências
```bash
pip install -r requirements.txt
```

Se o arquivo `requirements.txt` não existir, instale as dependências manualmente:
```bash
pip install pytest decimal
```

### 4. Execute o Sistema Multilíngue
```bash
# Interface multilíngue completa (RECOMENDADO)
python multilingual_cli.py

# Interface em inglês apenas
python interactive_cli.py
```

### 5. Primeira Execução

Na primeira execução, você verá a tela de seleção de idioma:

```
==================================================
🌍 Seleção de Idioma
==================================================
 1. English
 2. Español (Spanish)
 3. Français (French)
 4. Deutsch (German)
 5. Italiano (Italian)
 6. Português (Portuguese)
 7. Русский (Russian)
 8. 中文 (Chinese)
 9. 日本語 (Japanese)
10. 한국어 (Korean)
11. العربية (Arabic)
12. हिन्दी (Hindi)
13. Nederlands (Dutch)
14. Svenska (Swedish)
15. Norsk (Norwegian)
16. Dansk (Danish)
17. Suomi (Finnish)
18. Polski (Polish)
19. Türkçe (Turkish)
20. Ελληνικά (Greek)

💡 Idioma detectado automaticamente: Português (Portuguese)

➤ Selecione seu idioma preferido:
   (Pressione Enter para auto-detectar, ou digite o número do idioma)
Escolha do idioma: 
```

## � Guia de Uso

### Menu Principal
Após selecionar o idioma, você verá o menu principal:

```
========================================
📋 MENU PRINCIPAL
========================================
1. 👤 Criar Nova Conta
2. 💰 Fazer Depósito  
3. � Fazer Saque
4. �🔄 Transferir Dinheiro
5. 💳 Ver Detalhes da Conta
6. � Ver Todas as Contas
7. 📜 Ver Histórico de Transações
8. 🗑️  Excluir Conta
9. � Sair
----------------------------------------
```

### Operações Básicas

#### 🆕 Criar Conta
1. Selecione opção `1`
2. Digite o nome do titular da conta
3. Informe o saldo inicial (ou pressione Enter para R$ 0,00)

#### � Fazer Depósito
1. Selecione opção `2`
2. Escolha a conta de destino
3. Digite o valor do depósito
4. Adicione uma descrição (opcional)

#### 💸 Fazer Saque
1. Selecione opção `3`
2. Escolha a conta de origem
3. Digite o valor do saque
4. Confirme se há saldo suficiente

#### 🔄 Transferir Dinheiro
1. Selecione opção `4`
2. Escolha a conta de origem
3. Escolha a conta de destino
4. Digite o valor da transferência
5. Confirme a operação

## �️ Estrutura do Projeto

```
CoreLedger/
├── src/                          # Código fonte principal
│   ├── models/                   # Modelos de dados
│   │   ├── __init__.py
│   │   ├── database.py          # Gerenciamento do banco SQLite
│   │   ├── account.py           # Modelo e repositório de contas
│   │   └── transaction.py       # Modelo de transações
│   ├── i18n/                    # Sistema de internacionalização
│   │   ├── __init__.py          # LanguageManager principal
│   │   └── translations/        # Arquivos de tradução
│   │       ├── es.json         # Espanhol
│   │       ├── fr.json         # Francês
│   │       ├── de.json         # Alemão
│   │       ├── zh.json         # Chinês
│   │       ├── ja.json         # Japonês
│   │       └── pt.json         # Português (em desenvolvimento)
│   └── ledger.py                # Sistema bancário principal
├── tests/                       # Testes automatizados
│   ├── __init__.py
│   ├── test_account.py         # Testes de contas
│   ├── test_database.py        # Testes de banco de dados
│   ├── test_ledger.py          # Testes do sistema principal
│   └── test_transaction.py     # Testes de transações
├── examples/                    # Exemplos de uso
├── multilingual_cli.py         # Interface multilíngue (PRINCIPAL)
├── interactive_cli.py          # Interface em inglês
├── requirements.txt            # Dependências Python
└── README.md                   # Este arquivo
```

## 🧪 Executando Testes

### Executar Todos os Testes
```bash
pytest tests/ -v
```

### Executar Testes com Cobertura
```bash
pytest tests/ --cov=src --cov-report=html
```

### Executar Teste Específico
```bash
pytest tests/test_ledger.py::TestBankLedger::test_create_account -v
```

## ⚙️ Configuração Avançada

### Personalizar Localização do Banco de Dados
```bash
# Usar banco de dados personalizado
python multilingual_cli.py meu_banco.db
```

### Arquivos de Configuração
- **Preferências de Idioma**: `.coreledger_config.json`
- **Banco de Dados**: `multilingual_bank.db` (padrão)

### Variáveis de Ambiente
```bash
# Definir idioma padrão (opcional)
export CORELEDGER_LANG=pt

# Definir localização do banco (opcional)
export CORELEDGER_DB_PATH=/caminho/para/banco.db
```

## 🌐 Idiomas Suportados

| Código | Idioma | Status | Símbolo Monetário |
|--------|--------|--------|-------------------|
| `en` | English | ✅ Completo | $ |
| `es` | Español | ✅ Completo | $ |
| `fr` | Français | ✅ Completo | $ |
| `de` | Deutsch | ✅ Completo | $ |
| `it` | Italiano | 🔄 Em desenvolvimento | € |
| `pt` | Português | 🔄 Em desenvolvimento | R$ |
| `ru` | Русский | 📋 Planejado | ₽ |
| `zh` | 中文 | ✅ Completo | ¥ |
| `ja` | 日本語 | ✅ Completo | ¥ |
| `ko` | 한국어 | 📋 Planejado | ₩ |
| `ar` | العربية | 📋 Planejado | $ |
| `hi` | हिन्दी | 📋 Planejado | ₹ |

## 🔧 Solução de Problemas

### Problema: Erro de Codificação no Terminal Windows
```bash
# Solução: Configure o terminal para UTF-8
chcp 65001
python multilingual_cli.py
```

### Problema: Banco de Dados Bloqueado
```bash
# Solução: Certifique-se de que não há outras instâncias rodando
# Ou delete o arquivo .db para recomeçar
del multilingual_bank.db
```

### Problema: Idioma Não Detectado Corretamente
```bash
# Solução: Selecione manualmente na primeira execução
# O sistema salvará sua preferência
```

### Problema: Dependências não Encontradas
```bash
# Solução: Reinstale as dependências
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 📊 Exemplos de Uso

### Exemplo 1: Gestão Pessoal
```python
# Criar conta pessoal
python multilingual_cli.py
# 1 -> "João Silva" -> "1000"
# Sistema criará conta com R$ 1.000,00
```

### Exemplo 2: Múltiplas Contas Familiares  
```python
# Criar contas para família
# Conta 1: "João (Principal)" -> R$ 5.000,00
# Conta 2: "Maria (Poupança)" -> R$ 2.000,00  
# Conta 3: "Filhos (Mesada)" -> R$ 200,00
# Transferir R$ 300 de João para Filhos
```

### Exemplo 3: Controle Empresarial
```python
# Contas empresariais
# "Conta Corrente" -> R$ 50.000,00
# "Conta Poupança" -> R$ 20.000,00
# "Fundo Emergência" -> R$ 10.000,00
# Transferências e histórico detalhado
```

## 🤝 Contribuindo

### Como Adicionar um Novo Idioma

1. **Crie o arquivo de tradução**:
```bash
# Copie o modelo em inglês
cp src/i18n/translations/en.json src/i18n/translations/pt.json
```

2. **Traduza todas as chaves**:
```json
{
  "app_welcome": "Bem-vindo ao Sistema Bancário CoreLedger",
  "menu_title": "MENU PRINCIPAL",
  "currency_symbol": "R$",
  "currency_format": "R$ {amount}"
}
```

3. **Adicione ao LanguageManager**:
```python
AVAILABLE_LANGUAGES = {
    'pt': 'Português (Portuguese)',
    # ... outros idiomas
}
```

4. **Teste a implementação**:
```bash
pytest tests/ -k "test_translations"
```

### Reportar Bugs
- Abra uma **issue** no GitHub com detalhes do problema
- Inclua informações do sistema operacional e versão do Python
- Anexe logs de erro se disponível

### Sugerir Melhorias
- **Pull requests** são bem-vindos!
- Siga os padrões de código existentes
- Adicione testes para novas funcionalidades

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- **Python Software Foundation** - Linguagem Python
- **SQLite** - Banco de dados embarcado
- **pytest** - Framework de testes
- **Comunidade Open Source** - Inspiração e recursos

## 📞 Suporte

- **GitHub Issues**: [Reportar problemas](https://github.com/seu-usuario/CoreLedger/issues)
- **Documentação**: Este README e comentários no código
- **Email**: seu-email@exemplo.com

---

### 🚀 **Comece Agora!**

```bash
git clone https://github.com/seu-usuario/CoreLedger.git
cd CoreLedger
python -m venv venv
venv\Scripts\activate  # Windows
pip install pytest
python multilingual_cli.py
```

**Desenvolvido com ❤️ em Python | Sistema Bancário Multilíngue Completo**

## Design Principles

- **Decimal Precision**: All monetary values use `decimal.Decimal` to avoid floating-point errors
- **ACID Transactions**: Database operations are wrapped in transactions for consistency
- **Input Validation**: Comprehensive validation for all operations
- **Error Handling**: Clear exceptions and error messages
- **Separation of Concerns**: Clean architecture with separate models and business logic