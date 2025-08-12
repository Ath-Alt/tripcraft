pipeline {
    agent any
    triggers {
        githubPush()
    }
    
    stages {
        stage("Build") {
            steps {
                echo "Building image"
                withCredentials([usernamePassword(credentialsId: "dockerHub", passwordVariable: "dockerHubPass", usernameVariable: "dockerHubUser")]) {
                    sh "docker build -t ${env.dockerHubUser}/tripcraft:${env.BUILD_NUMBER} ."
                }
            }
        }

        stage("Test") {
            steps {
                echo "Performing tests"
                script {
                    def success = false
                    sh "docker run -d --name tripcraft -p 8000:8000 athalt/tripcraft:latest"
                    sleep 5
                    def logs = sh(script: "docker logs tripcraft 2>&1", returnStdout: true).trim()
                    sh "docker rm -f tripcraft"
                    if (logs.contains("INFO Watching for file changes with StatReloader")) {
                        echo "Container passed running test"
                    }
                    else {
                        error "Container failed running test"
                    }
                }
            }
        }

        stage("Deploy") {
            steps {
                echo "Deploying to OpenShift"
                withCredentials([usernamePassword(credentialsId: "dockerHub", passwordVariable: "dockerHubPass", usernameVariable: "dockerHubUser")]) {
                    sh "docker login -u ${env.dockerHubUser} -p ${env.dockerHubPass}"
                    sh "docker push ${env.dockerHubUser}/tripcraft:${env.BUILD_NUMBER}"
                }
                sh "oc set image deployment/web web=athalt/tripcraft:${env.BUILD_NUMBER}"
            }
        }
    }
}