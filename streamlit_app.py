import streamlit as st
import sqlite3
from config import DB_PATH, USER_TABLE, USER_COLUMNS, USER_WEIGHT_TABLE, USER_WEIGHT_COLUMNS

# Connect to SQLite DB
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Generic fetch all rows from a table
def fetch_all(table):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table}")
    return cur.fetchall()

# Insert a row into a table
def insert_row(table, data):
    try:
        conn = get_connection()
        cur = conn.cursor()
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table} ({', '.join(data.keys())}) VALUES ({placeholders})"
        cur.execute(query, tuple(data.values()))
        conn.commit()
    except Exception as e:
        st.error(f"Error inserting into {table}: {e}")

# Update a row by primary key
def update_row(table, pk_name, pk_value, data):
    try:
        conn = get_connection()
        cur = conn.cursor()
        set_clause = ', '.join([f"{col}=?" for col in data])
        query = f"UPDATE {table} SET {set_clause} WHERE {pk_name} = ?"
        cur.execute(query, tuple(data.values()) + (pk_value,))
        conn.commit()
    except Exception as e:
        st.error(f"Error updating {table}: {e}")

# Delete a row by primary key
def delete_row(table, pk_name, pk_value):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {table} WHERE {pk_name} = ?", (pk_value,))
        conn.commit()
    except Exception as e:
        st.error(f"Error deleting from {table}: {e}")

def transfer_age(from_id, to_id, amount):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT age FROM {USER_TABLE} WHERE user_id = ?", (from_id,))
        from_age_result = cur.fetchone()
        cur.execute(f"SELECT age FROM {USER_TABLE} WHERE user_id = ?", (to_id,))
        to_age_result = cur.fetchone()

        if from_age_result is None or to_age_result is None:
            raise ValueError("One of the selected IDs does not exist.")

        from_age = from_age_result[0]
        to_age = to_age_result[0]

        if from_age < amount:
            raise ValueError("Insufficient age to transfer.")

        # Begin transaction
        cur.execute(f"UPDATE {USER_TABLE} SET age = age - ? WHERE user_id = ?", (amount, from_id))
        cur.execute(f"UPDATE {USER_TABLE} SET age = age + ? WHERE user_id = ?", (amount, to_id))
        conn.commit()
        return True, "Transfer successful."
    except Exception as e:
        conn.rollback()
        return False, f"Transfer failed: {e}"

# --- Streamlit UI ---
st.title("Gym Tracker CRUD App")

tab1, tab2 = st.tabs(["Users", "Weight Logs"])

with tab1:
    st.header("Manage Users")

    users = fetch_all(USER_TABLE)
    user_ids = [user["user_id"] for user in users]

    st.subheader("Existing Users")
    st.dataframe(users)

    st.subheader("Add New User")
    with st.form("add_user_form"):
        new_user = {col: st.text_input(f"{col}") for col in USER_COLUMNS}
        submitted = st.form_submit_button("Add User")
        if submitted:
            if all(new_user.values()):
                insert_row(USER_TABLE, new_user)
                st.success("User added!")
            else:
                st.error("Please fill in all fields.")

    if users:
        st.subheader("Update User")
        selected_user_id = st.selectbox("Select User ID to update", user_ids)
        selected_user = next((u for u in users if u["user_id"] == selected_user_id), None)
        if selected_user:
            with st.form("update_user_form"):
                updated_user = {
                    col: st.text_input(col, value=selected_user[col]) for col in USER_COLUMNS
                }
                updated = st.form_submit_button("Update User")
                if updated:
                    update_row(USER_TABLE, "user_id", selected_user_id, updated_user)
                    st.success("User updated!")

        st.subheader("Delete User")
        delete_user_id = st.selectbox("Select User ID to delete", user_ids, key="delete_user")
        if st.button("Delete User"):
            delete_row(USER_TABLE, "user_id", delete_user_id)
            st.warning("User deleted!")

        # --- Transaction: Transfer Age ---
        st.subheader("Transfer Age Between Users (Transactional)")

        # Create name-to-id and id-to-name mappings
        name_id_map = {f"{user['user_name']} (ID {user['user_id']})": user['user_id'] for user in users}
        id_name_map = {user['user_id']: user['user_name'] for user in users}
        id_age_map = {user['user_id']: user['age'] for user in users}

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

with tab2:
    st.header("Manage Weight Logs")

    weights = fetch_all(USER_WEIGHT_TABLE)
    weight_ids = [w["weight_log_id"] for w in weights]

    st.subheader("Existing Weight Logs")
    st.dataframe(weights)

    st.subheader("Add New Weight Log")
    with st.form("add_weight_form"):
        # Map user names to IDs for selection
        user_map = {f"{u['user_name']} (ID {u['user_id']})": u['user_id'] for u in users}
        selected_user = st.selectbox("Select User", list(user_map.keys()))
        new_weight_log = {
            "user_id": user_map[selected_user],
            "weight": st.number_input("Weight (lbs/kg)", min_value=0.0, format="%.2f"),
            "date": st.date_input("Date").isoformat(),
        }
        submitted = st.form_submit_button("Add Weight Log")
        if submitted:
            insert_row(USER_WEIGHT_TABLE, new_weight_log)
            st.success("Weight log added!")

    if weights:
        st.subheader("Update Weight Log")
        selected_weight_id = st.selectbox("Select Weight Log ID to update", weight_ids)
        selected_weight = next((w for w in weights if w["weight_log_id"] == selected_weight_id), None)
        if selected_weight:
            with st.form("update_weight_form"):
                updated_weight = {
                    "user_id": st.selectbox("User", list(user_map.keys()),
                                            index=list(user_map.values()).index(selected_weight["user_id"])),
                    "weight": st.number_input("Weight (lbs/kg)", value=selected_weight["weight"], format="%.2f"),
                    "date": st.date_input("Date", value=selected_weight["date"]),
                }
                # Convert selected user back to user_id
                updated_weight["user_id"] = user_map[updated_weight["user_id"]]

                updated = st.form_submit_button("Update Weight Log")
                if updated:
                    update_row(USER_WEIGHT_TABLE, "weight_log_id", selected_weight_id, updated_weight)
                    st.success("Weight log updated!")

        st.subheader("Delete Weight Log")
        delete_weight_id = st.selectbox("Select Weight Log ID to delete", weight_ids, key="delete_weight")
        if st.button("Delete Weight Log"):
            delete_row(USER_WEIGHT_TABLE, "weight_log_id", delete_weight_id)
            st.warning("Weight log deleted!")




