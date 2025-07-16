pipeline {
    agent {
        any {
            image 'python:3.11-slim'
        }
    }

    environment {
        DB_HOST = "localhost"
        DB_NAME = "weekend_tasks"
        DB_USER = "root"
        DB_PASSWORD = "password"
        DB_PORT = "3306"
    }

    stages {

        stage('Build in Docker') {
            steps {
                script {
                    docker.image('python:3.11-slim').inside('-v /var/run/docker.sock:/var/run/docker.sock') {
                        sh 'python --version'
                    }
                }
            }
        }
        stage('Install') {
            steps {
                sh 'apt-get update && apt-get install -y default-mysql-client chromium-driver'
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Init DB') {
            steps {
                sh 'mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD < database.sql'
                sh 'mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME < seed_data.sql'
            }
        }

        stage('Build') {
            steps {
                script {
                    def version = "1.0.${env.BUILD_ID}"
                    writeFile file: 'version.txt', text: version
                    archiveArtifacts artifacts: 'version.txt', fingerprint: true
                }
            }
        }

        stage('SonarQube') {
            environment {
                SONAR_SCANNER_OPTS = "-Dsonar.projectKey=weekend_app"
            }
            steps {
                withSonarQubeEnv('SonarQubeDocker') {
                    sh 'sonar-scanner'
                }
            }
        }

        stage('E2E Tests') {
            steps {
                sh 'pytest tests/test_e2e.py --html=report.html || true'
                archiveArtifacts artifacts: 'report.html', fingerprint: true
            }
        }

        stage('Performance Test') {
            steps {
                sh 'locust -f locustfile.py --headless -u 10 -r 2 -t 10s --host=http://localhost:5000'
            }
        }
    }

    post {
        always {
            junit 'report.xml'
        }
    }
}
