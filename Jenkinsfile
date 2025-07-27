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
                echo "Cloning code"
                git url: "https://github.com/Ath-Alt/tripcraft.git", branch: "master"
            }
        }
        
        stage("Build") {
            steps {
                echo "Building image"
                sh "docker build -t athalt/tripcraft ."
            }
        }
        
        stage("Push") {
            steps {
                echo "Pushing to DockerHub"
                withCredentials([usernamePassword(credentialsId: "dockerHub", passwordVariable: "dockerHubPass", usernameVariable: "dockerHubUser")]) {
                    sh "docker login -u ${env.dockerHubUser} -p ${env.dockerHubPass}"
                    sh "docker push ${env.dockerHubUser}/tripcraft"
                }
            }
        }
    }
}