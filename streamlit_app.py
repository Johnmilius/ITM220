import streamlit as st
import sqlite3
from config import DB_PATH, TABLE_NAME, COLUMNS

# Connect to SQLite DB
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
    return sqlite3.connect(DB_PATH)

def fetch_all():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {TABLE_NAME}")
    return cur.fetchall()

def insert_row(data):
    try:
        conn = get_connection()
        cur = conn.cursor()
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {TABLE_NAME} ({', '.join(data.keys())}) VALUES ({placeholders})"
        cur.execute(query, tuple(data.values()))
        conn.commit()
    except Exception as e:
        st.error(f"Error inserting data: {e}")

def update_row(id_val, data):
    try:
        conn = get_connection()
        cur = conn.cursor()
        set_clause = ', '.join([f"{col}=?" for col in data])
        query = f"UPDATE {TABLE_NAME} SET {set_clause} WHERE id = ?"
        cur.execute(query, tuple(data.values()) + (id_val,))
        conn.commit()
    except Exception as e:
        st.error(f"Error updating data: {e}")

def delete_row(id_val):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {TABLE_NAME} WHERE id = ?", (id_val,))
        conn.commit()
    except Exception as e:
        st.error(f"Error deleting data: {e}")

def transfer_age(from_id, to_id, amount):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT age FROM {TABLE_NAME} WHERE id = ?", (from_id,))
        from_age = cur.fetchone()[0]
        cur.execute(f"SELECT age FROM {TABLE_NAME} WHERE id = ?", (to_id,))
        to_age = cur.fetchone()[0]

        if from_age is None or to_age is None:
            raise ValueError("One of the selected IDs does not exist.")

        if from_age < amount:
            raise ValueError("Insufficient age to transfer.")

        # Begin transaction
        cur.execute(f"UPDATE {TABLE_NAME} SET age = age - ? WHERE id = ?", (amount, from_id))
        cur.execute(f"UPDATE {TABLE_NAME} SET age = age + ? WHERE id = ?", (amount, to_id))
        conn.commit()
        return True, "Transfer successful."
    except Exception as e:
        conn.rollback()
        return False, f"Transfer failed: {e}"

# --- Streamlit UI ---
st.title(f"CRUD App for '{TABLE_NAME}' Table")

rows = fetch_all()
st.subheader("Existing Records")
st.dataframe(rows)

# --- Add New Record ---
st.subheader("Add New Record")
with st.form("add_form"):
    new_data = {col: st.text_input(f"{col}") for col in COLUMNS}
    submitted = st.form_submit_button("Add")
    if submitted:
        insert_row(new_data)
        st.success("Record added!")

# --- Update Record ---
if rows:
    st.subheader("Update Existing Record")
    row_ids = [row['id'] for row in rows]
    selected_id = st.selectbox("Select ID to update", row_ids)
    selected_row = next((row for row in rows if row['id'] == selected_id), None)

    if selected_row:
        with st.form("update_form"):
            updated_data = {
                col: st.text_input(f"{col}", value=str(selected_row[col])) 
                for col in COLUMNS
            }
            updated = st.form_submit_button("Update")
            if updated:
                update_row(selected_id, updated_data)
                st.success("Record updated!")

    # --- Delete Record ---
    st.subheader("Delete Record")
    delete_id = st.selectbox("Select ID to delete", row_ids, key="delete")
    if st.button("Delete"):
        delete_row(delete_id)
        st.warning("Record deleted.")

    
# --- Transaction: Transfer Age ---
st.subheader("Transfer Age Between Users (Transactional)")

# Create name-to-id and id-to-name mappings
name_id_map = {f"{row['name']} (ID {row['id']})": row['id'] for row in rows}
id_name_map = {row['id']: row['name'] for row in rows}
id_age_map = {row['id']: row['age'] for row in rows}

from_name = st.selectbox("From (User)", list(name_id_map.keys()), key="from_user")
to_name_options = [n for n in name_id_map.keys() if n != from_name]
to_name = st.selectbox("To (User)", to_name_options, key="to_user")

from_id = name_id_map[from_name]
to_id = name_id_map[to_name]

st.markdown(f"**{id_name_map[from_id]}'s current age:** {id_age_map[from_id]}")
st.markdown(f"**{id_name_map[to_id]}'s current age:** {id_age_map[to_id]}")

amount = st.number_input("How many years to transfer (subtract from sender and add to recipient)", min_value=1, step=1)

if st.button("Transfer Age"):
    success, msg = transfer_age(from_id, to_id, amount)
    if success:
        st.success(msg)
    else:
        st.error(msg)

# ---

