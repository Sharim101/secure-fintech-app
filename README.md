# CY4053 - Secure FinTech Mini-Application

This project is an assignment for **CY4053 - Cybersecurity for FinTech** (BSFT 7th Semester, Fall 2025).

It is a mini-application built with Streamlit that demonstrates key secure development concepts. The app includes features for authentication, data validation, encrypted storage, and activity logging, and is designed to be manually tested for common vulnerabilities.

## 🚀 Features

* **User Authentication:** Secure registration and login with hashed passwords (using `bcrypt`).
* **Password Strength:** Enforces strong password policies during registration.
* **Session Management:** Securely manages user sessions and includes a logout function.
* **Secure Data Storage:** Uses SQLite for data storage, with all user passwords hashed.
* **Encrypted Notes:** A feature to write and store notes that are encrypted (using `cryptography.fernet`) before being saved to the database.
* **Input Validation:** Implements checks for input length, email format, and data types to prevent injection and bad data.
* **Access Control:** Users can only view their own transaction history and activity logs.
* **Secure File Uploads:** Restricts file uploads to specific types (e.g., `jpg`, `png`).
* **Audit Logging:** Tracks key user actions (logins, failures, transactions) in a local `activity.log` file.
* **Secure Error Handling:** Prevents leaking sensitive information (like database schemas or stack traces) to the user.

## 🛠️ How to Run

### 1. Prerequisites

* Python 3.8+
* `pip` (Python package installer)

### 2. Installation

1.  **Clone the repository:**
    ```bash
    git clone [your-github-repo-link]
    cd [your-repo-name]
    ```

2.  **Install the required Python libraries:**
    ```bash
    pip install -r requirements.txt
    ```
    *(If you don't have a `requirements.txt` file, just run:)*
    ```bash
    pip install streamlit bcrypt cryptography
    ```

### 3. Running the Application

1.  **Open your terminal** in the project directory.
2.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```
3.  Your default web browser will automatically open to the application's URL (usually `http://localhost:8501`).

## 🧪 Manual Security Testing

This app was built to be tested. The file `Manual_Test_Cases.xlsx` contains the documentation for 20 manual tests performed on the application to validate its security features, as required by the assignment.
