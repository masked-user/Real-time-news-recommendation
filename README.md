
### Project Team Number: 65
### Team Members:
      Aditya Sriram Seshadri
      Nitharshan Coimbatore Venkatesan
      Parimala Gutta
## Deployment Steps for the Project  

### 1. Kafka Deployment on GKE
1. **Create a GKE cluster**:  
   ```bash
   gcloud container clusters create kafka-cluster \  
     --num-nodes=3 \  
     --zone=us-central1-a  
   ```
2. **Authenticate the cluster**:  
   ```bash
   gcloud container clusters get-credentials kafka-cluster --zone=us-central1-a  
   kubectl get nodes  
   ```
3. **Install Helm**:  
   ```bash
   curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash  
   helm repo add bitnami https://charts.bitnami.com/bitnami  
   helm repo update  
   ```
4. **Deploy Kafka with Zookeeper using Helm**:  
   ```bash
   helm install kafka bitnami/kafka \  
     --set replicaCount=3 \  
     --set zookeeper.replicaCount=3 \  
     --set externalAccess.enabled=true \  
     --set externalAccess.service.type=LoadBalancer \  
     --set externalAccess.autoDiscovery.enabled=true \  
     --set rbac.create=true \  
     --set controller.automountServiceAccountToken=true \  
     --set broker.automountServiceAccountToken=true  
   ```
5. **Check Kafka logs and metrics**:  
   ```bash
   kubectl logs kafka-controller-0  
   kubectl get svc  
   ```
6. **Install metrics-server for resource monitoring**:  
   ```bash
   kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.6.1/components.yaml  
   kubectl get deployment metrics-server -n kube-system  
   kubectl logs deployment/metrics-server -n kube-system  
   kubectl top pods  
   ```

---

### 2. Cloud SQL Setup
1. **Create a Cloud SQL database instance**.  
2. **Set up the database and table to store user information**.  
3. **Ensure the backend is updated** with the database connection details, such as instance name, database name, and table name.  
4. **Open the required port (3306)** in the firewall for database access.  

---

### 3. BigQuery Setup
1. **Create BigQuery credentials** to enable secure access.  
2. **Set up a dataset and a table** in BigQuery to store processed clickstream data.  
3. **Update the backend with the credentials** in the required configuration file.  

---

### 4. Databricks and ADF Setup
1. **Create an Azure Data Factory (ADF) account** and set up a new resource group.  
2. **Create a Databricks environment** within the ADF account, ensuring proper configuration.  
3. **Connect BigQuery to Databricks**:  
   - Provide BigQuery credentials to Databricks for  connectivity and data processing.  
   - Configure the Databricks environment to read and write data to and from BigQuery.  

---

### 5. Backend Deployment Using Cloud Run
1. **Authenticate and set up Google Cloud services**:  
   ```bash
   gcloud auth login  
   gcloud config set project [PROJECT_ID]  
   gcloud services enable artifactregistry.googleapis.com  
   gcloud services enable run.googleapis.com  
   gcloud services enable cloudbuild.googleapis.com  
   ```
2. **Add a Dockerfile** to containerize the backend application.  
3. **Test the Docker build locally**:  
   ```bash
   docker build -t flask-backend .  
   docker run -p 8080:8080 flask-backend  
   ```
4. **Create an Artifact Registry repository**:  
   ```bash
   gcloud artifacts repositories create my-repo --repository-format=docker --location=us-central1  
   ```
5. **Tag and push the Docker image**:  
   ```bash
   docker tag flask-backend us-central1-docker.pkg.dev/[PROJECT_ID]/my-repo/flask-backend:latest  
   gcloud auth configure-docker us-central1-docker.pkg.dev  
   docker push us-central1-docker.pkg.dev/[PROJECT_ID]/my-repo/flask-backend:latest  
   ```
6. **Deploy the backend to Cloud Run**:  
   ```bash
   gcloud run deploy flask-backend \  
     --image us-central1-docker.pkg.dev/[PROJECT_ID]/my-repo/flask-backend:latest \  
     --platform managed \  
     --region us-central1 \  
     --allow-unauthenticated \  
     --port 8080  
   ```

---

### 6. Frontend Deployment Using Cloud Storage
1. **Create a Cloud Storage bucket** and upload all static frontend files.  
2. **Update the JavaScript files** with the correct backend API endpoint.  
3. **Deploy the files** to the bucket.  

---

### 7. Configuration and Finalization
1. **Open firewall ports**:  
   - **3306** for MySQL  
   - **8080** for Cloud Run  
   - **9004** for Kafka  
2. **Ensure all services and instances** are deployed in the same zone to reduce latency.  
3. **Configure IAM policies** to allow Cloud Run to access Kafka, Cloud SQL, and BigQuery.  

By following this sequence, The project will be deployed effectively.
