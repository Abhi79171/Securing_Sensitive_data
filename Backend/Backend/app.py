from flask import Flask, request, jsonify, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from openai import OpenAI
import PyPDF2
import pandas as pd
import os
import re
import spacy
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from werkzeug.utils import secure_filename
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Initializes the Flask app
app = Flask(__name__)
app.secret_key = "supersecretkey" # Secret key for session management

# Initializes OpenAI client with Api Key
client = OpenAI(api_key="")

# Enables CORS to allow cross-origin requests
CORS(app, supports_credentials=True)

def get_db_connection():
    # Connects to SQLite database
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row # So we can access columns by name
    return conn

def init_db():
    # Initialize database tables if they don't exist
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table for authentication
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        first_name TEXT, last_name TEXT, email TEXT UNIQUE,
                        password TEXT, role TEXT DEFAULT NULL,
                        is_approved INTEGER DEFAULT 0, is_blocked INTEGER DEFAULT 0)''')

    # Chat history table for saving interactions
    cursor.execute('''CREATE TABLE IF NOT EXISTS chat_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
                        question TEXT, response TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)''')

    # Rules for detecting sensitive data patterns
    cursor.execute('''CREATE TABLE IF NOT EXISTS sensitive_rules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, rule TEXT UNIQUE)''')

    # Logs API endpoint usage
    cursor.execute('''CREATE TABLE IF NOT EXISTS api_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, endpoint TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    # Logs sensitive data detections
    cursor.execute('''CREATE TABLE IF NOT EXISTS sensitive_data_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        prompt TEXT,
                        detected_data TEXT,
                        bert_prediction TEXT,
                        finbert_prediction TEXT,
                        zero_shot_prediction TEXT,
                        is_sensitive INTEGER,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)''')
    conn.commit()
    conn.close()

init_db() # Creates tables when app starts

# Load sNLP models for detecting sensitive data
nlp = spacy.load("en_core_web_sm")
bert_classifier = pipeline("text-classification", model="./bert_finetuned", tokenizer="./bert_finetuned")
finbert_classifier = pipeline("text-classification", model="./finbert_finetuned", tokenizer="./finbert_finetuned")
zero_shot_classifier = pipeline("text-classification", model="./zero_shot_finetuned", tokenizer="./zero_shot_finetuned")

