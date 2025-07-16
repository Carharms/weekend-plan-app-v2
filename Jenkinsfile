pipeline {
    agent none

    environment {
        DOCKER_IMAGE = 'weekend-task-manager'
        DOCKER_REGISTRY = 'localhost:5000' // Keeping for potential future use, not actively used in simplified Docker push
        SONAR_PROJECT_KEY = 'weekend-task-manager'
        DB_HOST = 'localhost'
        DB_NAME = 'weekend_tasks_test'
        DB_USER = 'root'
        DB_PASSWORD = 'password'

        // Versioning - Simplified to use BUILD_NUMBER directly
        VERSION = "1.0.${BUILD_NUMBER}"
        PACKAGE_NAME = "weekend-task-manager-${VERSION}"
    }

    stages {
        stage('Checkout & Version') {
            agent { label 'main' }
            steps {
                checkout scm
                script {
                    env.DEPLOY_ENV = 'production' // Always production for simplicity
                    writeFile file: 'version.txt', text: env.VERSION
                    echo "Building version: ${env.VERSION}"
                    echo "Deploy environment: ${env.DEPLOY_ENV}"
                }
            }
        }

        stage('Build & Package') {
            agent { label 'build' }
            steps {
                script {
                    echo "Building application version: ${env.VERSION}"
                    echo "Package name: ${env.PACKAGE_NAME}"
                }

                sh 'pip install -r requirements.txt'

                // Create artificants
                sh """
                    mkdir -p dist
                    tar -czf dist/${PACKAGE_NAME}.tar.gz \
                        --exclude='dist' \
                        --exclude='.git' \
                        --exclude='__pycache__' \
                        --exclude='*.pyc' \
                        --exclude='venv' \
                        .
                    cd dist
                    sha256sum *.tar.gz > checksums.txt
                    ls -la
                """

                sh """
                    docker build -t ${DOCKER_IMAGE}:${VERSION} .
                """
            }

            // Fingerprints allow tracking of files across different builds
            post {
                success {
                    archiveArtifacts artifacts: 'dist/**', fingerprint: true
                    archiveArtifacts artifacts: 'version.txt', fingerprint: true
                }
            }
        }
// test
        // Replace your existing SonarQube stages with these Docker-based versions

stage('Code Quality Analysis and Quality Gate') {
    agent { label 'testing' }
    steps {
        script {
            // Ensure SonarQube server is running via Docker
            echo "Starting SonarQube server via Docker..."
            bat '''
                docker stop sonarqube || echo "SonarQube container not running"
                docker rm sonarqube || echo "SonarQube container does not exist"
                docker run -d --name sonarqube -p 9000:9000 sonarqube:lts-community
            '''
            
            // Wait for SonarQube to be ready
            echo "Waiting for SonarQube to be ready..."
            bat '''
                timeout /t 60 /nobreak >nul
                for /l %%i in (1,1,30) do (
                    curl -f http://localhost:9000/api/system/status && goto :ready
                    echo Waiting for SonarQube... attempt %%i
                    timeout /t 10 /nobreak >nul
                )
                echo SonarQube failed to start
                exit /b 1
                :ready
                echo SonarQube is ready!
            '''

            // Create SonarQube project properties
            writeFile file: 'sonar-project.properties', text: """
sonar.projectKey=${SONAR_PROJECT_KEY}
sonar.projectName=Weekend Task Manager
sonar.projectVersion=${VERSION}
sonar.sources=.
sonar.exclusions=**/node_modules/**,**/dist/**,**/build/**,**/*.pyc,**/venv/**,**/__pycache__/**
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.xunit.reportPath=test-results.xml
sonar.qualitygate.wait=true
sonar.host.url=http://localhost:9000
            """

            // Run tests and coverage
            bat '''
                pip install coverage pytest
                coverage run -m pytest test_app.py --junitxml=test-results.xml || echo "Tests completed with issues"
                coverage xml || echo "Coverage report generated"
            '''

            // Run SonarQube Scanner via Docker
            echo "Running SonarQube Scanner via Docker..."
            bat """
                docker run --rm ^
                    --network host ^
                    -v "%cd%":/usr/src ^
                    -w /usr/src ^
                    sonarsource/sonar-scanner-cli:latest ^
                    -Dsonar.projectKey=${SONAR_PROJECT_KEY} ^
                    -Dsonar.projectName="Weekend Task Manager" ^
                    -Dsonar.projectVersion=${VERSION} ^
                    -Dsonar.sources=. ^
                    -Dsonar.exclusions=**/node_modules/**,**/dist/**,**/build/**,**/*.pyc,**/venv/**,**/__pycache__/** ^
                    -Dsonar.python.coverage.reportPaths=coverage.xml ^
                    -Dsonar.python.xunit.reportPath=test-results.xml ^
                    -Dsonar.host.url=http://localhost:9000 ^
                    -Dsonar.qualitygate.wait=true
            """
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'sonar-project.properties', fingerprint: true
            archiveArtifacts artifacts: 'coverage.xml', fingerprint: true, allowEmptyArchive: true
            archiveArtifacts artifacts: 'test-results.xml', fingerprint: true, allowEmptyArchive: true
        }
    }
}

// Updated Quality Gate stage for Docker
    stage('Quality Gate') {
        agent { label 'testing' }
        steps {
            timeout(time: 10, unit: 'MINUTES') {
                script {
                    try {
                        echo "Checking Quality Gate via Docker..."
                        
                        // Get the latest task ID from SonarQube
                        def taskId = bat(
                            script: '''
                                curl -s "http://localhost:9000/api/ce/activity?component=%SONAR_PROJECT_KEY%&status=SUCCESS,FAILED,CANCELED" | findstr /r "\"id\""
                            ''',
                            returnStdout: true
                        ).trim()
                        
                        echo "Latest task info: ${taskId}"
                        
                        // Check quality gate status
                        def qualityGateStatus = bat(
                            script: '''
                                curl -s "http://localhost:9000/api/qualitygates/project_status?projectKey=%SONAR_PROJECT_KEY%" | findstr /r "\"status\""
                            ''',
                            returnStdout: true
                        ).trim()
                        
                        echo "Quality Gate Status: ${qualityGateStatus}"
                        
                        // Simple check - look for "ERROR" in the response
                        if (qualityGateStatus.contains('"status":"ERROR"')) {
                            echo "Quality Gate Failed!"
                            error "Pipeline aborted due to quality gate failure"
                        }
                        
                        echo "✅ Quality Gate passed successfully!"
                        
                    } catch (Exception e) {
                        echo "Quality Gate check failed: ${e.getMessage()}"
                        echo "This might be due to SonarQube server connectivity issues."
                        throw e
                    }
                }
            }
        }
        post {
            always {
                // Clean up SonarQube container
                bat '''
                    docker stop sonarqube || echo "SonarQube container already stopped"
                    docker rm sonarqube || echo "SonarQube container already removed"
                '''
            }
        }
    }


        stage('Database Setup') {
            agent { label 'database' }
            steps {
                script {
                    echo "Setting up database for ${env.DEPLOY_ENV} environment"
                    // Create database, run schema, and seed data
                    sh '''
                        mysql -u${DB_USER} -p${DB_PASSWORD} -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME};"
                        mysql -u${DB_USER} -p${DB_PASSWORD} ${DB_NAME} < database/schema.sql
                        mysql -u${DB_USER} -p${DB_PASSWORD} ${DB_NAME} < database/seed_data.sql
                    '''
                }
            }
        }

        stage('E2E Tests with Selenium') {
            agent { label 'testing' }
            steps {
                script {
                    // Start application (simplified, assuming app.py is directly executable)
                    sh 'python app.py > app.log 2>&1 &'
                    sh 'sleep 15' // Give app time to start

                    // Run Selenium E2E tests
                    dir('e2e_tests') {
                        sh '''
                            pip install -r requirements.txt
                            python -m pytest selenium_tests.py -v --html=../e2e-report.html --junitxml=../e2e-results.xml
                        '''
                    }
                }
            }
            post {
                always {
                    // Stop application (basic kill)
                    sh 'pkill -f "python app.py" || true'

                    archiveArtifacts artifacts: 'e2e-report.html', fingerprint: true
                    archiveArtifacts artifacts: 'e2e-results.xml', fingerprint: true
                    junit 'e2e-results.xml'
                }
            }
        }

        stage('Performance Testing') {
            agent { label 'testing' }
            steps {
                script {
                    // Start application for performance testing
                    sh 'python app.py > perf_app.log 2>&1 &'
                    sh 'sleep 10' // Give app time to start

                    // Run performance tests using a simple Locust command
                    dir('performance_testing') {
                        sh '''
                            pip install locust
                            locust -f locustfile.py --headless -u 10 -r 2 --run-time 30s --html results/performance_report.html --csv results/performance_metrics
                        '''
                    }
                }
            }
            post {
                always {
                    // Stop application
                    sh 'pkill -f "python app.py" || true'

                    archiveArtifacts artifacts: 'performance_testing/results/**', fingerprint: true
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'performance_testing/results',
                        reportFiles: 'performance_report.html',
                        reportName: 'Performance Test Report'
                    ])
                }
            }
        }

        stage('Deploy') {
            agent { label 'deployment' }
            steps {
                script {
                    echo "Deploying version ${env.VERSION} to ${env.DEPLOY_ENV}"
                    // Basic Docker deployment
                    sh """
                        docker stop weekend-app || true
                        docker rm weekend-app || true
                        docker run -d \
                            --name weekend-app \
                            -p 5000:5000 \
                            ${DOCKER_IMAGE}:${VERSION}
                        sleep 10
                        curl -f http://localhost:5000/health
                    """
                }
            }
        }
    }

    post {
        always {
            node('main') {
                cleanWs()
            }
        }
        success {
            script {
                slackSend channel: '#devops',
                          color: 'good',
                          message: """✅ PIPELINE SUCCESS: ${env.JOB_NAME} - ${env.BUILD_NUMBER}
                                     Version: ${env.VERSION}
                                     Branch: ${env.BRANCH_NAME}
                                     Environment: ${env.DEPLOY_ENV}
                                  """
            }
        }
        failure {
            script {
                slackSend channel: '#devops',
                          color: 'danger',
                          message: """❌ PIPELINE FAILURE: ${env.JOB_NAME} - ${env.BUILD_NUMBER}
                                     Version: ${env.VERSION}
                                     Branch: ${env.BRANCH_NAME}
                                     Check logs for details
                                  """
            }
        }
    }
}