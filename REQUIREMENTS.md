
# CoreLedger — Requisitos (uma página)

## Requisitos funcionais
- Painel em tempo real via WebSocket `/ws` que transmite mensagens `dashboard_update`.
- Endpoints REST:
  - `GET /api/dashboard` — retorna KPIs e dados para os gráficos.
  - `GET /api/accounts`, `POST /api/accounts` — listar e criar contas.
  - `POST /api/transactions/deposit|withdrawal|transfer` — executar transações.
  - `POST /api/simulate/random-transaction` — gerar tráfego de teste.
- Persistência: banco SQLite com tabelas `accounts` e `transactions`; operações de transferência devem ser ACID.
- Frontend: aplicativo React que renderiza KPIs, gráficos (Recharts) e formulários de transação/conta; usa WS com fallback para REST.

## Requisitos não funcionais
- Desempenho: latência das requisições GET P95 &lt; 200 ms em condições típicas de nó único.
- Latência de broadcast WS: objetivo &lt; 500 ms (mediana &lt; 200 ms).
- Escalabilidade: SQLite serve para protótipo/local; migrar para PostgreSQL em produção para concorrência e resiliência.
- Disponibilidade: meta 99.9% com instâncias redundantes e health checks.
- Segurança: usar HTTPS/WSS e implementar autenticação (JWT/OAuth) antes de expor publicamente.
- Observabilidade: instrumentar métricas (Prometheus) e logs estruturados; expor `/metrics` e `/healthz`.
- Manutenibilidade: manter código modular, adicionar lint, tipagem e testes; manter CI verde.

## Critérios de aceite (exemplos testáveis)
- Funcionais:
  - `GET /api/dashboard` deve retornar 200 e um JSON contendo as chaves `kpis` e `charts`.
  - Cliente conectado ao `/ws` deve receber um `dashboard_update` em até 1s após executar `/api/simulate/random-transaction`.
  - `POST /api/accounts` com payload `{ "name": "X", "initial_balance": 10 }` aumenta `total_accounts` em 1 e a nova conta aparece em `GET /api/accounts`.
  - Depósitos/saques/transferências devem atualizar saldos corretamente e persistir registros em `transactions`.
- Não funcionais:
  - Suíte de testes do backend passa localmente e na CI (ex.: todos os testes pytest passam).
  - Build de produção do frontend conclui sem erros de lint e gera artefatos estáveis.
  - Métricas expostas em `GET /metrics` no formato Prometheus.
  - `GET /healthz` retorna `{"status":"ok","db":"ok","ws_connections":<int>}` quando saudável.

## Observações e próximos passos sugeridos
- Substituir SQLite por PostgreSQL e adicionar migrações (Alembic) para produção.
- Implementar autenticação e controle de acesso e aplicar rate-limiting nas APIs públicas.
- Fornecer Dockerfiles e `docker-compose.yml` para desenvolvimento local (já incluídos).

