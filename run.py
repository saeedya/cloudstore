from os import environ
from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv('.env.development')

# Get environment name or default to 'development'
env = environ.get('FLASK_ENV', 'development')

# Create app with correct config
app = create_app(env)

if __name__ == '__main__':
    app.run()