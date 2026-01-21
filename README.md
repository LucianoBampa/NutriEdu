# 🥗 NutriEdu AI

Plataforma educacional interativa baseada em Inteligência Artificial para **educação nutricional e socioemocional de crianças e adolescentes (3 a 18 anos)**.

O NutriEdu AI combina **IA generativa**, **Streamlit** e **visão computacional** para apoiar alunos, professores e instituições no desenvolvimento de hábitos saudáveis, bem-estar emocional e aprendizagem significativa.

---

## 🎯 Objetivo do Projeto

Auxiliar estudantes a:
- Compreender melhor suas emoções
- Avaliar hábitos alimentares de forma simples e acessível
- Receber sugestões nutricionais adequadas à idade
- Desenvolver autonomia, autoconsciência e bem-estar

E apoiar professores com:
- Painéis cognitivos e emocionais
- Ferramentas de acompanhamento pedagógico

---

## 🚀 Funcionalidades Principais

### 🧠 IA Emocional
- Detecção de estado emocional (foco / distração / cansaço)
- Baseada em visão computacional (MediaPipe)
- Feedback em linguagem simples

### 🥗 IA Nutricional
- Avaliação de lanches digitados pelo aluno
- Classificação: **Saudável / Moderado / Não recomendado**
- Sugestões acessíveis e educativas

### 👩‍🏫 Painel do Professor
- Visualização geral do estado emocional e cognitivo
- Apoio à tomada de decisão pedagógica

### 📊 Avaliação Educacional
- Análise integrada do desempenho e bem-estar

---

## 🧱 Arquitetura do Projeto

```
NutriEdu/
│── app.py                  # Aplicação principal (Streamlit)
│── nutri_ai.py              # IA Nutricional (OpenAI)
│── emocao.py                # Análise emocional (MediaPipe)
│── database.py              # Persistência local (SQLite)
│── requirements.txt
│── README.md
│── .env
│
├── pages/
│   ├── 01_IA_Emocional.py
│   ├── 02_IA_Tutora.py
│   ├── 03_IA_Nutricional.py
│   ├── 04_Painel_Cognitivo.py
│   ├── 05_Painel_Professor.py
│   └── 07_IA_Avaliacao.py
│
├── images/
│   ├── logo1.png
│   └── ilustracao.png
│
└── venv/
```

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.9+**
- **Streamlit** (interface web)
- **OpenAI API** (IA generativa)
- **MediaPipe** (visão computacional)
- **SQLite** (armazenamento local)
- **VS Code + Pylance + Flake8**

---

## ⚙️ Como Executar Localmente

### 1️⃣ Clonar o repositório
```bash
git clone https://github.com/seu-usuario/NutriEdu.git
cd NutriEdu
```

### 2️⃣ Criar e ativar ambiente virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3️⃣ Instalar dependências
```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar variáveis de ambiente
Crie um arquivo `.env`:
```
OPENAI_API_KEY=sua_chave_aqui
```

### 5️⃣ Executar aplicação
```bash
streamlit run app.py
```

---

## 🔐 Segurança

- Nenhum dado sensível é armazenado em nuvem
- Chaves protegidas via `.env`
- Projeto educacional, sem fins clínicos

---

## 📚 Público-Alvo

- Crianças e adolescentes (3 a 18 anos)
- Professores e educadores
- Escolas e projetos educacionais

---

## 📌 Status do Projeto

✅ MVP funcional
✅ Pronto para deploy no Streamlit Cloud
🚧 Em evolução contínua

---

## 👨‍💻 Autor

**Luciano Bampa Vieira**  
Projeto educacional com foco em IA aplicada à educação e saúde.

---

## 📄 Licença

Este projeto é de uso educacional e acadêmico.

