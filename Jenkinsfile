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

        stage('Prepare .env File') {
            steps {
                sh '''
                echo "GEMINI_API_KEY=$GEMINI_API_KEY" > .env
                echo "PG_USER=$PG_USER" >> .env
                echo "PG_DB=$PG_DB" >> .env
                echo "PG_PASSWORD=$PG_PASSWORD" >> .env
                echo "PG_HOST=$PG_HOST" >> .env
                echo "PG_PORT=$PG_PORT" >> .env
                echo "QDRANT_HOST=$QDRANT_HOST" >> .env
                echo "QDRANT_PORT=$QDRANT_PORT" >> .env
                echo "REDIS_HOST=$REDIS_HOST" >> .env
                echo "REDIS_PORT=$REDIS_PORT" >> .env
                '''
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
