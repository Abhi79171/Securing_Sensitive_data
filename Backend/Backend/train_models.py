import os
import numpy as np
import pandas as pd

# Hugging Face Transformers imports for tokenization, modeling, and training
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    TrainerCallback,
)
from datasets import Dataset

# Scikit-learn metrics for evaluation
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
)

# To deal with imbalanced labels by oversampling the minority class
from imblearn.over_sampling import RandomOverSampler


# Raw training examples
training_data = [
    {"text": "Customer account number: 123456789", "label": 1},
    {"text": "The balance is updated", "label": 0},
    {"text": "Account activity report is available", "label": 0},
    {"text": "Generate the monthly financial summary", "label": 0},
    {"text": "Customer satisfaction survey is due", "label": 0},
    {"text": "Upcoming board meeting scheduled", "label": 0},
    {"text": "Finance team has submitted the proposal", "label": 0},
    {"text": "Credit card number: 4111 1111 1111 1111", "label": 1},
    {"text": "Bank account info: ACC9988776655", "label": 1},
    {"text": "PIN: 4321", "label": 1},
    {"text": "Please process the transaction ID: TXN998877", "label": 1},
    {"text": "Transaction details: ID 9876543210", "label": 1},
    {"text": "User email: john.doe@example.com", "label": 1},
    {"text": "Login credentials: user123 / pass456", "label": 1},
    {"text": "Quarterly budget projections are optimistic", "label": 0},
    {"text": "Routing number: 021000021", "label": 1},
    {"text": "Document has been reviewed", "label": 0},
    {"text": "Social Security Number: 123-45-6789", "label": 1},
    {"text": "Finalize the agreement draft", "label": 0},
    {"text": "Invoice for services rendered", "label": 0},
    {"text": "SWIFT code: DEUTDEFF", "label": 1},
    {"text": "Meeting notes are attached", "label": 0},
    {"text": "User password: MyP@ssw0rd!", "label": 1},
    {"text": "Policy update shared with all departments", "label": 0},
    {"text": "Customer's date of birth: 01/01/1980", "label": 1},
    {"text": "Vendor list finalized", "label": 0},
    {"text": "Internal ID: EMP12345", "label": 1},
    {"text": "IT team is patching systems", "label": 0},
    {"text": "Phone number: +1-555-123-4567", "label": 1},
    {"text": "Training session next Monday", "label": 0},
    {"text": "Card expiration date: 12/26", "label": 1},
    {"text": "Minutes from yesterday’s call", "label": 0},
    {"text": "Security answer: mother’s maiden name", "label": 1},
    {"text": "Annual performance reviews due", "label": 0},
    {"text": "Tax ID: 99-9999999", "label": 1},
    {"text": "Customer inquiries are increasing", "label": 0},
    {"text": "Medical record number: MRN456123", "label": 1},
    {"text": "Weekly newsletter published", "label": 0},
    {"text": "National ID: ABC123456", "label": 1},
    {"text": "Reminder: policy acknowledgment required", "label": 0},
    {"text": "Private key: -----BEGIN PRIVATE KEY-----", "label": 1},
    {"text": "Design mockups shared with team", "label": 0},
    {"text": "SSN: 321-54-9876", "label": 1},
    {"text": "Presentations ready for review", "label": 0},
    {"text": "Insurance policy number: INS12345678", "label": 1},
    {"text": "Slack channel updated", "label": 0},
    {"text": "Driver's license: D1234567", "label": 1},
    {"text": "Budget meeting scheduled", "label": 0},
    {"text": "Bank account ending in 7890", "label": 1},
    {"text": "File uploaded to shared drive", "label": 0},
    {"text": "Customer credentials stored securely", "label": 1},
    {"text": "Quarter close expected next week", "label": 0},
    {"text": "Sensitive token: abc123xyz", "label": 1},
    {"text": "Marketing campaign in draft mode", "label": 0},
    {"text": "Passcode: 654321", "label": 1},
    {"text": "Documentation for onboarding ready", "label": 0},
    {"text": "User ID: U123456789", "label": 1},
    {"text": "Graphics team is updating slides", "label": 0},
    {"text": "Mailing address: 123 Main St", "label": 1},
    {"text": "Presentation approved by execs", "label": 0},
    {"text": "Authentication code: 999999", "label": 1},
    {"text": "Send invites to the conference", "label": 0},
    {"text": "Device IMEI: 357881074565234", "label": 1},
    {"text": "Reports merged successfully", "label": 0},
    {"text": "SSN submitted to HR", "label": 1},
    {"text": "Dev team deployed the patch", "label": 0},
    {"text": "IP address: 192.168.1.1", "label": 1},
    {"text": "Q&A session recorded", "label": 0},
    {"text": "Encrypted password hash stored", "label": 1},
    {"text": "All team leads have responded", "label": 0},
    {"text": "User biometric data uploaded", "label": 1},
    {"text": "Update product descriptions", "label": 0},
    {"text": "API key: sk_test_abc123", "label": 1},
    {"text": "No blockers reported", "label": 0},
    {"text": "Certificate serial: 00:11:22:33", "label": 1},
    {"text": "Check-in complete", "label": 0},
    {"text": "Personal data redacted", "label": 1},
    {"text": "Team agreed on next steps", "label": 0},
    {"text": "Confidential report attached", "label": 1},
    {"text": "All invoices reconciled", "label": 0},
    {"text": "Secure message: encrypted.txt", "label": 1},
    {"text": "Reminder to fill out expense reports", "label": 0},
    {"text": "User credentials compromised", "label": 1},
    {"text": "Slides uploaded to portal", "label": 0},
    {"text": "Secret question: first school", "label": 1},
    {"text": "New role added to org chart", "label": 0},
    {"text": "Tracking ID: TRK1234567", "label": 1},
    {"text": "Department KPIs updated", "label": 0},
    {"text": "Client signature needed", "label": 0},
    {"text": "Cloud backup successful", "label": 0},
    {"text": "Weekly sync scheduled", "label": 0},
    {"text": "Template shared in drive", "label": 0},
    {"text": "Files reviewed by legal", "label": 0},
    {"text": "Discussion points documented", "label": 0},
    {"text": "FAQ page revised", "label": 0},
    {"text": "Draft contract under review", "label": 0},
    {"text": "Server maintenance completed", "label": 0},
    {"text": "Holiday calendar updated", "label": 0},
    {"text": "No PII included in attachment", "label": 0},
    {"text": "Time off request approved", "label": 0},
    {"text": "Automation scripts deployed", "label": 0},
    {"text": "New hire onboarding scheduled", "label": 0},
    {"text": "Team lunch on Friday", "label": 0},
    {"text": "Updated roles and responsibilities", "label": 0},
    {"text": "Performance dashboard shared", "label": 0},
    {"text": "Monthly metrics reviewed", "label": 0},
    {"text": "Support ticket resolved", "label": 0},
    {"text": "Expenses categorized properly", "label": 0},
    {"text": "Updated marketing assets uploaded", "label": 0},
    {"text": "Backup server restored", "label": 0},
    {"text": "Sprint goals finalized", "label": 0},
    {"text": "UI changes reviewed", "label": 0},
    {"text": "Payroll details for March: $5,400 credited", "label": 1},
    {"text": "Employee bank account number: 123456789012", "label": 1},
    {"text": "W-2 form uploaded for tax filing", "label": 1},
    {"text": "Company credit card limit: $25,000", "label": 1},
    {"text": "Direct deposit routing number: 123456789", "label": 1},
    {"text": "Net salary breakdown shared in chat", "label": 1},
    {"text": "Internal reimbursement form with receipts", "label": 1},
    {"text": "Expense report with full card number attached", "label": 1},
    {"text": "Vendor payment info: ACH transfer details", "label": 1},
    {"text": "Loan account statement sent via chat", "label": 1},
    {"text": "Encrypted tax documents uploaded", "label": 1},
    {"text": "Access code to corporate investment portal", "label": 1},
    {"text": "Company's EIN: 12-3456789", "label": 1},
    {"text": "Financial audit data for Q2 submitted", "label": 1},
    {"text": "Banking credentials for ERP system shared", "label": 1},
    {"text": "Full credit card statement sent to bot", "label": 1},
    {"text": "Employee compensation report: $120,000 annual", "label": 1},
    {"text": "Access granted to payroll processing system", "label": 1},
    {"text": "Routing and account number for wire transfer", "label": 1},
    {"text": "Company debit card PIN: 1234", "label": 1},
    {"text": "Bank statement PDF uploaded for reconciliation", "label": 1},
    {"text": "Corporate tax return files uploaded", "label": 1},
    {"text": "Sensitive ledger file shared by mistake", "label": 1},
    {"text": "Bank login details sent to support bot", "label": 1},
    {"text": "Internal balance sheet showing negative cash flow", "label": 1},
    {"text": "List of high-value client invoices", "label": 1},
    {"text": "Private financial forecast for FY2025", "label": 1},
    {"text": "Credit card CVV and expiration sent in plain text", "label": 1},
    {"text": "SWIFT transfer receipt attached", "label": 1},
    {"text": "Internal purchase orders with pricing details", "label": 1},
    {"text": "Confidential finance access credentials shared", "label": 1},
    {"text": "Form 1099 attached for freelance payments", "label": 1},
    {"text": "Internal billing system credentials", "label": 1},
    {"text": "Client account balance and payment history", "label": 1},
    {"text": "Bank account used for salary disbursements", "label": 1},
    {"text": "Cryptocurrency wallet address shared", "label": 1},
    {"text": "Salary advance request with personal account info", "label": 1},
    {"text": "Pension contribution breakdown shared", "label": 1},
    {"text": "Private equity portfolio spreadsheet", "label": 1},
    {"text": "Payment authorization token sent", "label": 1},
    {"text": "Payroll summary including employee SSNs", "label": 1},
    {"text": "Mortgage account number and monthly payments", "label": 1},
    {"text": "Loan payoff schedule sent for approval", "label": 1},
    {"text": "Retirement account summary shared", "label": 1},
    {"text": "Expense card details for all employees", "label": 1},
    {"text": "Private comments on financial audit draft", "label": 1},
    {"text": "ACH transfer history downloaded", "label": 1},
    {"text": "Invoice numbers and bank routing info shared", "label": 1},
    {"text": "Screenshot of online banking login", "label": 1},
    {"text": "Corporate AmEx number shared with bot", "label": 1},
    {"text": "Bank wire instructions sent for vendor", "label": 1},
    {"text": "Internal cost breakdown for confidential project", "label": 1},
    {"text": "Payment gateway API key shared", "label": 1},
    {"text": "Full ledger with transaction IDs uploaded", "label": 1},
    {"text": "Bank account info used in fraud investigation", "label": 1},
    {"text": "Spreadsheet of Q4 earnings shared", "label": 1},
    {"text": "Private investor report uploaded", "label": 1},
    {"text": "Capital expenditure file included", "label": 1},
    {"text": "Sensitive budget planning documents", "label": 1},
    {"text": "Login to bank reconciliation tool provided", "label": 1},
    {"text": "Payroll slip with net salary and deductions", "label": 1},
    {"text": "Salary hikes and bonus info disclosed", "label": 1},
    {"text": "Private budget reforecast shared in chat", "label": 1},
    {"text": "Annual report with profit margin sent", "label": 1},
    {"text": "Detailed transaction logs attached", "label": 1},
    {"text": "Crypto wallet seed phrase shared", "label": 1},
    {"text": "Internal transaction authorization PIN", "label": 1},
    {"text": "Client wire instructions shared", "label": 1},
    {"text": "Bank OTP entered for account access", "label": 1},
    {"text": "Government financial ID shared", "label": 1},
    {"text": "Quarterly income statement disclosed", "label": 1},
    {"text": "Cloud accounting platform login shared", "label": 1},
    {"text": "Stock trading password revealed", "label": 1},
    {"text": "Pay stub image uploaded", "label": 1},
    {"text": "Internal tax planning memo attached", "label": 1},
    {"text": "Internal audit notes on cash reserves", "label": 1},
    {"text": "Proof of address and banking documents", "label": 1},
    {"text": "Receipts with full card details sent", "label": 1},
    {"text": "Internal discount and pricing strategy", "label": 1},
    {"text": "Corporate earnings presentation draft", "label": 1},
    {"text": "SaaS subscription credit card info exposed", "label": 1},
    {"text": "Financial KPI dashboard screenshot shared", "label": 1},
    {"text": "Payment token shared in chat", "label": 1},
    {"text": "Loan application form submitted", "label": 1},
    {"text": "Proof of wire transfer to international vendor", "label": 1},
    {"text": "PDF of investment prospectus uploaded", "label": 1},
    {"text": "Account security questions answered", "label": 1},
    {"text": "Online banking access from shared IP", "label": 1},
    {"text": "Excel with client payment methods", "label": 1},
    {"text": "Document including bank codes and SWIFT IDs", "label": 1},
    {"text": "Client refund transaction IDs", "label": 1},
    {"text": "Internal credit risk report", "label": 1},
    {"text": "Scan of signed financial agreement", "label": 1},
    {"text": "Cardholder name and full PAN included", "label": 1},
    {"text": "Merchant account ID and access code", "label": 1},
    {"text": "Mobile banking login credentials", "label": 1},
    {"text": "Salary distribution list sent to bot", "label": 1},
    {"text": "High-level funding allocation details shared", "label": 1},
    {"text": "Draft of confidential earnings call script", "label": 1},
    {"text": "Screenshot with internal investment links", "label": 1},
    {"text": "Company retirement fund details", "label": 1},
    {"text": "Secure link to banking documents posted", "label": 1},
    {"text": "Account holder info and KYC docs uploaded", "label": 1},
    {"text": "PDF containing multiple bank account numbers", "label": 1},
    {"text": "Internal funds transfer form completed", "label": 1},
    {"text": "HR file with bank and salary details", "label": 1},
    {"text": "Tax audit correspondence shared", "label": 1},
    {"text": "PDF with sensitive reimbursement records", "label": 1},
    {"text": "Shareholder dividend distribution chart", "label": 1},
    {"text": "Cardholder authentication data entered", "label": 1},
    {"text": "One-time use bank token shared", "label": 1},
    {"text": "Confidential invoice summary attached", "label": 1},
    {"text": "Finance software login shared via chat", "label": 1},
    {"text": "Private statement of cash flows", "label": 1},
    {"text": "Screenshot of balance sheet with figures", "label": 1},
    {"text": "Vendor bank details for automated payments", "label": 1},
    {"text": "Bank faxed authorization code included", "label": 1},
    {"text": "Finalized cash flow report shared", "label": 1},
    {"text": "Personal credit card used for business expense", "label": 1},
    {"text": "PDF of confidential budget breakdown", "label": 1},
    {"text": "Payment summary to external consultant", "label": 1},
    {"text": "Private key to financial record system", "label": 1},
    {"text": "Sensitive compensation survey attached", "label": 1},
    {"text": "Account reset code for payroll service", "label": 1},
    {"text": "Image of void check for direct deposit", "label": 1},
    {"text": "Government financial aid ID submitted", "label": 1},
    {"text": "Spreadsheet of financial approvals", "label": 1},
    {"text": "Detailed vendor pricing agreement", "label": 1},
    {"text": "Balance transfer request to credit union", "label": 1},
    {"text": "Invoice from overseas contractor", "label": 1},
    {"text": "Internal note on large fund transfers", "label": 1},
    {"text": "Screenshot of salary portal", "label": 1},
    {"text": "List of all payroll beneficiaries", "label": 1},
    {"text": "QR code for banking app shared", "label": 1},
    {"text": "Summary of withheld taxes uploaded", "label": 1},
    {"text": "Form 1040 draft shared for review", "label": 1},
    {"text": "Company loan approval notice", "label": 1},
    {"text": "Upload of billing contact info with card", "label": 1},
    {"text": "Company's internal cost center list", "label": 1},
    {"text": "Internal form with card authorization details", "label": 1},
    {"text": "Pension fund details shared via chatbot", "label": 1},
    {"text": "Financial breakdown of merger deal", "label": 1},
    {"text": "Schedule next project check-in for Friday", "label": 0},
    {"text": "Send reminder about upcoming webinar", "label": 0},
    {"text": "Update the internal documentation links", "label": 0},
    {"text": "Draft a welcome message for the new hire", "label": 0},
    {"text": "Share onboarding checklist with team", "label": 0},
    {"text": "Prepare slides for quarterly team update", "label": 0},
    {"text": "Schedule a brainstorming session next week", "label": 0},
    {"text": "Organize folders by project name", "label": 0},
    {"text": "Review content calendar for May", "label": 0},
    {"text": "Send follow-up email to client", "label": 0},
    {"text": "Create agenda for next leadership sync", "label": 0},
    {"text": "Collect feedback from product testers", "label": 0},
    {"text": "Update Jira tickets with new priorities", "label": 0},
    {"text": "Design banner for internal newsletter", "label": 0},
    {"text": "Compile survey results into a report", "label": 0},
    {"text": "Check availability for office hours", "label": 0},
    {"text": "Coordinate team outing for next month", "label": 0},
    {"text": "Share link to recorded training session", "label": 0},
    {"text": "Upload project charter to shared folder", "label": 0},
    {"text": "Tag stakeholders in project update post", "label": 0},
    {"text": "Draft internal announcement about policy change", "label": 0},
    {"text": "List upcoming deadlines for Q2", "label": 0},
    {"text": "Proofread email draft before sending", "label": 0},
    {"text": "Update meeting notes with action items", "label": 0},
    {"text": "Confirm attendance for next all-hands", "label": 0},
    {"text": "Summarize client feedback on prototype", "label": 0},
    {"text": "Add team bios to about page", "label": 0},
    {"text": "Update project tracker status", "label": 0},
    {"text": "Send kudos to engineering team", "label": 0},
    {"text": "Prepare questions for user interview", "label": 0},
    {"text": "Create task list for website redesign", "label": 0},
    {"text": "Export contacts from old CRM", "label": 0},
    {"text": "Compile customer testimonials", "label": 0},
    {"text": "Schedule design review for Thursday", "label": 0},
    {"text": "Email agenda to team before call", "label": 0},
    {"text": "Set up Slack reminders for project check-ins", "label": 0},
    {"text": "Write blog post draft for product launch", "label": 0},
    {"text": "Review competitor landing pages", "label": 0},
    {"text": "Start outline for next whitepaper", "label": 0},
    {"text": "Reorder team directory by department", "label": 0},
    {"text": "Clean up shared folders on drive", "label": 0},
    {"text": "Schedule monthly one-on-one meetings", "label": 0},
    {"text": "Review the new style guide", "label": 0},
    {"text": "Remind team about code freeze", "label": 0},
    {"text": "Assign owner for Q2 OKRs", "label": 0},
    {"text": "List team priorities in weekly update", "label": 0},
    {"text": "Document lessons learned from sprint", "label": 0},
    {"text": "Summarize action items from retro", "label": 0},
    {"text": "Coordinate cross-functional alignment", "label": 0},
    {"text": "Double-check deadline for marketing copy", "label": 0},
    {"text": "Finalize talking points for presentation", "label": 0},
    {"text": "Send invite for roadmap review", "label": 0},
    {"text": "Share summary of quarterly goals", "label": 0},
    {"text": "Create checklist for launch readiness", "label": 0},
    {"text": "Move completed tasks to 'Done' column", "label": 0},
    {"text": "Update sprint board with recent changes", "label": 0},
    {"text": "Reassign tasks from out-of-office teammate", "label": 0},
    {"text": "Request headcount forecast for next quarter", "label": 0},
    {"text": "Draft customer support FAQ", "label": 0},
    {"text": "List follow-up items from client call", "label": 0},
    {"text": "Upload training deck to LMS", "label": 0},
    {"text": "Coordinate logistics for team retreat", "label": 0},
    {"text": "Share link to team goals document", "label": 0},
    {"text": "Plan agenda for onboarding session", "label": 0},
    {"text": "Review new project naming conventions", "label": 0},
    {"text": "Summarize department highlights", "label": 0},
    {"text": "Post reminder about PTO deadlines", "label": 0},
    {"text": "Update contact list for partners", "label": 0},
    {"text": "Create slide deck for investor update (no financials)", "label": 0},
    {"text": "Share new company branding guidelines", "label": 0},
    {"text": "Compile questions from town hall", "label": 0},
    {"text": "Organize user feedback by topic", "label": 0},
    {"text": "Archive old campaigns from CRM", "label": 0},
    {"text": "List all current open roles", "label": 0},
    {"text": "Assign mentor for new employee", "label": 0},
    {"text": "Post job opening to internal board", "label": 0},
    {"text": "Send pulse survey to employees", "label": 0},
    {"text": "Prepare internal release notes", "label": 0},
    {"text": "Tag issues by severity in bug tracker", "label": 0},
    {"text": "Update team calendar with PTO", "label": 0},
    {"text": "Add product launch to event calendar", "label": 0},
    {"text": "Highlight success stories in newsletter", "label": 0},
    {"text": "List steps for knowledge transfer", "label": 0},
    {"text": "Remind team to update email signatures", "label": 0},
    {"text": "Create onboarding task list for intern", "label": 0},
    {"text": "Confirm room booking for leadership meeting", "label": 0},
    {"text": "Reschedule product demo", "label": 0},
    {"text": "Attach logos to press kit", "label": 0},
    {"text": "Send calendar invite to new stakeholder", "label": 0},
    {"text": "Add task to update mobile screenshots", "label": 0},
    {"text": "Prepare internal FAQs for new feature", "label": 0},
    {"text": "List of external tools used by team", "label": 0},
    {"text": "Clean up unused Slack channels", "label": 0},
    {"text": "Create checklist for accessibility review", "label": 0},
    {"text": "Remind design team of brand colors", "label": 0},
    {"text": "Draft announcement for internal wiki launch", "label": 0},
    {"text": "Check timezone difference for client call", "label": 0},
    {"text": "Review attendance list for training", "label": 0},
    {"text": "Organize folders by department", "label": 0},
    {"text": "Send update about cafeteria hours", "label": 0},
    {"text": "Draft message for internal celebration", "label": 0},
    {"text": "Update policies with latest terminology", "label": 0},
    {"text": "10", "label": 0},
    {"text": "7894", "label": 0},
    {"text": "PIN: 7894", "label": 1},
    {"text": "My pin is 7894", "label": 1},
    {"text": "Share tips on effective Zoom calls", "label": 0},
    {"text": "Add employee birthdays to calendar", "label": 0},
    {"text": "Create poll for preferred team lunch spot", "label": 0},
    {"text": "List ideas from last design sprint", "label": 0},
    {"text": "Review swag design samples", "label": 0},
    {"text": "Assign backup during vacation period", "label": 0},
    {"text": "Clarify expectations for async updates", "label": 0},
    {"text": "Summarize user pain points", "label": 0},
    {"text": "Send notes from coffee chat", "label": 0},
    {"text": "List popular topics from internal blog", "label": 0},
    {"text": "Schedule photo shoot for team profile pics", "label": 0},
    {"text": "Post lunch menu options in chat", "label": 0},
    {"text": "Remind team about fun Friday quiz", "label": 0},
    {"text": "Add new workspace members to channels", "label": 0},
    {"text": "Share Google Doc link to brainstorm", "label": 0},
    {"text": "Plan knowledge sharing week", "label": 0},
    {"text": "Update org chart with new joiners", "label": 0},
    {"text": "Pin onboarding resources to team channel", "label": 0},
    {"text": "Upload team photo to shared drive", "label": 0},
    {"text": "Send Slack reminder to submit weekly wins", "label": 0}
]

