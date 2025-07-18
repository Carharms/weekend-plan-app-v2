
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
            def workspace = pwd().replace('\\', '/')
            docker.image('python:3.11-slim').inside("-v ${workspace}:/workspace -w /workspace") {
                sh 'apt-get update && apt-get install -y default-mysql-client'
                sh 'pip install -r requirements.txt'
            }
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




    stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    bat '''
                    set JAVA_HOME=C:\\Program Files\\Java\\jdk-21
                    set PATH=%JAVA_HOME%\\bin;%PATH%
                    %SONAR_SCANNER_HOME%\\bin\\sonar-scanner.bat ^
                    -Dsonar.projectKey=weekend-app ^
                    -Dsonar.sources=. ^
                    -Dsonar.host.url=%SONAR_HOST_URL% ^
                    -Dsonar.login=%SONAR_AUTH_TOKEN% ^
                    -Dsonar.python.coverage.reportPaths=coverage.xml
                    '''
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
}