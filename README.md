# Noto.ai 📝🧠

Your intelligent, AI-powered PDF research companion — powered locally by **LLaMA 3** via Ollama.

---

## 🌟 Overview

**Noto.ai** transforms static PDFs into **interactive, AI-narrated research companions**. Ask questions, summarize content, and interact naturally — all while keeping your AI engine **local and private** using Meta’s LLaMA 3 via [Ollama](https://ollama.com/).

<p align="center">
  <img src="https://img.shields.io/badge/Language-Python-blue?style=flat-square" />
  <img src="https://img.shields.io/badge/Framework-Kivy-red?style=flat-square&logo=streamlit" />
  <img src="https://img.shields.io/badge/Model-LLaMA%203-blueviolet?style=flat-square" />
</p>

---

## 🚀 Features

| Feature              | Description                                 |
| -------------------- | ------------------------------------------- |
| 📄 PDF Reader        | Upload and parse any PDF                    |
| 🤖 Chat with PDF     | Interact with your documents using LLaMA 3  |
| 🧠 Summarization     | AI-generated summaries of sections or pages |
| 📍 Search & Navigate | Quickly find terms and content              |
| 🌙 Dark Mode         | Kivy-powered user-friendly interface        |
| 🖥️ Works Offline    | No cloud required – local model inference   |

---

## 🛠️ Tech Stack

* **UI:** Python + Kivy + KivyMD
* **AI Backend:** LLaMA 3 via [Ollama](https://ollama.com)
* **PDF Parsing:** `PyMuPDF` (`fitz`)
* **Text-to-AI:** Local API calls to `http://localhost:11434/api/generate`

---

## 📦 Installation

### 🐍 Python Environment

```bash
git clone https://github.com/sagnikdatta2k6/noto-ai-app.git
cd noto-ai-app
pip install -r requirements.txt
```

### 🤖 Ollama Setup (LLaMA 3)

1. Install [Ollama](https://ollama.com)
2. Pull LLaMA 3 model:

   ```bash
   ollama pull llama3
   ```
3. Run the model:

   ```bash
   ollama run llama3
   ```

### ▶️ Run the App

```bash
python main.py
```

---

## ⚙️ .env Configuration (Optional)

If needed, configure `.env`:

```
OLLAMA_API_URL=http://localhost:11434
MODEL_NAME=llama3
```
---

## 🤝 Contributing

1. Fork the repo
2. `git checkout -b feature/improve-ui`
3. Make your changes
4. Submit a pull request ✨

---

## 📜 License

MIT License. See [LICENSE](LICENSE).

---

## 🙋‍♂️ Author

**Sagnik Datta**
🌐 [GitHub](https://github.com/sagnikdatta2k6)
