## Real-Time News Recommendation System

The Real-Time News Recommendation System is designed to deliver personalized, up-to-date news content tailored to individual user preferences and behaviors. With the rapid growth of digital platforms as primary news sources, users face an overwhelming flood of information, making it challenging to find content relevant to their interests. This project addresses this issue by leveraging machine learning models, real-time data streaming, and a scalable framework to create a seamless and curated news experience.


## Key Features
1.**Personalized Recommendations**: Uses advanced recommendation algorithms to match news content with individual user preferences.
2.**Real-Time Processing**: Processes and analyzes news data in real time to ensure recommendations are always relevant and timely.
3.**User Behavior Analysis**: Tracks user interactions, such as click-through rates and reading patterns, to gain insights into behavior.
4.**Dynamic Feedback Loop**: Continuously updates and improves recommendations based on user behavior and preferences.
5.**Scalable Framework**: Designed to handle high volumes of data and users, ensuring consistent performance.


## Technical Overview
The system integrates several robust technologies:

1.**Machine Learning Models**: To predict and recommend content based on user preferences and behavior.
2.**Real-Time Data Streaming**: Ensures immediate processing and analysis of incoming data.
3.**Scalable Infrastructure**: Built with technologies like Kafka, BigQuery, and Databricks to handle massive data volumes.
4.**User Interaction Monitoring**: Tracks and analyzes click-through rates and engagement metrics to improve recommendations dynamically.
5.**Frontend & Backend Integration**: Seamless flow from user interaction to backend processing and recommendation delivery.


## Deployment Steps

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
