pipeline {
    agent any

    environment {
        FLASK_ENV = 'testing'
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'develop', url: 'https://github.com/saeedya/cloudstore.git'
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install -r requirements/test.txt
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '''
                . venv/bin/activate
                pytest tests/ --disable-warnings --cov=app --cov-report=xml
                '''
            }
        }

        stage('Generate Coverage Report') {
            steps {
                publishCoverage adapters: [coberturaAdapter('coverage.xml')]
            }
        }
    }

    post {
        always {
            echo 'Cleaning up workspace...'
            sh 'rm -rf venv'
        }
        failure {
            echo 'Tests failed!'
        }
        success {
            echo 'All tests passed!'
        }
    }
}
