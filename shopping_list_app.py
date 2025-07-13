import streamlit as st
import cohere
import pandas as pd
import re
import json
import io
import firebase_admin
import firebase_admin
from firebase_admin import credentials, db, initialize_app



# Read the JSON string from secrets and parse it
firebase_json = json.loads(st.secrets["FIREBASE_KEY"])

# Use credentials from dict directly
cred = credentials.Certificate(firebase_json)
initialize_app(cred)


# -------------------- CONFIG --------------------
COHERE_API_KEY = "pY0RWQCBSdpAOvDnWaj34UJmlcouxIcagE6ej5uG"
FIREBASE_CRED_PATH = "firebase_key"
FIREBASE_DB_URL = "https://vibe-dd050-default-rtdb.firebaseio.com"

# -------------------- INIT FIREBASE --------------------
firebase_json = json.loads(st.secrets["FIREBASE_KEY"])
if not firebase_admin._apps:
    # Note: Include the databaseURL if you are using the Firebase Realtime Database
    cred = credentials.Certificate(firebase_json)
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://vibe-dd050-default-rtdb.firebaseio.com"
    })

# Create a database reference
db_ref = db.reference('/shopping_list')


# -------------------- STREAMLIT SETUP --------------------
st.set_page_config(page_title="Shared Shopping List", layout="centered")
st.title("🛒 Shared Shopping List with Cost Split + AI + Firebase")

# -------------------- SESSION STATE --------------------
if "item_list" not in st.session_state:
    st.session_state.item_list = []
if "firebase_keys" not in st.session_state:
    st.session_state.firebase_keys = []

# -------------------- MULTI-CURRENCY --------------------
currency = st.selectbox("Select currency", ["KES", "USD", "EUR", "GBP"])
symbol_map = {"KES": "KSh", "USD": "$", "EUR": "€", "GBP": "£"}
symbol = symbol_map[currency]

# -------------------- MANUAL ITEM ENTRY --------------------
st.subheader("➕ Add Items Manually")
item = st.text_input("Item name")
price = st.number_input(f"Price ({currency})", step=1.0, min_value=0.0)

if st.button("Add Item"):
    if item and price:
        entry = {"name": item, "price": price, "currency": currency}
        st.session_state.item_list.append(entry)
        if db_ref:
            fb_key = db_ref.push(entry).key
            st.session_state.firebase_keys.append(fb_key)
        else:
            st.session_state.firebase_keys.append(None)
        st.success(f"✅ Added: {item} - {symbol} {price}")

# -------------------- DISPLAY LIST WITH EDIT/DELETE --------------------
st.subheader("🧾 Current Shopping List")
total = sum(i["price"] for i in st.session_state.item_list)
count = len(st.session_state.item_list)
split = total / count if count > 0 else 0

for idx, item in enumerate(st.session_state.item_list):
    col1, col2, col3 = st.columns([0.5, 0.3, 0.2])
    with col1:
        new_name = st.text_input(f"Name {idx}", value=item["name"], key=f"name_{idx}")
    with col2:
        new_price = st.number_input(f"Price {idx}", value=item["price"], key=f"price_{idx}")
    with col3:
        if st.button("💾 Save", key=f"save_{idx}"):
            st.session_state.item_list[idx]["name"] = new_name
            st.session_state.item_list[idx]["price"] = new_price
            fb_key = st.session_state.firebase_keys[idx]
            if db_ref and fb_key:
                db_ref.child(fb_key).update({"name": new_name, "price": new_price})
            st.success(f"✅ Updated: {new_name}")
        if st.button("❌ Delete", key=f"delete_{idx}"):
            fb_key = st.session_state.firebase_keys.pop(idx)
            deleted = st.session_state.item_list.pop(idx)
            if db_ref and fb_key:
                db_ref.child(fb_key).delete()
            st.success(f"🗑️ Deleted: {deleted['name']}")
            st.experimental_rerun()

st.markdown("---")
st.write(f"**Total**: {symbol} {total:.2f}")
st.write(f"**Split (per item)**: {symbol} {split:.2f}")

# -------------------- AI ITEM GENERATION --------------------
st.markdown("### 🤖 Generate items from natural language")
text = st.text_area("Try: 'Buy 2 milk, rice, and bread under 500'")

if st.button("Generate with AI"):
    co = cohere.Client(COHERE_API_KEY)

    prompt = f"""
You are an assistant that helps convert natural language shopping instructions into a list of items with prices in {currency}.
Format:
- Milk (2): {symbol}80
- Rice: {symbol}250
- Bread: {symbol}100

Text: {text}
"""

    with st.spinner("Thinking..."):
        response = co.generate(
            model='command-r-plus',
            prompt=prompt,
            max_tokens=200,
            temperature=0.4,
        )

    ai_output = response.generations[0].text.strip()
    st.markdown("#### 🧠 AI-Generated Items")
    st.code(ai_output, language="markdown")

    # -------------------- PARSE & ADD --------------------
    lines = ai_output.split("\n")
    for line in lines:
        line = line.strip()
        match = re.match(r"-\s*(.+?)(?:\s*\((\d+)\))?:\s*(?:KSh|\$|€|£)?\s*([\d.]+)", line)
        if match:
            name = match.group(1).strip()
            quantity = int(match.group(2)) if match.group(2) else 1
            try:
                unit_price = float(match.group(3))
                for _ in range(quantity):
                    entry = {"name": name, "price": unit_price, "currency": currency}
                    st.session_state.item_list.append(entry)
                    if db_ref:
                        fb_key = db_ref.push(entry).key
                        st.session_state.firebase_keys.append(fb_key)
                    else:
                        st.session_state.firebase_keys.append(None)
                st.success(f"✅ Added: {name} x{quantity} - {symbol}{unit_price}")
            except ValueError:
                st.warning(f"Skipped: {line} — invalid price format.")
        else:
            st.warning(f"Skipped: {line} — could not parse.")

# -------------------- EXPORT TO EXCEL --------------------
st.markdown("### 📦 Export List")
if st.button("Download Excel"):
    df = pd.DataFrame(st.session_state.item_list)
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Shopping List")
    st.download_button("📥 Download Excel", data=excel_buffer.getvalue(), file_name="shopping_list.xlsx")

# -------------------- FIREBASE VIEW (Editable) --------------------
if db_ref:
    st.markdown("### 🔥 Synced with Firebase Realtime DB (Editable)")
    try:
        firebase_data = db_ref.get()
        if firebase_data:
            for key, item in firebase_data.items():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])

                with col1:
                    new_name = st.text_input(f"Name_{key}", item["name"], key=f"name_{key}")

                with col2:
                    new_price = st.number_input(f"Price_{key}", value=item["price"], key=f"price_{key}")

                with col3:
                    new_currency = st.selectbox(
                        f"Currency_{key}", ["KES", "USD", "EUR", "GBP"],
                        index=["KES", "USD", "EUR", "GBP"].index(item["currency"]),
                        key=f"currency_{key}"
                    )

                with col4:
                    if st.button("💾 Save", key=f"save_{key}"):
                        db_ref.child(key).update({
                            "name": new_name,
                            "price": new_price,
                            "currency": new_currency
                        })
                        st.success(f"✅ Updated: {new_name}")
                        st.experimental_rerun()

                with col5:
                    if st.button("❌ Delete", key=f"delete_{key}"):
                        db_ref.child(key).delete()
                        st.warning(f"🗑️ Deleted: {item['name']}")
                        st.experimental_rerun()
        else:
            st.info("No Firebase data found.")
    except Exception as e:
        st.error(f"Firebase read error: {e}")
