import streamlit as st
import datetime

#--------------Session State Initialization----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

#--------------For Current User-----------
if "current_user" not in st.session_state:
    st.session_state.current_user = None

#--------------For Accounts (use consistent name)-------------
if "accounts" not in st.session_state:
    st.session_state.accounts = {}

if "transactions" not in st.session_state:
    st.session_state.transactions = {}

#-------------------------
# Function to Add transaction
#--------------------------
def add_transaction(user, ttype, amount):
    # Here we add dictionary to hold transactional details
    entry = {
        "type": ttype,
        "amount": float(amount),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    # Ensure user's transactions list exists (safety)
    if user not in st.session_state.transactions:
        st.session_state.transactions[user] = []
    st.session_state.transactions[user].insert(0, entry)

#-----------------------
# Function Authentication
#----------------------
def authenticate(username, pin):
    # Check user exists and PIN matches
    if username in st.session_state.accounts:
        return st.session_state.accounts[username]["pin"] == str(pin)
    return False

def register(username, pin, balance):
    # Register new user with initial balance
    if username in st.session_state.accounts:
        st.error("Username already exists")
        return False
    try:
        bal = float(balance)
        if bal < 0:
            st.error("Your balance is Zero")
            return False
    except:
        st.error("Invalid balance amount")
        return False

    st.session_state.accounts[username] = {
        "pin": str(pin),
        "balance": bal
    }
    st.session_state.transactions[username] = []
    st.success("Account created Successfully")
    return True

#-----------------------
# Function to deposit money
#----------------------
def deposit(amount):
    user = st.session_state.current_user
    if user is None:
        st.error("No user logged in")
        return
    try:
        amount = float(amount)
        if amount <= 0:
            st.error("Deposit amount must be positive")
            return
    except:
        st.error("Please Enter valid amount")
        return

    st.session_state.accounts[user]["balance"] += amount
    add_transaction(user, "Deposit", amount)
    # Save the History of Transaction
    st.success(f"Deposited {amount} successfully")
    # This message will show when the amount is deposited

#-----------------------
# Function to withdraw money
#-----------------------
def withdraw(amount):
    user = st.session_state.current_user
    if user is None:
        st.error("No user logged in")
        return
    try:
        amount = float(amount)
        if amount <= 0:
            st.error("Withdraw amount must be greater than Zero")
            return
    except:
        st.error("Please Enter valid amount")
        return

    if amount > st.session_state.accounts[user]["balance"]:
        st.error("Insufficient Balance")
        return

    st.session_state.accounts[user]["balance"] -= amount
    add_transaction(user, "Withdraw", amount)
    st.success(f"Withdrawn {amount} Successfully")
    # This message will show when the amount is withdrawn
    # Save the History of Transaction

def show_balance():
    user = st.session_state.current_user
    if user is None:
        st.error("No user logged in")
        return
    balance = st.session_state.accounts[user]["balance"]
    st.info(f"Your current balance is: {balance}")
    # This message will show the current balance

#-----------------------
# logout Function
#-----------------------
def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.success("logged out successfully")
    # This message will show when the user is logged out

#-----------------------
#--------Landing page----------
#--------------------------

def landing_page():
    st.title("Welcome to the ATM Samulation App")
    st.write("Welcome! Please login or create new account to continue")

    choice = st.radio("Select Option", ["Login", "Create Account"])

    if choice == "Login":
        username = st.text_input("Username", key="lp_username")
        pin = st.text_input("PIN", type="password", key="lp_pin")
        if st.button("Login"):
            if authenticate(username, pin):
                st.session_state.logged_in = True
                st.session_state.current_user = username
                st.success("Logged in Successfully")
            else:
                st.error("Invalid username or PIN")

    elif choice == "Create Account":
        username = st.text_input("Username", key="ca_username")
        pin = st.text_input("Set a PIN", type="password", key="ca_pin")
        balance = st.text_input(" Initial Deposit to Your New Account", key="ca_balance")
        if st.button("Create Account"):
            if register(username, pin, balance):
                # after successful register we keep user on landing page
                # they can now use Login to enter
                pass

#---------------- Dashboard Page -----------------
def dashboard():
    user = st.session_state.current_user
    if user is None:
        st.error("No user logged in - please login first")
        return

    st.sidebar.header("Account Info")
    st.sidebar.write(f"Username: {user}")
    st.sidebar.write(f"Balance: {st.session_state.accounts[user]['balance']:.2f}")

    if st.sidebar.button("Logout"):
        logout()
        st.experimental_rerun()

    st.header("ATM Dashboard")
    action = st.selectbox("Choose Action",
                          ["Deposit", "Withdraw", "Check Balance", "Transaction History"])

    if action == "Deposit":
        st.subheader("Deposit Money")
        amount = st.text_input("Enter Your amount to deposit", key="deposit_amount")
        if st.button("Deposit"):
            deposit(amount)

    elif action == "Withdraw":
        st.subheader("Withdraw Money")
        amount = st.text_input("Enter Your amount to withdraw", key="withdraw_amount")
        if st.button("Withdraw"):
            withdraw(amount)

    elif action == "Check Balance":
        st.subheader("Check Balance")
        st.info(f"Your current balance is: {st.session_state.accounts[user]['balance']:.2f}")

    elif action == "Transaction History":
        st.subheader("Transaction History")
        transactions = st.session_state.transactions.get(user, [])
        if not transactions:
            st.info("No transactions yet")
        else:
            for tx in transactions:
                st.write(f"{tx['time']}: {tx['type']} of amount {tx['amount']:.2f}")

#Main Router (no main() needed; streamlit re-runs on save)
if not st.session_state.logged_in:
    landing_page()
else:
    dashboard()
