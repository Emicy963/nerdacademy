# Acadêmico — Visão Técnica da Plataforma

> Documento de referência técnica. Actualizado a cada feature relevante adicionada à plataforma.
> Última actualização: 2026-04-27 (v0.4.6)

---

## O que é o Acadêmico

Acadêmico é uma plataforma SaaS (Software as a Service) de gestão académica desenvolvida para centros de formação técnica em Angola. O sistema permite que uma instituição gira estudantes, formadores, cursos, turmas, inscrições e avaliações, tudo num único lugar.

O modelo de negócio é multi-tenant: a mesma instalação do software serve várias instituições em paralelo, cada uma com os seus dados completamente isolados.

---

## Stack Tecnológica

| Camada | Tecnologia | Versão |
| --- | --- | --- |
| Runtime (backend) | Python | 3.13 |
| Framework web | Django | 5.0.6 |
| API REST | Django REST Framework | 3.15.2 |
| Autenticação | djangorestframework-simplejwt | 5.3.1 |
| Base de dados (dev) | SQLite | — |
| Base de dados (prod) | PostgreSQL | 16 |
| Frontend | HTML5 + CSS3 + ES6 (módulos nativos) | — |
| Deploy frontend | Vercel | — |
| Testes | pytest + pytest-django + factory-boy | — |

---

## Arquitectura Geral

### Separação backend / frontend

O backend é uma API REST pura — não serve HTML. O frontend é estático (ficheiros `.html`, `.css`, `.js`) que comunicam com o backend via `fetch()`. Não há framework de frontend (sem React, Vue, Angular), o que torna o código mais simples de aprender e manter.

### Multi-tenancy por Membership

O núcleo do sistema é o modelo `Membership`. Um utilizador (`User`) pode ter papéis diferentes em instituições diferentes:

```
User ──── Membership ──── Institution
              │
              └── role: admin | trainer | student
```

**Exemplo:** O mesmo utilizador pode ser formador no "Centro A" e estudante no "Centro B". Cada sessão está associada a uma instituição específica.

### Como o backend sabe a qual instituição pertence cada pedido

Cada pedido HTTP autenticado carrega dois cabeçalhos (headers):

1. `Authorization: Bearer <access_token>` — identifica o utilizador
2. `X-Institution-Id: <uuid>` — identifica a instituição activa

O middleware `MembershipJWTAuthentication` valida ambos e coloca `request.membership` disponível para todos os views. Os views nunca precisam de perguntar "a que instituição pertence este utilizador?" — a resposta já está em `request.membership.institution`.

---

## Estrutura do Backend

```
backend/
├── core/
│   ├── settings/
│   │   ├── base.py          ← Configuração comum a todos os ambientes
│   │   ├── development.py   ← SQLite, DEBUG=True, CORS aberto
│   │   └── production.py    ← PostgreSQL, CORS restrito, SMTP
│   ├── urls.py              ← Registo de todas as rotas da API
│   ├── permissions.py       ← IsAdminRole, IsTrainerRole, IsStudentRole
│   ├── exceptions.py        ← Handler global de erros (envelope padronizado)
│   ├── pagination.py        ← Paginação standard {count, pages, page, results}
│   └── mixins.py            ← PaginatedListMixin para views de listagem
└── apps/
    ├── accounts/            ← Utilizadores, Memberships, autenticação JWT
    ├── institutions/        ← Instituições, geração de códigos
    ├── students/            ← Perfis de estudantes
    ├── trainers/            ← Perfis de formadores
    ├── courses/             ← Cursos
    ├── classes/             ← Turmas e Inscrições (Enrollment)
    ├── grades/              ← Notas e avaliações
    └── notifications/       ← Notificações in-app por utilizador
```

Cada app segue a mesma estrutura interna: `models.py` → `serializers.py` → `services.py` → `views.py` → `urls.py` → `tests/`.

**Convenção:** toda a lógica de negócio vive em `services.py` (métodos estáticos). Os views são finos — apenas recebem o pedido, chamam o service e devolvem a resposta.

---

## Modelos de Dados

### User (`users`)