def detect_sensitive_data(message, user_id):
    """
       Detects sensitive data in a message using:
       - Named Entity Recognition (NER) via spaCy
       - Regex rules for financial data
       - BERT-based classifiers for general and financial sensitivity
       Logs detection results into the database.
       """
    redacted_message = message # It will replace sensitive content with [REDACTED]

    # It runs message through multiple models
    bert_result = bert_classifier(message)[0]
    finbert_result = finbert_classifier(message)[0]
    zero_shot_result = zero_shot_classifier(message)[0]

    # Normalizes zero-shot labels
    zero_shot_label = "LABEL_1" if zero_shot_result["label"] in ["sensitive", "LABEL_1"] else "LABEL_0"
    zero_shot_score = zero_shot_result["score"]

    # UsesspaCy for entity recognition
    doc = nlp(message)
    detected_entities = []
    for ent in doc.ents:
        if ent.label_ in ["MONEY", "PERSON", "ORG"]:
            detected_entities.append(ent.text)
            redacted_message = redacted_message.replace(ent.text, "[REDACTED]")

    financial_keywords = [
        r"\b(transfer|payment|deposit|withdraw|balance|account|card)\s+\$?\d+(?:\.\d{2})?\b",
        r"\bcredit card\s*(?:number)?\s*[0-9-]{13,16}\b",
        r"\baccount\s*(?:number)?\s*\d{8,12}\b",
        r"\bbank account\s*(?:number)?\s*\d{8,12}\b",
        r"\bpin\s*\d{4}\b",
        r"\btransaction\s*(?:ID|number)?\s*[A-Za-z0-9]{6,12}\b",
        r"\btransfer\s+\$?\d+(?:\.\d{2})?\s+to\s+(?:account|card)\s*\d{8,12}\b",
        r"\bpayment\s+of\s+\$?\d+(?:\.\d{2})?\b",
        r"\bdeposit\s+of\s+\$?\d+(?:\.\d{2})?\b",
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    ]
    for rule in financial_keywords:
        matches = re.findall(rule, message, re.IGNORECASE)
        if matches:
            detected_entities.extend(matches)
            redacted_message = re.sub(rule, "[REDACTED]", redacted_message, flags=re.IGNORECASE)

    # Determines if the message is sensitive based on model outputs or rule triggers
    model_sensitive = (
        (bert_result["label"] == "LABEL_1" and bert_result["score"] > 0.7) or
        (finbert_result["label"] == "LABEL_1" and finbert_result["score"] > 0.7) or
        (zero_shot_label == "LABEL_1" and zero_shot_score > 0.7)
    )
    rules_triggered = len(detected_entities) > 0
    is_sensitive = model_sensitive or rules_triggered

    # Logs detection results in the sensitive_data_logs table
    conn = get_db_connection()
    cursor = conn.cursor()
    detected_data = ", ".join(set(detected_entities)) if detected_entities else "N/A"
    bert_pred = f"{bert_result['label']} ({bert_result['score']:.2f})"
    finbert_pred = f"{finbert_result['label']} ({finbert_result['score']:.2f})"
    zero_shot_pred = f"{zero_shot_label} ({zero_shot_score:.2f})"
    cursor.execute('''INSERT INTO sensitive_data_logs (
                        user_id, prompt, detected_data, bert_prediction, finbert_prediction, zero_shot_prediction, is_sensitive
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (user_id, message, detected_data, bert_pred, finbert_pred, zero_shot_pred, int(is_sensitive)))
    conn.commit()
    conn.close()

    return is_sensitive, redacted_message

def log_api_request(endpoint):
    """
      Logs each API endpoint call, avoiding duplicate consecutive logs for the same endpoint.
      """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT endpoint, timestamp FROM api_logs ORDER BY id DESC LIMIT 1")
        last_log = cursor.fetchone()
        if not last_log or last_log["endpoint"] != endpoint:
            cursor.execute("INSERT INTO api_logs (endpoint) VALUES (?)", (endpoint,))
            conn.commit()
        conn.close()
    except Exception as e:
        print("Error logging API request:", str(e))


# logs API usage before each request (except pre-flight OPTIONS)
@app.before_request
def before_request():
    if request.method != "OPTIONS":
        log_api_request(request.path)

# ------------------------ User Management Endpoints ------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password = generate_password_hash(data.get("password"))
    role = "Employee"
    is_approved = 0
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (first_name, last_name, email, password, role, is_approved, is_blocked) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (first_name, last_name, email, password, role, is_approved, 0))
        conn.commit()
        conn.close()
        return jsonify({"message": "Registration successful. Waiting for admin approval."}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Email already exists"}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    if user:
        if user["is_approved"] == 0:
            return jsonify({"error": "Your account is pending approval."}), 403
        if user["is_blocked"] == 1:
            return jsonify({"error": "Your account has been blocked by the admin."}), 403
        if check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            return jsonify({"message": "Login successful", "id": user["id"], "role": user["role"]}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/users/approve", methods=["POST"])
def approve_user():
    data = request.json
    user_id = data.get("user_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_approved = 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "User approved successfully"}), 200

@app.route("/users/block", methods=["POST"])
def block_user():
    data = request.json
    user_id = data.get("user_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_blocked = 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "User blocked successfully"}), 200

@app.route("/users/unblock", methods=["POST"])
def unblock_user():
    data = request.json
    user_id = data.get("user_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_blocked = 0 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "User unblocked successfully"}), 200

@app.route("/users", methods=["GET"])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, first_name, last_name, email, role, is_approved, is_blocked FROM users")
    users = cursor.fetchall()
    conn.close()
    return jsonify([dict(user) for user in users]), 200

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out successfully"}), 200

@app.route("/profile", methods=["GET"])
def profile():
    if "user_id" in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, first_name, last_name, email, role FROM users WHERE id = ?", (session["user_id"],))
        user = cursor.fetchone()
        conn.close()
        if user:
            return jsonify(dict(user)), 200
    return jsonify({"error": "Unauthorized"}), 401

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print("Error extracting PDF text:", str(e))
    return text or "Unable to extract text from the PDF."

def extract_data_from_excel(file_path):
    df = pd.read_excel(file_path)
    return df.to_string()

def extract_data_from_csv(file_path):
    df = pd.read_csv(file_path)
    return df.to_string()

# ------------------------ Chat Endpoint ------------------------
@app.route("/chat", methods=["POST"])
def chat():
    """
       Main chat endpoint:
       - Accepts user message and optional file (PDF, Excel, CSV)
       - Detects sensitive data in both message and file
       - If sensitive data is found, responds with a warning
       - Otherwise, sends the message to OpenAI GPT for a response
       - Logs the conversation in the database
       """
    data = request.form
    user_id = data.get("user_id")
    message = request.form.get("message")
    file = request.files.get("file")

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        if filename.endswith(".pdf"):
            file_content = extract_text_from_pdf(filepath)
        elif filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_content = extract_data_from_excel(filepath)
        elif filename.endswith(".csv"):
            file_content = extract_data_from_csv(filepath)
        else:
            file_content = f"File {filename} uploaded but could not be read."
        is_sensitive_file, redacted_file_content = detect_sensitive_data(file_content, user_id)
    else:
        file_content = None
        is_sensitive_file = False
        redacted_file_content = ""

    is_sensitive_msg, redacted_message = detect_sensitive_data(message, user_id)

    if is_sensitive_msg or is_sensitive_file:
        chat_response = "Message or file contains sensitive data and has been redacted."
    else:
        prompt = redacted_message
        if file_content:
            prompt += f"\n\nFile Content:\n{redacted_file_content}"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        chat_response = response.choices[0].message.content

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (user_id, question, response) VALUES (?, ?, ?)",
                   (user_id, message, chat_response))
    conn.commit()
    conn.close()
    return jsonify({"response": chat_response})

@app.route("/history", methods=["POST"])
def history():
    # Fetches the full chat history for a specific user
    data = request.json
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT question, response, timestamp FROM chat_history WHERE user_id = ? ORDER BY timestamp DESC",
                   (user_id,))
    history = cursor.fetchall()
    conn.close()
    # Returns the user's chat history as a list of question/response pairs
    return jsonify(
        [{"question": row["question"], "response": row["response"], "timestamp": row["timestamp"]} for row in history])

@app.route("/queries", methods=["GET"])
def get_queries():
    # Fetches the latest 20 queries (across all users)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT question, response, timestamp FROM chat_history ORDER BY timestamp DESC LIMIT 20")
    queries = cursor.fetchall()
    conn.close()
    return jsonify([dict(query) for query in queries]), 200

@app.route("/rules", methods=["GET"])
def get_rules():
    # Fetches all sensitive data detection rules (regex patterns)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, rule FROM sensitive_rules")
    rules = cursor.fetchall()
    conn.close()
    return jsonify([dict(rule) for rule in rules]), 200

@app.route("/rules/add", methods=["POST"])
def add_rule():
    # Adds a new sensitive data detection rule
    data = request.json
    rule = data.get("rule")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sensitive_rules (rule) VALUES (?)", (rule,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Rule added successfully"}), 201

@app.route("/rules/delete", methods=["POST"])
def delete_rule():
    # Deletes a sensitive data detection rule by ID
    data = request.json
    rule_id = data.get("id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sensitive_rules WHERE id = ?", (rule_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Rule deleted successfully"}), 200

@app.route("/logs", methods=["GET"])
def get_logs():
    # Fetches recent API logs, skipping every second log (just to reduce clutter)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, endpoint, timestamp FROM (
            SELECT id, endpoint, timestamp, ROW_NUMBER() OVER (ORDER BY timestamp DESC) AS rn
            FROM api_logs
        ) WHERE rn % 2 = 1 LIMIT 25
    """)
    logs = cursor.fetchall()
    conn.close()
    return jsonify([dict(log) for log in logs]), 200

@app.route("/sensitive_logs", methods=["GET"])
def get_sensitive_logs():
    # Fetches all logs related to sensitive data detections
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sensitive_data_logs ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    conn.close()
    return jsonify([dict(log) for log in logs]), 200

@app.route("/performance", methods=["GET"])
def get_performance_metrics():
    """
        Compute accuracy, precision, recall, and F1-score of the sensitive data detection models
        based on historical logs in the sensitive_data_logs table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT bert_prediction, finbert_prediction, zero_shot_prediction, is_sensitive FROM sensitive_data_logs")
    logs = cursor.fetchall()
    conn.close()

    if not logs:
        return jsonify({"error": "No sensitive data logs available"}), 404

    y_true = [log["is_sensitive"] for log in logs]

    bert_preds = [1 if "LABEL_1" in log["bert_prediction"] and float(log["bert_prediction"].split("(")[1].split(")")[0]) > 0.7 else 0 for log in logs]
    finbert_preds = [1 if "LABEL_1" in log["finbert_prediction"] and float(log["finbert_prediction"].split("(")[1].split(")")[0]) > 0.7 else 0 for log in logs]
    zero_shot_preds = [1 if "LABEL_1" in log["zero_shot_prediction"] and float(log["zero_shot_prediction"].split("(")[1].split(")")[0]) > 0.7 else 0 for log in logs]

    # Computes standard classification metrics
    def compute_metrics(y_true, y_pred):
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        return {"accuracy": accuracy, "precision": precision, "recall": recall, "f1_score": f1}

    metrics = {
        "BERT": compute_metrics(y_true, bert_preds),
        "FinBERT": compute_metrics(y_true, finbert_preds),
        "Zero-shot": compute_metrics(y_true, zero_shot_preds)
    }

    return jsonify(metrics), 200

if __name__ == "__main__":
    initial_rules = [
        r"\b(?:\d[ -]*?){13,16}\b",
        r"\b\d{8,12}\b",
        r"\b(transfer|payment|deposit)\s+\$?\d+(?:\.\d{2})?(?:\s+to\s+\d{8,12})?\b",
        r"\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    ]
    conn = get_db_connection()
    cursor = conn.cursor()
    for rule in initial_rules:
        try:
            cursor.execute("INSERT INTO sensitive_rules (rule) VALUES (?)", (rule,))
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()

    app.run(debug=True, use_reloader=False)