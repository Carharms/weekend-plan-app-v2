pipeline {
    agent any

    environment {
        DB_HOST = "host.docker.internal"
        DB_NAME = "weekend_tasks"
        DB_USER = "root"
        DB_PASSWORD = "password"
        DB_PORT = "3306"
    }

    stages {
        stage('Install + Test') {
            steps {
                script {
                    docker.image('python:3.11-slim').inside {
                        sh 'apt-get update && apt-get install -y default-mysql-client chromium-driver'
                        sh 'pip install -r requirements.txt'
                        sh 'pytest tests/test_e2e.py --junitxml=report.xml'
                        // Must run junit inside same block where file exists
                        junit 'report.xml'
                    }
                }
            }
        }

        stage('Init DB') {
            steps {
                sh 'mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD < database.sql'
                sh 'mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME < seed_data.sql'
            }
        }

        stage('Build Artifact') {
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

        stage('E2E Report') {
            steps {
                script {
                    docker.image('python:3.11-slim').inside {
                        sh 'pytest tests/test_e2e.py --html=report.html || true'
                        sh 'ls -l report.html' // confirm it exists
                        archiveArtifacts artifacts: 'report.html', fingerprint: true
                    }
                }
            }
        }

        stage('Performance Test') {
            steps {
                sh 'locust -f locustfile.py --headless -u 10 -r 2 -t 10s --host=http://localhost:5000'
            }
        }
    }
}