| Campo | Tipo | Notas |
| --- | --- | --- |
| `id` | UUID | Chave primária |
| `email` | EmailField único | Campo de login (USERNAME_FIELD). Utilizadores sem email real recebem placeholder `{code}@local.academico` |
| `full_name` | CharField | Gerido pelo admin |
| `is_active` | Boolean | |
| `must_change_password` | Boolean | Activado sempre na criação — obriga mudança no primeiro login |
| `is_staff` | Boolean | Acesso ao Django Admin |

### Membership (`memberships`)

| Campo | Notas |
| --- | --- |
| `user` + `institution` + `role` | Constraint de unicidade |
| `role` | `admin` / `trainer` / `student` |
| `is_active` | Pode ser revogada sem eliminar o utilizador |

### Institution (`institutions`)

Entidade raiz do sistema. Contém nome, slug único (URL-friendly), prefixo para geração de códigos (ex: `CIN`), província e contactos.

### Student (`students`)

Perfil de estudante. Ligado a um `User` via ForeignKey (não OneToOne — o mesmo utilizador pode ser estudante em várias instituições). Código formato: `{PREFIXO}{ANO}{SEQ:04d}` → ex: `CIN20260001`

### Trainer (`trainers`)

Perfil de formador. Mesma estrutura do Student. Código formato: `{PREFIXO}F{ANO}{SEQ:04d}` → ex: `CINF20260001`. O "F" distingue formadores de estudantes.

### Course (`courses`)

Curso pertencente a uma instituição. Código único por instituição. Ex: "Redes Informáticas" — código "RI".

### Class (`classes`)

Turma que liga Course + Trainer. Estados: `open` → `in_progress` → `closed`. Uma vez fechada, não aceita mais mutações.

### Enrollment (`enrollments`)

Liga um Student a uma Class. Estados: `active` / `dropped` / `completed`. Um estudante não pode estar inscrito duas vezes na mesma turma.

### Grade (`grades`)

Nota ligada a um Enrollment. Tipos de avaliação: `continuous` / `exam` / `practical` / `project` / `other`. Escala configurável (`value` / `max_value`). Apenas uma nota por tipo de avaliação por enrollment (constraint único).

### Notification (`notifications`)

| Campo | Tipo | Notas |
| --- | --- | --- |
| `id` | UUID | Chave primária |
| `user` | FK → User | Destinatário da notificação |
| `type` | CharField | `enrollment` / `grade` / `system` |
| `title` | CharField | Título curto da notificação |
| `message` | TextField | Corpo (opcional) |
| `is_read` | Boolean | `False` por defeito |
| `created_at` | DateTimeField | Preenchido automaticamente |

**Triggers automáticos:**

- Inscrição num aluno: notifica o formador responsável pela turma
- Nota lançada: notifica o aluno

---

## Sistema de Autenticação

### Login

O endpoint `POST /api/auth/login/` aceita **email ou código** (de estudante ou formador):

- Com `@` no valor → trata como email directamente
- Sem `@` → procura em `Student.student_code` e `Trainer.trainer_code` → resolve para o email (real ou placeholder) antes de autenticar

A resposta devolve:
```json
{
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>",
  "user": { "id", "email", "full_name", ... },
  "must_change_password": true/false,
  "memberships": [{ "institution_id", "institution_name", "role", ... }]
}
```

### Primeiro login

`must_change_password = true` sempre na criação de conta. O frontend detecta este flag e redireciona para `/pages/change-password.html` antes de permitir qualquer acesso.

### Utilizadores sem email

Comuns em Angola. O sistema cria um email placeholder `{codigo}@local.academico` internamente. A senha inicial é `pass123`. O placeholder nunca é exposto ao frontend (o serializer devolve `""` para esses casos).

### Tokens JWT

- **Access token:** curta duração, enviado em todos os pedidos
- **Refresh token:** longa duração, usado para renovar o access sem novo login
- **Logout:** faz blacklist do refresh token no backend (o token fica inválido mesmo que não tenha expirado)

---

## API — Endpoints Completa

### Autenticação — `/api/auth/`

