pipeline {
    agent none
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }
    
    environment {
        // Version management
        VERSION = "${env.BUILD_NUMBER}-${env.GIT_COMMIT[0..7]}"
        APP_NAME = "weekend-task-manager"
        
        // SonarQube configuration
        SONAR_PROJECT_KEY = "weekend-task-manager"
        SONAR_PROJECT_NAME = "Weekend Task Manager"
        SONAR_SCANNER_HOME = tool 'SonarQubeScanner'
        
        // Database configuration for testing
        DB_HOST = 'localhost'
        DB_NAME = 'weekend_tasks_test'
        DB_USER = 'root'
        DB_PASSWORD = 'password'
        DB_PORT = '3306'

        // FOR LATER - ADJUST AND CONFIGURE
        WEBHOOK_TOKEN = 'weekend-task-manager-webhook'
        SLACK_CHANNEL = '#ci-cd'
        EMAIL_RECIPIENTS = 'your-email@example.com'
    }
    
    stages {
        stage('Checkout') {
            agent any
            steps {
                echo "Checking out source code..."
                checkout scm
                script {
                    // Set version based on branch
                    if (env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master') {
                        env.VERSION = "v${env.BUILD_NUMBER}"
                        env.IS_RELEASE = 'true'
                        env.DEPLOY_TO = 'production'
                    } else if (env.BRANCH_NAME == 'develop') {
                        env.VERSION = "dev-${env.BUILD_NUMBER}-${env.GIT_COMMIT[0..7]}"
                        env.IS_RELEASE = 'false'
                        env.DEPLOY_TO = 'staging'
                    } else if (env.BRANCH_NAME.startsWith('feature/')) {
                        env.VERSION = "feature-${env.BUILD_NUMBER}-${env.GIT_COMMIT[0..7]}"
                        env.IS_RELEASE = 'false'
                        env.DEPLOY_TO = 'none'
                    } else {
                        env.VERSION = "${env.BRANCH_NAME}-${env.BUILD_NUMBER}-${env.GIT_COMMIT[0..7]}"
                        env.IS_RELEASE = 'false'
                        env.DEPLOY_TO = 'none'
                    }
                    echo "Building version: ${env.VERSION}"
                    echo "Branch: ${env.BRANCH_NAME}"
                    echo "Deploy target: ${env.DEPLOY_TO}"
                }
            }
        }
        
        

        
        stage('Build & Test') {
            parallel {
                stage('Unit Tests') {
                    agent { label 'testing' }
                    steps {
                        echo "Running unit tests on testing agent..."
                        sh '''
                            python3 -m venv venv
                            . venv/bin/activate
                            pip install -r requirements.txt
                            python -m pytest test_app.py -v --junitxml=test-results.xml --cov=app --cov-report=xml
                        '''
                    }
                    post {
                        always {
                            junit 'test-results.xml'
                            archiveArtifacts artifacts: 'test-results.xml', allowEmptyArchive: true
                            publishCoverage adapters: [
                                coberturaAdapter('coverage.xml')
                            ], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                        }
                    }
                }
                
                stage('Code Quality Analysis') {
                    agent { label 'testing' }
                    steps {
                        echo "Running code quality analysis..."
                        script {
                            withSonarQubeEnv('SonarQube') {
                                sh '''
                                    python3 -m venv venv
                                    . venv/bin/activate
                                    pip install -r requirements.txt
                                    
                                    # Run flake8 for linting
                                    flake8 app.py --output-file=flake8-report.txt --tee
                                    
                                    # Run tests with coverage for SonarQube
                                    python -m pytest test_app.py --cov=app --cov-report=xml --cov-report=html
                                    
                                    # Run SonarQube analysis
                                    ${SONAR_SCANNER_HOME}/bin/sonar-scanner \
                                        -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                                        -Dsonar.projectName="${SONAR_PROJECT_NAME}" \
                                        -Dsonar.projectVersion=${VERSION} \
                                        -Dsonar.sources=app.py \
                                        -Dsonar.tests=test_app.py \
                                        -Dsonar.python.coverage.reportPaths=coverage.xml \
                                        -Dsonar.python.flake8.reportPaths=flake8-report.txt
                                '''
                            }
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'flake8-report.txt', allowEmptyArchive: true
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'htmlcov',
                                reportFiles: 'index.html',
                                reportName: 'Coverage Report'
                            ])
                        }
                    }
                }
            }
        }
        
        stage('Quality Gate') {
            agent { label 'testing' }
            steps {
                echo "Waiting for SonarQube Quality Gate..."
                timeout(time: 10, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
        
        stage('Build Artifacts') {
            agent { label 'deployment' }
            when {
                anyOf {
                    branch 'main'
                    branch 'master'
                    branch 'develop'
                    expression { return env.BRANCH_NAME.startsWith('release/') }
                }
            }
            steps {
                echo "Building application artifacts..."
                sh '''
                    # Create application package
                    mkdir -p dist
                    
                    # Create version file
                    echo "${VERSION}" > VERSION
                    
                    # Package application
                    tar -czf dist/${APP_NAME}-${VERSION}.tar.gz \
                        app.py \
                        requirements.txt \
                        VERSION \
                        templates/ \
                        static/ \
                        --exclude='.git' \
                        --exclude='venv' \
                        --exclude='__pycache__' \
                        --exclude='*.pyc'
                    
                    # Create Docker image (if Dockerfile exists)
                    if [ -f Dockerfile ]; then
                        docker build -t ${APP_NAME}:${VERSION} .
                        docker save ${APP_NAME}:${VERSION} | gzip > dist/${APP_NAME}-${VERSION}-docker.tar.gz
                    fi
                    
                    # Generate checksums
                    cd dist
                    sha256sum *.tar.gz > checksums.txt
                    cd ..
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'dist/**', allowEmptyArchive: false
                    archiveArtifacts artifacts: 'VERSION', allowEmptyArchive: false
                }
            }
        }
        
        stage('Deploy to Staging') {
            agent { label 'deployment' }
            when {
                anyOf {
                    branch 'develop'
                    expression { return env.BRANCH_NAME.startsWith('release/') }
                }
            }
            steps {
                echo "Deploying to staging environment..."
                sh '''
                    echo "Deploying version ${VERSION} to staging"
                    # Add your staging deployment commands here
                    # For example:
                    # scp dist/${APP_NAME}-${VERSION}.tar.gz staging-server:/opt/apps/
                    # ssh staging-server "cd /opt/apps && tar -xzf ${APP_NAME}-${VERSION}.tar.gz"
                '''
            }
        }
        
        stage('Deploy to Production') {
            agent { label 'deployment' }
            when {
                anyOf {
                    branch 'main'
                    branch 'master'
                }
            }
            steps {
                echo "Deploying to production environment..."
                input message: 'Deploy to Production?', ok: 'Deploy'
                sh '''
                    echo "Deploying version ${VERSION} to production"
                    # Add your production deployment commands here
                    # For example:
                    # scp dist/${APP_NAME}-${VERSION}.tar.gz production-server:/opt/apps/
                    # ssh production-server "cd /opt/apps && tar -xzf ${APP_NAME}-${VERSION}.tar.gz"
                '''
            }
        }
        
        stage('Integration Tests') {
            agent { label 'testing' }
            when {
                anyOf {
                    branch 'main'
                    branch 'master'
                    branch 'develop'
                }
            }
            steps {
                echo "Running integration tests..."
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    
                    # Run integration tests (you can add more comprehensive tests here)
                    python -m pytest test_app.py::WeekendTaskManagerTests::test_api_get_tasks -v
                    python -m pytest test_app.py::WeekendTaskManagerTests::test_health_check_healthy -v
                '''
            }
        }
    }
    
    post {
        always {
            node('master') {
                echo "Pipeline completed for ${env.BRANCH_NAME} - Version: ${env.VERSION}"
                cleanWs()
            }
        }
        success {
            node('master') {
                echo "Pipeline succeeded!"
                // Add notification logic here (email, Slack, etc.)
            }
        }
        failure {
            node('master') {
                echo "Pipeline failed!"
                // Add failure notification logic here
            }
        }
    }
}