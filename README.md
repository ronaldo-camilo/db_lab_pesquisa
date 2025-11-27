# Sistema de Gerenciamento de Pesquisa Médica - TCC

Sistema Django para gerenciar dados de pesquisa médica com 3 tipos de planilhas: Amostras Biológicas, Bioinformática e Dados Clínicos.

## 🎯 Funcionalidades

- ✅ **Detecção inteligente de duplicatas** usando Nome, Data de Nascimento e Nome da Mãe
- ✅ **Upload de planilhas Excel e CSV** com processamento automático
- ✅ **Sistema de resolução de conflitos** quando dados divergem
- ✅ **Entrada manual de dados** via formulário web
- ✅ **Exportação** em Excel, CSV e PDF
- ✅ **Interface moderna** com Bootstrap 5
- ✅ **Dashboard** com estatísticas

## 📋 Requisitos

- Python 3.8+
- Django 4.2+
- Pandas, OpenpyXL, ReportLab

## 🚀 Instalação

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Executar migrações

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Criar superusuário (admin)

```bash
python manage.py createsuperuser
```

### 4. Executar servidor

```bash
python manage.py runserver
```

Acesse: http://localhost:8000

## 📊 Como Usar

### Upload de Planilhas

1. Acesse **Upload Planilhas** no menu
2. Selecione arquivo Excel (.xlsx) ou CSV
3. Escolha o tipo (ou deixe detectar automaticamente)
4. O sistema processará e notificará sobre:
   - Novos pacientes criados
   - Dados atualizados
   - Conflitos encontrados

### Resolução de Conflitos

Quando houver dados divergentes:
1. Acesse **Conflitos** no menu
2. Compare os valores existentes vs novos
3. Escolha qual manter
4. Confirme as alterações

### Exportação de Dados

1. Acesse **Exportar Dados**
2. Escolha o formato (Excel, CSV ou PDF)
3. Aplique filtros opcionais
4. Clique em "Gerar e Baixar"

## 🗂️ Estrutura do Banco de Dados

O modelo `Paciente` unifica todos os campos das 3 planilhas:

**Campos Principais (Obrigatórios):**
- Nome do Paciente
- Data de Nascimento
- Nome da Mãe

**Outros Campos:**
- Identificação (CPF, RG, ID Projeto, etc.)
- Amostras Biológicas (DNA, RNA, Sangue, Plasma, etc.)
- Bioinformática (Metiloma, Exoma, RNA-Seq, etc.)
- Dados Clínicos (CARS, QI, Históricos, etc.)

## 🔧 Administração

Acesse o painel admin em: http://localhost:8000/admin

Login com as credenciais do superusuário criado.

## 📁 Estrutura do Projeto

```
TCC/
├── pacientes/              # App principal
│   ├── models.py          # Modelos Paciente e ConflitoDados
│   ├── views.py           # Views para CRUD e processamento
│   ├── forms.py           # Formulários
│   ├── utils.py           # Funções de importação
│   └── templates/         # Templates HTML
├── pesquisa_medica/       # Configurações Django
├── manage.py
├── requirements.txt
└── README.md
```

## 💡 Lógica de Processamento

### Caso Negativo (Paciente Novo)
- Sistema cria novo registro com todos os dados

### Caso Positivo (Paciente Existente)
- Campos vazios são preenchidos automaticamente
- Campos iguais são ignorados

### Caso Especial (Conflito)
- Sistema detecta divergência
- Cria registro de conflito
- Usuário decide qual valor manter

## 🎨 Interface

Interface moderna com:
- Sidebar de navegação
- Dashboard com estatísticas
- Tabelas responsivas
- Formulários organizados por seções
- Alertas e notificações
- Bootstrap 5 + Bootstrap Icons

## 📝 Licença

Projeto acadêmico - TCC

