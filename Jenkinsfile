pipeline {
    agent any

    environment {
        // From folder-scoped Jenkins credentials (must match IDs)
        GEMINI_API_KEY = credentials("GEMINI_API_KEY")
        PG_USER = credentials("PG_USER")
        PG_DB = credentials("PG_DB")
        PG_PASSWORD = credentials("PG_PASSWORD")
        PG_HOST = credentials("PG_HOST")
        PG_PORT = credentials("PG_PORT")
        QDRANT_HOST = credentials("QDRANT_HOST")
        QDRANT_PORT = credentials("QDRANT_PORT")
        REDIS_HOST = credentials("REDIS_HOST")
        REDIS_PORT = credentials("REDIS_PORT")
    }

    stages {
        stage('Clone Repository') {
            steps {
                git credentialsId: '2eb76234-7740-49f6-aab9-e78cc92aebe6', url: 'https://github.com/Manav1011/dishto.git', branch: 'main'
            }
        }

        stage('Inject .env from Jenkins Secret File') {
            steps {
                withCredentials([file(credentialsId: 'd63654a7-3421-4802-bebf-e3652e9b6141', variable: 'ENV_FILE')]) {
                    sh 'cp "$ENV_FILE" .env'
                }
            }
        }

        stage('Build & Deploy') {
            steps {
                sh '''
                docker-compose down || true
                docker-compose up -d --build
                '''
            }
        }

        stage('Show Logs (optional)') {
            steps {
                sh 'docker-compose logs --tail=20'
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
