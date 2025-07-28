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

        stage("Test") {
            steps {
                echo "Testing app"
                sh '''
                    POD=$(oc get po -l app=django -o jsonpath="{.items[0].metadata.name}")
                    oc exec $POD -- python manage.py test
                '''
            }
        }

        stage("Build") {
            steps {
                echo "Building image"
                sh "docker build --no-cache -t athalt/tripcraft:openshift ."
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