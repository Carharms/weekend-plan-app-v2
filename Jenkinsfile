
pipeline {
    agent any
    
    environment {
        DB_HOST = "172.17.0.1" // Docker host gateway IP on Linux
        DB_NAME = "weekend_tasks"
        DB_USER = "root"
        DB_PASSWORD = "password"
        DB_PORT = "3308"
        SONAR_SCANNER_HOME = tool 'SonarScanner'
        PATH = "${SONAR_SCANNER_HOME}/bin:${env.PATH}"
        NOTIFICATION_EMAIL = "charms014@gmail.com"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                // List files to verify what's in workspace
                bat 'dir'
            }
        }
        
        stage('Build') {
            steps {
                script {
                    docker.build("weekend-app:${env.BUILD_NUMBER}")
                }
            }
        }
        
        stage('Test Dependencies') {
            steps {
                script {
                    bat """
                    docker run --rm ^
                    -v %cd%:/workspace ^
                    -w /workspace ^
                    python:3.11-slim ^
                    sh -c "apt-get update && apt-get install -y default-mysql-client && pip install -r requirements.txt"
                    """
                }
            }
        }

        stage('Start MySQL via Compose') {
            steps {
                bat  '''
                docker-compose up -d mysql
                '''
                sleep(time: 20, unit: 'SECONDS') // wait for MySQL to initialize
            }
        }

       
        
        stage('E2E Tests') {
            steps {
                script {
                    bat """
                    docker run --rm ^
                    -v %cd%:/workspace ^
                    -w /workspace ^
                    python:3.11-slim ^
                    sh -c "apt-get update && apt-get install -y chromium-driver && \
                           pip install selenium pytest-html && \
                           pytest test_e2e.py --html=e2e-report.html || true"
                    """
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'e2e-report.html',
                        reportName: 'E2E Test Report'
                    ])
                }
            }
        }
        
        stage('Performance Test') {
            when {
                branch 'main'
            }
            steps {
                script {
                    bat """
                    docker run --rm ^
                    -v %cd%:/workspace ^
                    -w /workspace ^
                    python:3.11-slim ^
                    sh -c "pip install locust && \
                           locust -f locustfile.py --headless -u 10 -r 2 -t 30s --host=http://host.docker.internal:5000 --html=perf-report.html"
                    """
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'perf-report.html',
                        reportName: 'Performance Test Report'
                    ])
                }
            }
        }
        
        stage('Package Artifacts') {
            steps {
                script {
                    def version = "1.0.${env.BUILD_NUMBER}"
                    writeFile file: 'version.txt', text: version

                    // Debug: List all files in workspace
                    bat 'dir /s'
                    
                    // Check existence with better error handling
                    def filesToCheck = ['app.py', 'templates', 'static', 'requirements.txt']
                    def missing = []
                    
                    filesToCheck.each { file ->
                        if (!fileExists(file)) {
                            missing.add(file)
                            echo "Missing: ${file}"
                        } else {
                            echo "Found: ${file}"
                        }
                    }
                    
                    if (missing) {
                        error "Missing files/directories: ${missing.join(', ')}"
                    }

                    // Package - use PowerShell for better Windows compatibility
                    bat """
                    powershell -Command "Compress-Archive -Path app.py,templates,static,requirements.txt,version.txt -DestinationPath weekend-app-${version}.zip"
                    """

                    archiveArtifacts artifacts: "weekend-app-${version}.zip,version.txt", fingerprint: true
                }
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to staging environment'
                bat 'docker run -d -p 5000:5000 --name staging-app weekend-app:${BUILD_NUMBER}'
            }
        }
    }
}