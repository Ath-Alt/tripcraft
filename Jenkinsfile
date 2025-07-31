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
                    sh "docker build -t ${env.dockerHubUser}/tripcraft:openshift ."
                }
            }
        }

            stage("Test") {
                steps {
                    echo "Performing tests"
                    sh '''
                        [ -d admin_app ] && [ -d user_app ] && [ -d TripCraft ]
                    '''
                }
            }

        stage("Deploy") {
            steps {
                echo "Deploying to OpenShift"
                withCredentials([usernamePassword(credentialsId: "dockerHub", passwordVariable: "dockerHubPass", usernameVariable: "dockerHubUser")]) {
                    sh "docker login -u ${env.dockerHubUser} -p ${env.dockerHubPass}"
                    sh "docker push ${env.dockerHubUser}/tripcraft:openshift"
                }
                sh "oc import-image django:openshift --confirm"
            }
        }
    }
}