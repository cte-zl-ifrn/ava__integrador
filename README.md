# AVA - Portal

O AVA-Portal é um middleware integrador entre SUAP e Moodle, além disso, também tem um dashboard com todos os cursos e inscrições que integrou, desta forma cada usuário tem acesso aos cursos/diários em que está inscrito sem precisar procurar em vários Moodles.

Neste projeto, além do AVA-Portal, foi colocado um Fake SUAP, para emular o funcionado da integraçãod o SUAP ou outro sistema acadêmico, e um par de Moodles (ZL e Presencial), para emular o cenário de ter mais um Moodle a integrar.

> Neste projeto usamos o [Docker](https://docs.docker.com/engine/install/) e o [Docker Compose Plugin](https://docs.docker.com/compose/install/compose-plugin/#:~:text=%20Install%20the%20plugin%20manually%20%F0%9F%94%97%20%201,of%20Compose%20you%20want%20to%20use.%20More%20) (não o [docker-compose](https://docs.docker.com/compose/install/) 😎). O setup foi todo testado usando o Linux e Mac OS.

> Os containeres terão o prefixo `ism-`, que é um acrônimo para "Integrador Suap Moodle".

## Como funciona

**Como desenvolvedor** - no `local_settings.py` do SUAP configure as variáveis (`MOODLE_SYNC_URL` e `MOODLE_SYNC_TOKEN`), no AVA-Portal configure o mesmo token que você configurou no SUAP. Para cada  Moodle a ser integrado instale o plugin `auth_suap` e cadastre no AVA-Portal como um "Ambiente". 

**Como usuário** - no SUAP, o secretário acadêmico autoriza cada diário a ser integrado ao Moodle, na página do diário no SUAP o professor clica em "Sincronizar" e a mágica se faz, ou seja, o SUAP envia para o AVA-Portal que, com base na sigla do campus, decide para qual Moodle encaminhar a requisição de integração, o Moodle cadastra/atualiza as categorias (Campus, Diário, Semestre, Turma), o curso, os pólos como grupos do curso e os professores e alunos, então inscreve os professores (Formador e Tutor) e os alunos, por fim, arrola os alunos nos grupos de seus respectivos pólos.

As variáveis de ambiente no SUAP têm as seguintes definições:
- `MOODLE_SYNC_URL` - URL do AVA-Portal
- `MOODLE_SYNC_TOKEN` - o token deve ser o mesmo que você vai configurar ao cadastrar o SUAP no AVA-Portal, é usada para autenticação do SUAP, guarde segredo desta chave.

## Como iniciar o desenvolvimento

Este docker-compose assume que você não tenha aplicações rodando na porta 80, ou seja, pare o serviço que está na porta 80 ou faça as configurações necessárias vocês mesmo. O script `_/deploy` já cria automaticamente uma entrada no /etc/hosts, caso não exista, que aponta para localhost. Isso é necessário para simplificar o cenário de desenvolvimento local.

```bash
mkdir ava
cd ava


# Baixe o projeto
git clone git@github.com:cte-zl-ifrn/portal__ava.git portal__ava 

cd portal__ava

# Baixa as dependencias, instala o sistema, um suap fake e 1 moodle para teste
_/deploy


# Se você usa o VSCode
code portal__ava.code-workspace

```

> O **Portal** estará disponível em http://ava/painel, o primeiro usuário a acessar será declarado como superusuário e poderá fazer tudo no sistema.

> O **Moodle** estará disponível em http://ava/, o usuário/senha do administrador serão admin/admin.

Caso você deseje fazer debug da AVA-Portal, tente:

```bash
_/portal/down
_/portal/debug
```

## oAuth2 do SUAP

- É obrigatório ao menos um dos escopos `identificacao` ou `email`, os quais retornam os atributos:
  - `identificacao` - NUMÉRICO - **é o IFid do usuário**, no caso: matrícula para alunos ou servidores e CPF para demais colaboradores
  - `nome_social` - ALFANUMÉRICO - **nome social**, este é o informado pelo indivíduo, não se trata de apelido, mas sim de nome social, conforme legislação
  - `nome_usual` - ALFANUMÉRICO - **nome usual**, escolhido pelo indivíduo na interface do SUAP
  - `nome_registro` - ALFANUMÉRICO - **nome civil**, este é conforme está no registro civil do indivíduo
  - `nome` - ALFANUMÉRICO - **nome completo**, para compatibilidade com APIs que não sabem tratar nome e sobrenome separados
  - `primeiro_nome` - ALFANUMÉRICO - **primeiro nome**, para compatibilidade com APIs que não sabem tratar nome e sobrenome juntos
  - `ultimo_nome` - ALFANUMÉRICO - **último nome**, para compatibilidade com APIs que não sabem tratar nome e sobrenome juntos
  - `campus` - ALFANUMÉRICO - **sigla do campus** do aluno ou servidor, caso exista, não se aplica aos demais colaboradores
  - `email_preferencial` - EMAIL - **email preferencial** para comunicação, caso exista, para servidores é o mesmo que o `email`, para alunos e demais colaboradores `email_secundario`, salvo se a instituição tiver criado um mecanismo que permita ao usuário escolher qual é seu email preferencial.
  - `email` - EMAIL - **email do servidor**, caso exista, apenas para servidores
  - `email_secundario` - EMAIL - **email pessoal**, caso exista, o mesmo usado para recuperação de senha, para todos
  - `email_google_classroom` - EMAIL - **email do Google Suite**, caso exista, apenas para alunos e servidores
  - `email_academico` - EMAIL - **email da Microsoft 365**, caso exista, apenas para alunos e servidores
  - `foto` - URL - **URL da foto no SUAP**, assim poderá ser usada a mesma foto em todos os ambientes
- Já o escopo `documentos_pessoais` retorna os atributos:
  - `cpf` - NUMÉRICO - **CPF** do indivíduo, útil para os casos de integração com gov.br ou para informar que possui outras contas no sistema. Poderá ser necessário novo login para trocar de conta.
  - `data_de_nascimento` - DATA - **data de nascimento**, ajuda a identificar indivíduos menos de idade, entre outros
  - `sexo` - ALFANUMÉRICO - **sexo**
  - No futuro poderá retornar dados de **necessidades especiais**, assim os sistemas já adaptarão as interfaces a estas necessidades.


## Screenshots

O design ficará como os designs [web](https://xd.adobe.com/view/00dc014e-8919-47ad-ab16-74ac81ca0c2a-558f/) e [mobile](https://xd.adobe.com/view/28b2f455-b115-4363-954f-77b5bcf1dba1-7de1/).

### v4 - Melhorias na UX

#### Desktop
![screenshot](docs/images/screenshot.v4.png)

#### Mobile
![screenshot](docs/images/screenshot.mobile.v4.png)

### v3 - Uso comum por aluno, tutor e professor

#### Desktop
![screenshot](docs/images/screenshot.v3.jpg)

#### Mobile
![screenshot](docs/images/screenshot.mobile.v3.png)

### v2 - Hiper focado no aluno

#### Desktop
![screenshot](screenshot.v2.png)

### v1 - Esforço urgente, sem projeto de UX

#### Desktop
![screenshot](screenshot.v1.png)

## Plugins previstos

1. suap sync (local)
   1. importar as inscrições (alunos e professores) dos diários
   2. exportar as presenças dos alunos
   3. exportar as notas dos alunos
2. suap attendances (block)
   1. configurar o modelo de cálculo de presenças
   2. permitir que os professores visualizem as presenças
   3. permitir que os alunos visualizem as presenças
3. suap auth (auth)
   1. autênticar usando o oauth do SUAP
   2. auto inscrever os alunos ao fazer login


## Tipo de commits

- `feat:` novas funcionalidades.
- `fix:` correção de bugs.
- `refactor:` refatoração ou performances (sem impacto em lógica).
- `style:` estilo ou formatação de código (sem impacto em lógica).
- `test:` testes.
- `doc:` documentação no código ou do repositório.
- `env:` CI/CD ou settings.
- `build:` build ou dependências.

