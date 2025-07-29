## Jenkins CI/CD Pipeline

This project uses Jenkins to automatically test, build, and deploy a Django app to OpenShift.

### Pipeline Overview

- **Triggers:** Every time someone pushes to the 'master' branch
- **Tools Used:** Docker, OpenShift, Jenkins

---

### Pipeline Stages

#### 1. **Clone**
Grabs the latest code from the 'master' branch using Git.

#### 2. **Test**
Runs Django tests with 'python manage.py test'.

#### 3. **Build**
Makes a new Docker image (no cache):
'''
docker build --no-cache -t athalt/tripcraft:openshift .
'''

#### 4. **Push**
Sends the image to DockerHub (You'll need credentials set up to log in):
'''
docker push athalt/tripcraft:openshift
'''

#### 5. **Deploy**
Restarts the deployment on OpenShift to use the new image:
'''
oc rollout restart deployment/django
'''

---

### Credentials

Make sure Jenkins has a DockerHub login saved with the ID dockerHub.

---

### Dependencies

- Docker
- OpenShift CLI (oc)
- Jenkins with plugins: Git, Docker, Credentials

---

### Notes

- Jenkins skips the default git checkout on purpose so it can clne manually.
- The tests run inside the actual OpenShift environment, so Jenkins must be allowed to use oc.