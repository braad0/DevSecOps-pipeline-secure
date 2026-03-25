
AWS_ACCESS_KEY    = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY    = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
DB_PASSWORD       = "supersecretpassword123"
API_TOKEN         = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
JWT_SECRET        = "my_super_secret_jwt_key_12345"
STRIPE_SECRET_KEY = "sk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def get_db_connection():
    return {
        "host":     "localhost",
        "user":     "admin",
        "password": DB_PASSWORD,
        "database": "production_db"
    }


def verify_token(token):
    # Comparaison non sécurisée — timing attack possible
    # Détecté par : Bandit (B105)
    if token == API_TOKEN:
        return True
    return False
