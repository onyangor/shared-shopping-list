# 🛒 Shared Shopping List App (w/ AI & Firebase)

A collaborative shopping list app built with **Streamlit**, integrated with **Firebase Realtime DB** and enhanced by **AI item generation via Cohere API**. It allows users to:
- Add items manually or generate them from natural language.
- Edit or delete items with instant Firebase sync.
- Export the list to Excel.
- Split total cost evenly.

---

## 🔧 Features

- ✅ Real-time Firebase syncing (add/edit/delete)
- ✅ Multi-currency support
- ✅ AI-powered shopping list generation
- ✅ Excel export
- ✅ Cost splitting
- ✅ Beautiful and simple Streamlit interface

---

## 🖥️ Live Demo

> [🚀 Try it here](https://share.streamlit.io/your-username/shopping-list-app)

---

## 📦 Setup Locally

### 1. Clone the repository

```bash
git clone https://github.com/your-username/shopping-list-app.git
cd shopping-list-app
```

### 2. Create a virtual environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add Firebase credentials

Create a `firebase_key.json` file in the project root using your Firebase Admin SDK key.

---

## 🚀 Run the App

```bash
streamlit run app.py
```

---

## 📤 Deployment

You can deploy this app using [Streamlit Cloud](https://streamlit.io/cloud):

1. Push this project to a GitHub repo.
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Connect your repo and deploy `app.py`.
4. Paste your Firebase credentials in the Secrets tab like this:

```toml
[firebase]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...==\n-----END PRIVATE KEY-----\n"
...
```

---

## 🤖 AI Model

Powered by [Cohere's](https://cohere.com) `command-r-plus` model to extract structured shopping lists from natural language.

---

## 🛡️ Security Notes

- Do **not** commit `firebase_key.json` publicly.
- Use Firebase security rules to restrict public access.
- You can enhance this app with Firebase Auth if needed.

---

## 🙌 Contributions

Pull requests welcome. For major changes, please open an issue first.

---

## 📜 License

MIT License