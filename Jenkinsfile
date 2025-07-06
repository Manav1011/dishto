pipeline {
    agent any

    stages {
        stage('Clone Repository') {
            steps {
                deleteDir() // Clean workspace before cloning
                git credentialsId: '2eb76234-7740-49f6-aab9-e78cc92aebe6', url: 'https://github.com/Manav1011/dishto.git', branch: 'main'
            }
        }

        stage('Inject .env from Jenkins Secret File') {
            steps {
                // Remove any existing .env file to avoid permission issues
                sh 'rm -f .env'
                withCredentials([file(credentialsId: 'd63654a7-3421-4802-bebf-e3652e9b6141', variable: 'ENV_FILE')]) {
                    sh 'cp "$ENV_FILE" .env'
                }
            }
        }

        stage('Build & Deploy') {
            steps {
                sh '''
                docker compose down || true
                docker compose up -d --build
                '''
            }
        }

        stage('Show Logs (optional)') {
            steps {
                sh 'docker compose logs --tail=20'
            }
        }
    }

    post {
        success {
            echo "✅ Deployment successful!"
        }
        failure {
            echo "❌ Build or deployment failed. Check logs above."
        }
    }
}
