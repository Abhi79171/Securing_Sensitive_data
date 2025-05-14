# Securing Sensitive Data in AI-Driven Chatbots

This project focuses on building a secure, privacy-aware chatbot system that prevents the leakage of sensitive data (like financial, personal, or health-related information) when users interact with AI language models. The system integrates Natural Language Processing (NLP) models and rule-based filters to screen inputs and outputs for sensitive content in real time.

## Features

- **Sensitive Data Detection**: Identifies financial, personal, and health-related data using transformer-based models and regex patterns.
- **NLP Classifier**: Fine-tuned BERT/GPT/FinBERT models for classifying and tagging sensitive input.
- **Chatbot Interface**: User-friendly frontend to interact with the bot.
- **Admin Dashboard**: Tracks flagged content, model decisions, and user query logs.
- **Logs & Monitoring**: Stores and visualizes detected sensitive data entries for auditing and compliance.
- **Multi-Model Evaluation**: Compares outputs from OpenAI, Claude, and other LLMs for correctness and sensitivity.

## Tech Stack

- **Backend**: Python (Flask)
- **Frontend**: React.js
- **Models**: HuggingFace Transformers (BERT, FinBERT, zero-shot BART)
- **Database**: SQLite
- **Security**: Regex-based filters 



### Prerequisites

- Python 3.9+
- Node.js & npm (for frontend)
- SqLite