def balance_dataset(data):
    X = np.array([d["text"] for d in data]).reshape(-1, 1)
    y = np.array([d["label"] for d in data])
    ros = RandomOverSampler(random_state=42)
    X_resampled, y_resampled = ros.fit_resample(X, y)
    balanced_data = [{"text": text[0], "label": label} for text, label in zip(X_resampled, y_resampled)]
    return balanced_data

balanced_training_data = balance_dataset(training_data)
data_dict = {"text": [d["text"] for d in balanced_training_data], "label": [d["label"] for d in balanced_training_data]}
dataset = Dataset.from_dict(data_dict)

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions[0] if isinstance(pred.predictions, tuple) else pred.predictions
    preds = preds.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average="binary")
    acc = accuracy_score(labels, preds)
    cm = confusion_matrix(labels, preds)
    tn, fp, fn, tp = cm.ravel()
    return {
        "accuracy": acc,
        "f1": f1,
        "precision": precision,
        "recall": recall,
        "true_negatives": tn,
        "false_positives": fp,
        "false_negatives": fn,
        "true_positives": tp
    }

class CustomCallback(TrainerCallback):
    def _init_(self, model_name):
        self.model_name = model_name
        self.results = []

    def on_evaluate(self, args, state, control, metrics, **kwargs):
        epoch = state.epoch
        eval_metrics = {
            "model": self.model_name,
            "epoch": epoch,
            "eval_accuracy": metrics.get("eval_accuracy", 0.0),
            "eval_f1": metrics.get("eval_f1", 0.0),
            "eval_precision": metrics.get("eval_precision", 0.0),
            "eval_recall": metrics.get("eval_recall", 0.0),
            "true_negatives": metrics.get("eval_true_negatives", 0),
            "false_positives": metrics.get("eval_false_positives", 0),
            "false_negatives": metrics.get("eval_false_negatives", 0),
            "true_positives": metrics.get("eval_true_positives", 0)
        }
        self.results.append(eval_metrics)
        df = pd.DataFrame(self.results)
        print(f"\n{self.model_name} Epoch {epoch} Results:")
        print(df.to_markdown(index=False))
        df.to_csv("training_results.csv", mode='a', header=not os.path.exists("training_results.csv"), index=False)

