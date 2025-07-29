pipeline {
    agent any
    triggers {
        githubPush()
    }
    options {
        skipDefaultCheckout(true)
    }
    
    stages {
        stage("Clone") {
            steps {
                echo "Cloning app"
                git url: "https://github.com/Ath-Alt/tripcraft.git", branch: "master"
            }
        }

        stage("Build") {
            steps {
                script {
                    tripcraft = docker.build("athalt/tripcraft:openshift")
                }
            }
        }

        stage("Test") {
            steps {
                script {
                    tripcraft.inside {
                        sh 'python manage.py test'
                    }
                }
            }
        }
        
        stage("Push") {
            steps {
                echo "Pushing to DockerHub"
                withCredentials([usernamePassword(credentialsId: "dockerHub", passwordVariable: "dockerHubPass", usernameVariable: "dockerHubUser")]) {
                    sh "docker login -u ${env.dockerHubUser} -p ${env.dockerHubPass}"
                    sh "docker push ${env.dockerHubUser}/tripcraft:openshift"
                }
            }
        }

        stage("Deploy") {
            steps {
                echo "Deploying to OpenShift"
                sh "oc rollout restart deployment/django"
            }
        }
    }
}