| Método | Endpoint | Acesso | Descrição |
| --- | --- | --- | --- |
| POST | `/login/` | Público | Login por email ou código |
| POST | `/refresh/` | Público | Renovar access token |
| POST | `/logout/` | Auth | Invalidar refresh token |
| GET/PATCH | `/me/` | Auth | Dados do utilizador; PATCH actualiza email |
| GET | `/memberships/` | Auth | Listar Memberships activas |
| POST | `/change-password/` | Auth | Alterar palavra-passe |
| POST | `/password-reset/` | Público | Link de reset de senha por email |
| POST | `/password-reset/confirm/` | Público | Validar token e definir senha |

### Instituições — `/api/institutions/`

| Método | Endpoint | Acesso | Descrição |
| --- | --- | --- | --- |
| POST | `/register/` | Público | Auto-registo: cria instituição + admin + tokens |
| GET/PATCH | `/me/` | Auth | Dados da instituição activa; PATCH actualiza campos |

### Estudantes — `/api/students/`

| Método | Endpoint | Acesso | Descrição |
| --- | --- | --- | --- |
| GET | `/` | Admin/Trainer | Listar estudantes |
| POST | `/` | Admin | Criar estudante |
| GET | `/me/` | Student | O meu perfil |
| GET/PATCH/DELETE | `/<id>/` | Admin/Trainer | Detalhe, editar, desactivar |
| POST | `/<id>/reset-password/` | Admin | Reset de senha |

### Formadores — `/api/trainers/`

| Método | Endpoint | Acesso | Descrição |
| --- | --- | --- | --- |
| GET | `/` | Admin | Listar formadores |
| POST | `/` | Admin | Criar formador |
| GET | `/me/` | Trainer | O meu perfil |
| GET/PATCH/DELETE | `/<id>/` | Admin | Detalhe, editar, desactivar |
| POST | `/<id>/reset-password/` | Admin | Reset de senha |
| GET | `/<id>/classes/` | Admin | Turmas do formador |

### Cursos — `/api/courses/`

| Método | Endpoint | Acesso | Descrição |
| --- | --- | --- | --- |
| GET | `/` | Auth | Listar cursos |
| POST | `/` | Admin | Criar curso |
| GET/PATCH/DELETE | `/<id>/` | Admin | Detalhe, editar, desactivar |
| GET | `/<id>/classes/` | Auth | Turmas de um curso |

### Turmas — `/api/classes/`

| Método | Endpoint | Acesso | Descrição |
| --- | --- | --- | --- |
| GET | `/` | Auth | Listar turmas |
| POST | `/` | Admin | Criar turma |
| GET | `/my-enrollments/` | Student | As minhas inscrições |
| GET/PATCH/DELETE | `/<id>/` | Admin | Detalhe, editar, fechar |
| POST | `/<id>/close/` | Admin | Fechar turma |
| GET/POST | `/<id>/enrollments/` | Admin/Trainer | Inscrições de uma turma |
| PATCH/DELETE | `/<id>/enrollments/<eid>/` | Admin/Trainer | Gerir inscrição |

### Notas — `/api/grades/`

| Método | Endpoint | Acesso | Descrição |
| --- | --- | --- | --- |
| GET | `/` | Auth | Listar notas |
| POST | `/` | Trainer/Admin | Criar nota |
| GET | `/report/` | Admin/Trainer | Relatório de notas |
| GET | `/my-grades/` | Student | As minhas notas |
| PATCH/DELETE | `/<id>/` | Trainer/Admin | Editar/eliminar nota |
| GET | `/enrollment/<eid>/` | Auth | Notas de um enrollment |

### Notificações — `/api/notifications/`

| Método | Endpoint | Acesso | Descrição |
| --- | --- | --- | --- |
| GET | `/` | Auth | Lista recente + contagem de não lidas |
| POST | `/<id>/read/` | Auth | Marcar uma notificação como lida |
| POST | `/read-all/` | Auth | Marcar todas as notificações como lidas |

### Envelope de resposta padrão

**Lista:**
```json
{ "count": 42, "pages": 3, "page": 1, "next": "...", "previous": null, "results": [...] }
```

**Erro:**
```json
{ "error": true, "status_code": 400, "detail": "..." }
```

