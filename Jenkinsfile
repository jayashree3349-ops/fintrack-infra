pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo 'Building FinTrack application...'
            }
        }

        stage('Test') {
            steps {
                echo 'Running FinTrack tests...'
            }
        }
    }

    post {
        success {
            echo 'FinTrack CI pipeline completed successfully.'
        }
        failure {
            echo 'FinTrack CI pipeline failed.'
        }
    }
}
