pipeline {
    agent any
    options { timestamps() }
    environment { IMAGE_NAME = 'ai-document-timeline-agent' }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Install and Test') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -r requirements-dev.txt
                    pytest -q
                '''
            }
        }
        stage('Build Docker Image') {
            steps { sh 'docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} .' }
        }
        stage('Deployment') {
            steps {
                echo 'Deployment is not automatic in this starter pipeline.'
                echo 'Configure secured credentials and an approved deployment target first.'
            }
        }
    }
    post { always { cleanWs() } }
}