---

## Geração de Códigos

O `InstitutionService` gera automaticamente os códigos de estudante e formador:

- **Prefixo:** derivado do nome da instituição (iniciais das primeiras 3 palavras, ou 3 primeiras letras se nome simples). Ex: "Centro de Informática" → `CIN`
- **Estudante:** `{PREFIXO}{ANO}{SEQ:04d}` → `CIN20260001`
- **Formador:** `{PREFIXO}F{ANO}{SEQ:04d}` → `CINF20260001`
- A sequência procura o próximo número disponível (tolera gaps de deleções)
- O admin também pode definir o código manualmente

---

## Gestão de Palavras-passe

| Cenário | Comportamento |
| --- | --- |
| Criar student/trainer com email | Senha aleatória (`secrets.token_urlsafe(8)`), email de boas-vindas enviado |
| Criar student/trainer sem email | Senha `pass123`, sem email enviado |
| Admin reset de senha | Nova senha aleatória, email enviado, `must_change_password = True` |
| Qualquer novo utilizador | `must_change_password = True` — frontend obriga mudança no primeiro login |

---

## Estrutura do Frontend

```
frontend/
├── index.html               ← Landing page pública (PT/EN)
├── css/
│   ├── global.css           ← Design system: tokens, reset, tipografia, componentes
│   └── layout.css           ← Shell da app: sidebar, topbar, área de conteúdo
├── js/
│   ├── config.js            ← URL base da API
│   ├── api.js               ← Todas as chamadas HTTP (injecção de tokens, refresh automático)
│   ├── layout.js            ← Shell da app (sidebar, topbar, breadcrumb, auth guards)
│   └── i18n.js              ← Sistema de traduções PT/EN (808 linhas de dicionário)
└── pages/
    ├── login.html           ← Login por email ou código
    ├── change-password.html ← Mudança de senha obrigatória (primeiro login)
    ├── dashboard.html       ← Dashboard adaptado por papel (admin/trainer/student)
    ├── students.html        ← Gestão de estudantes (admin)
    ├── trainers.html        ← Gestão de formadores (admin)
    ├── courses.html         ← Gestão de cursos (admin)
    ├── classes.html         ← Gestão de turmas (admin/trainer)
    ├── grades.html          ← Gestão de notas (trainer/admin)
    ├── reports.html         ← Relatórios com gráficos (Chart.js) e impressão
    ├── profile.html         ← Perfil do utilizador (ver info + editar email)
    ├── register.html        ← Auto-registo de nova instituição (público)
    ├── forgot-password.html ← Pedido de recuperação de senha (público)
    ├── reset-password.html  ← Definir nova senha via token (público)
    ├── about.html           ← Sobre (estática)
    ├── contact.html         ← Contacto (estática)
    ├── privacy.html         ← Privacidade (estática)
    └── terms.html           ← Termos de uso (estática)
```

### api.js — Camada de Comunicação

Centraliza todas as chamadas à API. Gere automaticamente:
- Injecção do `Authorization: Bearer <token>` em todos os pedidos
- Injecção do `X-Institution-Id` em pedidos que requerem contexto institucional
- Refresh automático do access token quando expira (resposta 401)
- Logout automático se o refresh também falhar

### layout.js — Shell da Aplicação

Carrega a sidebar e topbar a partir de `components/shell.html`. Expõe:
- `requireAuth()` — redireciona para login se não há sessão
- `requireRole(role)` — redireciona se o papel activo não corresponde
- `setBreadcrumb(items)` — actualiza o breadcrumb da topbar
- `initLayout()` — chamado em todas as páginas autenticadas; aplica traduções automaticamente

### i18n.js — Internacionalização

Sistema de traduções PT/EN. Exporta `t(key)` para uso em JavaScript e `applyTranslations()` para atributos `data-i18n` no HTML. Persiste o idioma em `localStorage` (chave `academico_locale`). O idioma por defeito é Português.

### Estado de Sessão (localStorage)

