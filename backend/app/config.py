import os

MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() in ("1", "true", "yes")

QUALIFIED_THRESHOLD = float(os.getenv("QUALIFIED_THRESHOLD", "0.6"))

# Salesforce creds (blank in mock mode -> in-memory simulator)
SF_INSTANCE_URL = os.getenv("SALESFORCE_INSTANCE_URL", "")
SF_CLIENT_ID = os.getenv("SALESFORCE_CLIENT_ID", "")
SF_CLIENT_SECRET = os.getenv("SALESFORCE_CLIENT_SECRET", "")
SF_USERNAME = os.getenv("SALESFORCE_USERNAME", "")
SF_PASSWORD = os.getenv("SALESFORCE_PASSWORD", "")
SF_SECURITY_TOKEN = os.getenv("SALESFORCE_SECURITY_TOKEN", "")

DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "data", "leadpilot.db"))
