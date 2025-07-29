## Jenkins CI/CD Pipeline

This project uses a Jenkins pipeline to automatically test, build, and deploy the Django application to OpenShift.

### Pipeline Overview

- **Trigger:** Runs on every push to the 'master' branch.
- **Environment:** Docker, OpenShift, Jenkins

---

### Pipeline Stages

#### 1. **Clone**
Clones the 'master' branch of the repository using the Git plugin.

#### 2. **Test**
Executes Django tests using 'python manage.py test'.

#### 3. **Build**
Builds a new Docker image from the project directory:
'''
docker build --no-cache -t athalt/tripcraft:openshift .
'''

#### 4. **Push**
Pushes the Docker image to DockerHub using Jenkins credentials:
'''
docker push athalt/tripcraft:openshift
'''

#### 5. **Deploy**
Restarts the OpenShift deployment to pick up the new images:
'''
oc rollout restart deployment/django
'''

---

### Credentials

Make sure Jenkins has a credential entry with ID 'dockerHub' containing your DockerHub username and login token.

---

### Dependencies

- Docker
- OpenShift CLI ('oc')
- Jenkins (with Git, Docker, and Credentials plugins)

---

### Notes

- The default checkout is skipped using 'skipDefaultCheckout(true)' to allow manual git cloning.
- Tests run inside the live OpenShift environment, so 'oc' CLI access must be configured on the Jenkins node.