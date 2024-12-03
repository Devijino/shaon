pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Building...'
                // Insert your build commands here, for example:
                // sh 'mvn clean compile'
            }
        }
        stage('Test') {
            steps {
                echo 'Testing...'
                // Insert your test commands here, for example:
                // sh 'mvn test'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying...'
                // Insert your deployment commands here, for example:
                // sh 'scp target/myapp.jar user@server:/path/'
            }
        }
    }
}
