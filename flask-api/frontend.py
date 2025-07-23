import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:5000/users"

st.set_page_config(page_title="User Dashboard", layout="centered")

st.title("👨‍💼 User Management Dashboard")

# Load user data
@st.cache_data(ttl=1)
def load_users():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json().get("users", [])
    return []

def refresh_users():
    st.session_state['users'] = load_users()

# Initialize session state
if 'users' not in st.session_state:
    refresh_users()

st.sidebar.header("📋 Menu")
menu = st.sidebar.radio("Navigate", ["View Users", "Add User", "Edit User", "Delete User"])

if menu == "View Users":
    st.subheader("📊 Current Users")
    users_df = pd.DataFrame(st.session_state['users'])
    if not users_df.empty:
        st.dataframe(users_df[['id', 'name', 'age']], use_container_width=True)
    else:
        st.info("No users found.")

elif menu == "Add User":
    st.subheader("➕ Add New User")
    with st.form("add_user_form"):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=0)
        submit = st.form_submit_button("Add User")

        if submit:
            if name and age:
                res = requests.post(API_URL, json={"name": name, "age": age})
                if res.status_code == 201:
                    st.success("User added successfully!")
                    refresh_users()
                else:
                    st.error(res.json().get("error", "Unknown error"))
            else:
                st.warning("Please enter all fields.")

elif menu == "Edit User":
    st.subheader("✏️ Edit Existing User")
    user_list = {u['name']: u['id'] for u in st.session_state['users']}
    selected = st.selectbox("Select User", list(user_list.keys()))

    if selected:
        user_id = user_list[selected]
        user_data = next((u for u in st.session_state['users'] if u['id'] == user_id), None)

        with st.form("edit_form"):
            new_name = st.text_input("Name", value=user_data['name'])
            new_age = st.number_input("Age", min_value=0, value=user_data['age'])
            update = st.form_submit_button("Update User")

            if update:
                res = requests.put(f"{API_URL}/{user_id}", json={"name": new_name, "age": new_age})
                if res.status_code == 200:
                    st.success("User updated!")
                    refresh_users()
                else:
                    st.error(res.json().get("error", "Failed to update"))

elif menu == "Delete User":
    st.subheader("🗑️ Delete User")
    user_list = {u['name']: u['id'] for u in st.session_state['users']}
    selected = st.selectbox("Select User to Delete", list(user_list.keys()))

    if st.button("Delete"):
        user_id = user_list[selected]
        res = requests.delete(f"{API_URL}/{user_id}")
        if res.status_code == 200:
            st.success("User deleted")
            refresh_users()
        else:
            st.error("Error deleting user")