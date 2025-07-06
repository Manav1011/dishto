pipeline {
    agent any
    environment {
        INIT_PATH = "${env.WORKSPACE}/init"
    }
    stages {
        stage('Clone Repository') {
            steps {
                deleteDir()
                git credentialsId: 'manav1011-cred', url: 'https://github.com/Manav1011/dishto.git', branch: 'main'
            }
        }

        stage('Inject .env from Jenkins Secret File') {
            steps {
                dir("${env.WORKSPACE}") {
                    sh 'rm -f .env'
                    withCredentials([file(credentialsId: 'backend-env', variable: 'ENV_FILE')]) {
                        sh 'cp "$ENV_FILE" .env'
                    }
                }
            }
        }

        stage('Build & Deploy') {
            steps {
                dir("${env.WORKSPACE}") {
                    sh '''
                    docker compose down || true
                    docker compose up -d --build
                    '''
                }
            }
        }

        stage('Show Logs (optional)') {
            steps {
                dir("${env.WORKSPACE}") {
                    sh 'docker compose logs --tail=20'
                }
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