def fine_tune_bert():
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)

    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=128)

    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    tokenized_dataset = tokenized_dataset.train_test_split(test_size=0.2)

    training_args = TrainingArguments(
        output_dir="./bert_finetuned",
        num_train_epochs=5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir="./logs",
        logging_steps=10,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["test"],
        compute_metrics=compute_metrics,
        callbacks=[CustomCallback("BERT")]
    )

    trainer.train()
    model.save_pretrained("./bert_finetuned")
    tokenizer.save_pretrained("./bert_finetuned")
    print("BERT fine-tuning completed.")

def fine_tune_finbert():
    tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
    model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone", num_labels=2,
                                                               ignore_mismatched_sizes=True)

    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=128)

    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    tokenized_dataset = tokenized_dataset.train_test_split(test_size=0.2)

    training_args = TrainingArguments(
        output_dir="./finbert_finetuned",
        num_train_epochs=5,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir="./logs",
        logging_steps=10,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        learning_rate=2e-5,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["test"],
        compute_metrics=compute_metrics,
        callbacks=[CustomCallback("FinBERT")]
    )

    trainer.train()
    model.save_pretrained("./finbert_finetuned")
    tokenizer.save_pretrained("./finbert_finetuned")
    print("FinBERT fine-tuning completed.")

def fine_tune_zero_shot():
    tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-mnli")
    model = AutoModelForSequenceClassification.from_pretrained("facebook/bart-large-mnli", num_labels=2,
                                                               ignore_mismatched_sizes=True)

    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=128)

    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    tokenized_dataset = tokenized_dataset.train_test_split(test_size=0.2)

    training_args = TrainingArguments(
        output_dir="./zero_shot_finetuned",
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir="./logs",
        logging_steps=10,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["test"],
        compute_metrics=compute_metrics,
        callbacks=[CustomCallback("Zero-shot")]
    )

    trainer.train()
    model.save_pretrained("./zero_shot_finetuned")
    tokenizer.save_pretrained("./zero_shot_finetuned")
    print("Zero-shot fine-tuning completed.")

if __name__ == "__main__":
    if os.path.exists("training_results.csv"):
        os.remove("training_results.csv")
    fine_tune_bert()
    fine_tune_finbert()
    fine_tune_zero_shot()