pipeline {
    agent none
    
    environment {
        DOCKER_IMAGE = 'weekend-task-manager'
        DOCKER_TAG = "${BUILD_NUMBER}"
        SONAR_PROJECT_KEY = 'weekend-task-manager'
        DB_HOST = 'localhost'
        DB_NAME = 'weekend_tasks_test'
        DB_USER = 'root'
        DB_PASSWORD = 'password'
    }
    
    stages {
        stage('Checkout') {
            agent { label 'main' }
            steps {
                checkout scm
                script {
                    if (env.BRANCH_NAME == 'main') {
                        env.DEPLOY_ENV = 'production'
                    } else {
                        env.DEPLOY_ENV = 'staging'
                    }
                }
            }
        }

        stage('Branch Logic') {
            steps {
                script {
                    if (env.BRANCH_NAME == 'main') {
                        echo "Prod deployment to main branch"
                        env.DEPLOY_ENV = 'production'
                        env.RUN_PERFORMANCE_TESTS = 'true'
                    } else if (env.BRANCH_NAME == 'develop') {
                        echo "Staging deployment to branch"
                        env.DEPLOY_ENV = 'staging'
                        env.RUN_PERFORMANCE_TESTS = 'false'
                    } else {
                        echo "Feature branch detected: Running tests only"
                        env.DEPLOY_ENV = 'none'
                        env.RUN_PERFORMANCE_TESTS = 'false'
                    }
                    echo "Calculated DEPLOY_ENV: ${env.DEPLOY_ENV}"
                    echo "Calculated RUN_PERFORMANCE_TESTS: ${env.RUN_PERFORMANCE_TESTS}"
                }
            }
        }
        
        stage('Build') {
            agent { label 'build' }
            steps {
                script {
                    echo "Building for branch: ${env.BRANCH_NAME}"
                    echo "Deploy environment: ${env.DEPLOY_ENV}"
                }
                
                sh 'pip install -r requirements.txt'
                
                // Build Docker image
                sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
            }
            post {
                success {
                    archiveArtifacts artifacts: 'requirements.txt', fingerprint: true
                }
            }
        }
        
        stage('Test') {
            parallel {
                stage('Unit Tests') {
                    agent { label 'testing' }
                    steps {
                        sh 'python -m pytest test_app.py -v --junitxml=test-results.xml'
                    }
                    post {
                        always {
                            junit 'test-results.xml'
                        }
                    }
                }
                
                stage('Code Quality') {
                    agent { label 'sonar' }
                    steps {
                        script {
                            def scannerHome = tool 'SonarQube Scanner'
                            withSonarQubeEnv('SonarQube') {
                                sh "${scannerHome}/bin/sonar-scanner"
                            }
                        }
                    }
                }
            }
        }
        
        stage('Quality Gate') {
            agent { label 'sonar' }
            steps {
                timeout(time: 1, unit: 'HOURS') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
        
        stage('Database Setup') {
            agent { label 'database' }
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                sh 'mysql -u${DB_USER} -p${DB_PASSWORD} < weekend_tasks.sql'
                echo 'Database schema created and seeded'
            }
        }
        
        stage('E2E Tests') {
            agent { label 'testing' }
            steps {
                // Start application
                sh 'python app.py &'
                // Period for app to start
                sh 'sleep 10'
                
                // Run E2E tests
                dir('e2e_tests') {
                    sh 'pytest test_user_journey.py -v --html=../e2e-report.html --self-contained-html'
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'e2e-report.html', fingerprint: true
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
        
        stage('Performance Tests') {
            agent { label 'testing' }
            when {
                branch 'main'
            }
            steps {
                dir('performance_testing') {
                    sh 'chmod +x run_performance_tests.sh'
                    sh './run_performance_tests.sh'
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'performance_testing/performance_results/*', fingerprint: true
                }
            }
        }
        
        stage('Deploy') {
            agent { label 'deployment' }
            when {
                branch 'main'
            }
            steps {
                echo "Deploying to ${env.DEPLOY_ENV}"
                sh "docker run -d -p 5000:5000 --name weekend-app-${BUILD_NUMBER} ${DOCKER_IMAGE}:${DOCKER_TAG}"
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
            slackSend channel: '#devops',
                     color: 'good',
                     message: "PIPELINE SUCCESS: ${env.JOB_NAME} - ${env.BUILD_NUMBER}"
        }
        failure {
            slackSend channel: '#devops',
                     color: 'danger',
                     message: "PIPELINE FAILURE: ${env.JOB_NAME} - ${env.BUILD_NUMBER}"
        }
    }
}