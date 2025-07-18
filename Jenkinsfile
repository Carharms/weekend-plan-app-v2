
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

        stage('Database Setup') {
            steps {
                script {
                    try {
                        // Clean up any existing containers first
                        bat '''
                        echo Cleaning up any existing MySQL containers...
                        docker stop mysql-server-temp 2>nul || echo "No existing container to stop"
                        docker rm mysql-server-temp 2>nul || echo "No existing container to remove"
                        '''
                        
                        // Start MySQL server container on a different port
                        bat '''
                        echo Starting MySQL server container on port 3307...
                        docker run --name mysql-server-temp -e MYSQL_ROOT_PASSWORD=%DB_PASSWORD% -e MYSQL_DATABASE=%DB_NAME% -p 3307:3306 -d mysql:8.0
                        '''
                        
                        // Wait for MySQL to be ready
                        bat '''
                        echo Waiting for MySQL to be ready...
                        timeout /t 45 /nobreak
                        '''
                        
                        // Test connection multiple times to ensure readiness
                        bat '''
                        echo Testing MySQL connection...
                        for /l %%i in (1,1,5) do (
                            docker exec mysql-server-temp mysql -u root -p%DB_PASSWORD% -e "SELECT 'MySQL is ready!' as status;" && goto :ready
                            echo Attempt %%i failed, waiting 10 more seconds...
                            timeout /t 10 /nobreak
                        )
                        :ready
                        '''
                        
                        // Create database and tables
                        bat '''
                        echo Creating database schema...
                        docker exec -i mysql-server-temp mysql -u root -p%DB_PASSWORD% < database.sql
                        '''
                        
                        // Seed data
                        bat '''
                        echo Seeding test data...
                        docker exec -i mysql-server-temp mysql -u root -p%DB_PASSWORD% %DB_NAME% < seed_data.sql
                        '''
                        
                        // Verify setup
                        bat '''
                        echo Verifying database setup...
                        docker exec mysql-server-temp mysql -u root -p%DB_PASSWORD% -e "USE %DB_NAME%; SHOW TABLES; SELECT COUNT(*) as 'Total Records' FROM weekend_tasks; SELECT day, COUNT(*) as 'Events per Day' FROM weekend_tasks GROUP BY day;"
                        '''
                        
                        echo "✓ Database setup completed successfully!"
                        
                    } catch (Exception e) {
                        echo "Error during database setup: ${e.getMessage()}"
                        // Show container logs for debugging
                        bat '''
                        echo Showing container logs for debugging...
                        docker logs mysql-server-temp || echo "No logs available"
                        '''
                        throw e
                    } finally {
                        // Clean up: stop and remove the temporary container
                        bat '''
                        echo Cleaning up temporary MySQL container...
                        docker stop mysql-server-temp || echo "Container already stopped"
                        docker rm mysql-server-temp || echo "Container already removed"
                        '''
                    }
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