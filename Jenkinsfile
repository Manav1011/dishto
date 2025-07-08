pipeline {
    agent any

    stages {
        stage('Clone Repository') {
            steps {
                deleteDir() // Clean workspace before cloning
                git credentialsId: 'manav1011-cred', url: 'https://github.com/Manav1011/dishto.git', branch: 'main'
            }
        }

        stage('Inject .env from Jenkins Secret File') {
            steps {
                // Remove any existing .env file to avoid permission issues
                sh 'rm -f .env'
                withCredentials([file(credentialsId: 'backend-env', variable: 'ENV_FILE')]) {
                    sh 'cp "$ENV_FILE" .env'
                }
            }
        }

        stage('Build & Deploy') {
            steps {
                sh '''
                docker compose down || true
                docker compose build
                # Run migrations before starting the app
                docker compose run --rm app python manage.py makemigrations --noinput
                docker compose run --rm app python manage.py migrate --noinput
                docker compose up -d
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
