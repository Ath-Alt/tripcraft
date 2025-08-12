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

                    try {
                        timeout(time: 30, unit: 'SECONDS') {
                            while (!success) {
                                echo "Status: ${success}"
                                def logs = sh(script: "docker logs tripcraft", returnStdout: true).trim()
                                echo "Logs: ${logs}"
                                if (logs.contains("INFO Watching for file changes with StatReloader")) {
                                    success = true
                                } else {
                                    sleep 5
                                }
                            }
                        }
                    } finally {
                        sh "docker rm -f tripcraft"
                    }
                    echo "Container passed running test"
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