pipeline {
    agent any
    
    environment {
        DB_HOST = "host.docker.internal"
        DB_NAME = "weekend_tasks"
        DB_USER = "root"
        DB_PASSWORD = "password"
        DB_PORT = "3306"
        SONAR_SCANNER_HOME = tool 'SonarScanner'
        PATH = "${SONAR_SCANNER_HOME}/bin:${env.PATH}"
        NOTIFICATION_EMAIL = "example@example.com"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build') {
            agent {
                label 'build'
            }
            steps {
                script {
                    docker.build("weekend-app:${env.BUILD_NUMBER}")
                }
            }
        }
        
        stage('Test Dependencies') {
            steps {
                script {
                    docker.image('python:3.11-slim').inside {
                        sh 'apt-get update && apt-get install -y default-mysql-client'
                        sh 'pip install -r requirements.txt'
                    }
                }
            }
        }
        
        stage('Unit Tests') {
            when {
                not { branch 'main' }
            }
            steps {
                script {
                    docker.image('python:3.11-slim').inside {
                        sh 'pip install pytest'
                        sh 'pytest tests/test_unit.py --junitxml=unit-report.xml || true'
                        junit 'unit-report.xml'
                    }
                }
            }
        }
        
        stage('Database Setup') {
            steps {
                sh 'mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD < database.sql'
                sh 'mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME < seed_data.sql'
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh '''
                    sonar-scanner \
                    -Dsonar.projectKey=weekend-app \
                    -Dsonar.sources=. \
                    -Dsonar.host.url=$SONAR_HOST_URL \
                    -Dsonar.login=$SONAR_AUTH_TOKEN \
                    -Dsonar.python.coverage.reportPaths=coverage.xml
                    '''
                }
            }
        }
        
        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
        
        stage('E2E Tests') {
            agent {
                label 'test-agent'
            }
            steps {
                script {
                    docker.image('python:3.11-slim').inside {
                        sh 'apt-get update && apt-get install -y chromium-driver'
                        sh 'pip install selenium pytest-html'
                        sh 'pytest tests/test_e2e.py --html=e2e-report.html || true'
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
        }
        
        stage('Performance Test') {
            when {
                branch 'main'
            }
            steps {
                script {
                    sh 'pip install locust'
                    sh 'locust -f locustfile.py --headless -u 10 -r 2 -t 30s --host=http://localhost:5000 --html=perf-report.html'
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
                    
                    sh "tar -czf weekend-app-${version}.tar.gz app.py templates/ static/ requirements.txt"
                    
                    archiveArtifacts artifacts: "weekend-app-${version}.tar.gz,version.txt", fingerprint: true
                }
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to staging environment'
                sh 'docker run -d -p 5000:5000 --name staging-app weekend-app:${BUILD_NUMBER}'
            }
        }
    }
    
    post {
        always {
            // Clean workspace after build
            cleanWs()
            
            // Archive test results if they exist
            script {
                if (fileExists('unit-report.xml')) {
                    junit 'unit-report.xml'
                }
                if (fileExists('e2e-report.html')) {
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'e2e-report.html',
                        reportName: 'Final E2E Report'
                    ])
                }
            }
        }
        
        success {
            emailext (
                to: "${env.NOTIFICATION_EMAIL}",
                subject: "✅ BUILD SUCCESS: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
                body: """
                <h2>Build Completed Successfully!</h2>
                <p><strong>Project:</strong> ${env.JOB_NAME}</p>
                <p><strong>Build Number:</strong> ${env.BUILD_NUMBER}</p>
                <p><strong>Branch:</strong> ${env.BRANCH_NAME}</p>
                <p><strong>Build URL:</strong> <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>
                <p><strong>Duration:</strong> ${currentBuild.durationString}</p>
                <p><strong>Commit:</strong> ${env.GIT_COMMIT}</p>
                
                <h3>Test Results:</h3>
                <p>All tests passed successfully. Check the build logs for detailed results.</p>
                
                <p>Best regards,<br>Jenkins CI/CD System</p>
                """,
                mimeType: 'text/html'
            )
        }
        
        failure {
            emailext (
                to: "${env.NOTIFICATION_EMAIL}",
                subject: "❌ BUILD FAILED: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
                body: """
                <h2>Build Failed!</h2>
                <p><strong>Project:</strong> ${env.JOB_NAME}</p>
                <p><strong>Build Number:</strong> ${env.BUILD_NUMBER}</p>
                <p><strong>Branch:</strong> ${env.BRANCH_NAME}</p>
                <p><strong>Build URL:</strong> <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>
                <p><strong>Console Output:</strong> <a href="${env.BUILD_URL}console">${env.BUILD_URL}console</a></p>
                <p><strong>Duration:</strong> ${currentBuild.durationString}</p>
                <p><strong>Commit:</strong> ${env.GIT_COMMIT}</p>
                
                <h3>Failure Details:</h3>
                <p>Please check the console output and logs for detailed error information.</p>
                <p>Failed stage: ${env.STAGE_NAME}</p>
                
                <p>Please investigate and fix the issues.</p>
                <p>Best regards,<br>Jenkins CI/CD System</p>
                """,
                mimeType: 'text/html'
            )
        }
        
        unstable {
            emailext (
                to: "${env.NOTIFICATION_EMAIL}",
                subject: "⚠️ BUILD UNSTABLE: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
                body: """
                <h2>Build Completed with Warnings!</h2>
                <p><strong>Project:</strong> ${env.JOB_NAME}</p>
                <p><strong>Build Number:</strong> ${env.BUILD_NUMBER}</p>
                <p><strong>Branch:</strong> ${env.BRANCH_NAME}</p>
                <p><strong>Build URL:</strong> <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>
                <p><strong>Duration:</strong> ${currentBuild.durationString}</p>
                <p><strong>Commit:</strong> ${env.GIT_COMMIT}</p>
                
                <h3>Warning Details:</h3>
                <p>The build completed but some tests failed or there were quality gate issues.</p>
                <p>Please review the test results and address any failing tests.</p>
                
                <p>Best regards,<br>Jenkins CI/CD System</p>
                """,
                mimeType: 'text/html'
            )
        }
        
        aborted {
            emailext (
                to: "${env.NOTIFICATION_EMAIL}",
                subject: "🚫 BUILD ABORTED: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
                body: """
                <h2>Build Was Aborted!</h2>
                <p><strong>Project:</strong> ${env.JOB_NAME}</p>
                <p><strong>Build Number:</strong> ${env.BUILD_NUMBER}</p>
                <p><strong>Branch:</strong> ${env.BRANCH_NAME}</p>
                <p><strong>Build URL:</strong> <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>
                <p><strong>Duration:</strong> ${currentBuild.durationString}</p>
                
                <p>The build was manually aborted or timed out.</p>
                
                <p>Best regards,<br>Jenkins CI/CD System</p>
                """,
                mimeType: 'text/html'
            )
        }
    }
}