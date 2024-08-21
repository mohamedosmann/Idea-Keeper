import streamlit as st
import bcrypt

# Initialize session state for users, ideas, and authentication status
if 'users' not in st.session_state:
    st.session_state['users'] = {}  # Store users as {email: hashed_password}
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None
if 'ideas' not in st.session_state:
    st.session_state['ideas'] = {}
if 'edit_index' not in st.session_state:
    st.session_state['edit_index'] = None
if 'refresh' not in st.session_state:
    st.session_state['refresh'] = 0  # This will be used to trigger a refresh

# Function to register a new user
def register_user(email, password):
    if email in st.session_state['users']:
        st.error("User already exists. Please log in.")
    else:
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        st.session_state['users'][email] = hashed_pw
        st.session_state['ideas'][email] = []
        st.success("Registration successful! Logging you in...")
        return True
    return False

# Function to authenticate user
def authenticate(email, password):
    if email in st.session_state['users'] and bcrypt.checkpw(password.encode(), st.session_state['users'][email]):
        st.session_state['authenticated'] = True
        st.session_state['current_user'] = email
        st.success(f"Welcome back, {email}!")
        trigger_rerun()  # Redirect to the idea management page
    else:
        st.error("Invalid email or password. Please try again.")

# Function to log out user
def logout():
    st.session_state['authenticated'] = False
    st.session_state['current_user'] = None
    st.session_state['edit_index'] = None
    st.success("You have been logged out.")
    trigger_rerun()

# Function to add an idea
def add_idea(email, title, content):
    idea = {
        'title': title,
        'content': content
    }
    st.session_state['ideas'][email].append(idea)
    st.session_state['edit_index'] = None  # Clear edit index after adding

# Function to update an idea
def update_idea(email, index, title, content):
    if 0 <= index < len(st.session_state['ideas'][email]):
        st.session_state['ideas'][email][index] = {'title': title, 'content': content}
        st.session_state['edit_index'] = None  # Reset edit index after updating

# Function to delete an idea
def delete_idea(email, index):
    if 0 <= index < len(st.session_state['ideas'][email]):
        st.session_state['ideas'][email].pop(index)

# Increment the refresh key to trigger a rerun
def trigger_rerun():
    st.session_state['refresh'] += 1

# Display homepage with description and developer credit
st.title("💡 Idea Keeper")
st.markdown("""
**Idea Keeper** is a simple and secure app that helps you manage your ideas efficiently. 
Whether it's for work, a personal project, or just a thought, keep all your ideas in one place and manage them with ease.

This app allows you to:
- Create new ideas
- Edit existing ideas
- Delete ideas you no longer need

All your ideas are stored securely and are accessible only by you.

---

*Developed by Mohamed Osman* © 2024
""")

# Display option to choose between Login and Register
if not st.session_state['authenticated']:
    st.subheader("Login or Register to Start Managing Your Ideas")

    option = st.selectbox("Choose an option", ["Login", "Register"])

    if option == "Register":
        st.subheader("Register")
        email = st.text_input("Email", placeholder="Enter your email", key="register_email")
        password = st.text_input("Password", placeholder="Enter your password", type="password", key="register_password")
        register_button = st.button("Register")

        if register_button and email and password:
            if register_user(email, password):
                authenticate(email, password)  # Automatically log in after registration

    elif option == "Login":
        st.subheader("Login")
        email = st.text_input("Email", placeholder="Enter your email", key="login_email")
        password = st.text_input("Password", placeholder="Enter your password", type="password", key="login_password")
        login_button = st.button("Login")

        if login_button and email and password:
            authenticate(email, password)

else:
    # Logged in - show the Idea Keeper app
    st.subheader(f"Welcome, {st.session_state['current_user']}! Manage your ideas below:")

    # Form for adding or updating an idea
    with st.form(key='idea_form', clear_on_submit=True):
        if st.session_state['edit_index'] is not None:
            # Ensure the edit index is within bounds before accessing the idea
            if 0 <= st.session_state['edit_index'] < len(st.session_state['ideas'][st.session_state['current_user']]):
                idea = st.session_state['ideas'][st.session_state['current_user']][st.session_state['edit_index']]
                title = st.text_input(label="💡 Idea Title", value=idea['title'])
                content = st.text_area(label="📝 Idea Content", value=idea['content'])
                submit_button = st.form_submit_button(label="Update Idea")
            else:
                st.warning("Invalid idea selected for editing.")
                st.session_state['edit_index'] = None
                trigger_rerun()
        else:
            title = st.text_input(label="💡 Idea Title")
            content = st.text_area(label="📝 Idea Content")
            submit_button = st.form_submit_button(label="Save Idea")

        if submit_button:
            if st.session_state['edit_index'] is not None:
                update_idea(st.session_state['current_user'], st.session_state['edit_index'], title, content)
            else:
                add_idea(st.session_state['current_user'], title, content)
            trigger_rerun()

    # Display the ideas in a custom table format with inline buttons
    st.subheader("Your Ideas")
    if st.session_state['ideas'][st.session_state['current_user']]:
        for index, idea in enumerate(st.session_state['ideas'][st.session_state['current_user']]):
            cols = st.columns([4, 1, 1])  # Define column sizes
            with cols[0]:
                st.write(f"**{idea['title']}**\n{idea['content']}")
            with cols[1]:
                if st.button(f"✏️ Edit", key=f"edit_{index}"):
                    st.session_state['edit_index'] = index
                    trigger_rerun()
            with cols[2]:
                if st.button(f"🗑️ Delete", key=f"delete_{index}"):
                    delete_idea(st.session_state['current_user'], index)
                    trigger_rerun()
    else:
        st.write("No ideas yet. Add a new idea to get started! 😊")

    # Logout button
    if st.button("Logout"):
        logout()
        trigger_rerun()