| Chave | Conteúdo |
| --- | --- |
| `academico_token` | JWT access token |
| `academico_refresh` | JWT refresh token |
| `academico_institution` | UUID da instituição activa |
| `academico_user` | JSON com dados do utilizador |
| `academico_memberships` | JSON array de Memberships activas |
| `academico_role` | Papel activo (`admin`/`trainer`/`student`) |
| `academico_must_change_password` | `"true"` / `"false"` |
| `academico_locale` | `"pt"` ou `"en"` |

---

## Emails Automáticos

| Trigger | Destinatário | Conteúdo |
| --- | --- | --- |
| Criar student/trainer com email | Novo utilizador | Boas-vindas + código + senha temporária |
| Admin reset de senha | Utilizador | Nova senha temporária |
| Recuperação de senha (auto-serviço) | Utilizador | Link de reset válido 24h |

Utiliza `Django send_mail`. Em desenvolvimento usa o backend de consola (imprime no terminal). Em produção usa SMTP (Gmail ou outro configurado em `.env`).

---

## Testes Automatizados

```
backend/
└── apps/
    ├── accounts/tests/      ← 29 testes de serviço
    ├── institutions/tests/  ← 13 testes de serviço
    ├── students/tests/      ← 21 testes de serviço
    ├── trainers/tests/      ← 19 testes de serviço
    ├── courses/tests/       ← 15 testes de serviço
    ├── classes/tests/       ← 23 testes de serviço
    ├── grades/tests/        ← 19 testes de serviço
    └── notifications/tests/ ← 7 testes de serviço
```

**Total:** 143+ testes de serviço + testes HTTP de todos os endpoints
(94 adicionados na v0.3.0). Todos os testes passam a zero falhas.

**Executar:**
```bash
cd backend
pytest
```

---

## Iniciar em Desenvolvimento

```bash
# Backend
cd backend
.venv\Scripts\activate           # Windows
source .venv/bin/activate        # Linux/Mac
python manage.py runserver

# Frontend
cd frontend
python -m http.server 3000
```

**Credenciais de teste:** `cinfotec@edu.com` / senha definida na criação da instituição / instituição: CINFOTEC Huambo / papel: admin

---

## Funcionalidades Pendentes

| Feature | Estado |
| --- | --- |
| Página de perfil (ver/editar email) | Concluído (v0.4.2) |
| Recuperação de senha por email | Concluído (v0.4.3) |
| Notificações in-app | Concluído (v0.4.4) |
| Relatórios com gráficos + exportação CSV/PDF | Concluído (v0.4.5) |
| Auto-registo de instituição (self-service) | Concluído (v0.4.6) |
| Infra de deploy (Railway + Vercel + CI/CD) | Concluído (v0.4.6) |
| Controlo de presenças (sessões de aula) | Arquivado (baixa prioridade) |

---

## Histórico de Versões

Ver [CHANGELOG.md](CHANGELOG.md) para detalhes completos por versão.

| Versão | Data | Destaques |
| --- | --- | --- |
| v0.1.0 | 2026-02-05 | Estrutura base, todos os modelos, API inicial |
| v0.2.0 | 2026-03-09 | Services layer, paginação, testes, frontend completo |
| v0.3.0 | 2026-03-28 | Multi-tenancy (Membership), MembershipJWTAuthentication, 94 testes HTTP |
| v0.4.0 | 2026-04-21 | Geração de códigos, must_change_password, reset de senha, welcome emails |
| v0.4.1 | 2026-04-27 | i18n PT/EN, login por código, páginas estáticas (about/contact/privacy/terms) |
| v0.4.2 | 2026-04-27 | Página de perfil, PATCH /auth/me/ para editar email |
| v0.4.3 | 2026-04-27 | Recuperação de senha por email (token Django, silent 200) |
| v0.4.4 | 2026-04-27 | Notificações in-app (enrollment/grade triggers, painel no topbar) |
| v0.4.5 | 2026-04-27 | Página de relatórios com Chart.js, stats, impressão e export CSV/PDF |
| v0.4.6 | 2026-04-27 | Auto-registo de instituição, infra de deploy (Railway + Vercel + CI/CD) |

---

*Desenvolvido por PyNerd Development. Propriedade exclusiva — todos os direitos reservados.*
