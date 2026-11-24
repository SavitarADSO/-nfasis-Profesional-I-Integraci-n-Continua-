pipeline {
    agent any

    options {
        disableConcurrentBuilds()
        timestamps()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh 'docker build -t proyecto-ci-app:jenkins ./app'
            }
        }

        stage('Test') {
            steps {
                sh 'docker run --rm --entrypoint python proyecto-ci-app:jenkins -m py_compile app.py'
            }
        }
    }
}
