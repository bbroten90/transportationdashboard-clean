# Deployment Guide for Google Cloud Platform

This guide provides step-by-step instructions for deploying the Transportation Dashboard application to Google Cloud Platform (GCP).

## Prerequisites

1. A Google Cloud Platform account
2. Google Cloud SDK installed and configured
3. Docker installed locally
4. Git repository with your application code

## Step 1: Set Up Google Cloud Project

1. Create a new Google Cloud project (or use an existing one):
   ```bash
   gcloud projects create transportation-dashboard --name="Transportation Dashboard"
   gcloud config set project transportation-dashboard
   ```

2. Enable required APIs:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable artifactregistry.googleapis.com
   gcloud services enable sqladmin.googleapis.com
   gcloud services enable documentai.googleapis.com
   gcloud services enable storage.googleapis.com
   ```

## Step 2: Set Up Cloud SQL (PostgreSQL)

1. Create a PostgreSQL instance:
   ```bash
   gcloud sql instances create transportation-db \
     --database-version=POSTGRES_15 \
     --tier=db-f1-micro \
     --region=us-central1 \
     --root-password=your-secure-password
   ```

2. Create a database:
   ```bash
   gcloud sql databases create transportation --instance=transportation-db
   ```

3. Create a user:
   ```bash
   gcloud sql users create transportation-user \
     --instance=transportation-db \
     --password=your-secure-user-password
   ```

4. Get the connection string:
   ```bash
   gcloud sql instances describe transportation-db --format='value(connectionName)'
   ```
   Note this value for later use.

## Step 3: Set Up Cloud Storage Buckets

1. Create buckets for PDF storage:
   ```bash
   gcloud storage buckets create gs://transportation-incoming-pdfs --location=us-central1
   gcloud storage buckets create gs://transportation-processed-pdfs --location=us-central1
   gcloud storage buckets create gs://transportation-error-pdfs --location=us-central1
   ```

## Step 4: Set Up Document AI (Optional)

1. Create a Document AI processor:
   ```bash
   gcloud documentai processor-types list --location=us
   gcloud documentai processors create \
     --processor-type=FORM_PARSER_V2 \
     --location=us \
     --display-name="Transportation Order Processor"
   ```

2. Get the processor ID:
   ```bash
   gcloud documentai processors list --location=us
   ```
   Note the processor ID for later use.

## Step 5: Set Up Artifact Registry

1. Create a Docker repository:
   ```bash
   gcloud artifacts repositories create transportation-repo \
     --repository-format=docker \
     --location=us-central1 \
     --description="Transportation Dashboard Docker repository"
   ```

2. Configure Docker to use the repository:
   ```bash
   gcloud auth configure-docker us-central1-docker.pkg.dev
   ```

## Step 6: Build and Push Docker Images

1. Build and tag the backend image:
   ```bash
   docker build -t us-central1-docker.pkg.dev/transportation-dashboard/transportation-repo/backend:latest -f Dockerfile.backend .
   docker push us-central1-docker.pkg.dev/transportation-dashboard/transportation-repo/backend:latest
   ```

2. Build and tag the frontend image:
   ```bash
   docker build -t us-central1-docker.pkg.dev/transportation-dashboard/transportation-repo/frontend:latest -f Dockerfile.frontend .
   docker push us-central1-docker.pkg.dev/transportation-dashboard/transportation-repo/frontend:latest
   ```

## Step 7: Deploy Backend to Cloud Run

1. Deploy the backend service:
   ```bash
   gcloud run deploy backend \
     --image=us-central1-docker.pkg.dev/transportation-dashboard/transportation-repo/backend:latest \
     --region=us-central1 \
     --platform=managed \
     --allow-unauthenticated \
     --set-env-vars="ENVIRONMENT=production,DATABASE_URL=postgresql://transportation-user:your-secure-user-password@/transportation?host=/cloudsql/YOUR_CONNECTION_NAME,SAMSARA_API_KEY=your-samsara-api-key,GOOGLE_MAPS_API_KEY=your-google-maps-api-key,WEATHER_API_KEY=your-weather-api-key" \
     --add-cloudsql-instances=YOUR_CONNECTION_NAME
   ```
   Replace `YOUR_CONNECTION_NAME` with the connection string from Step 2.

2. Get the backend service URL:
   ```bash
   gcloud run services describe backend --region=us-central1 --format='value(status.url)'
   ```
   Note this URL for the frontend deployment.

## Step 8: Deploy Frontend to Cloud Run

1. Update the Nginx configuration to point to the backend service:
   Edit `nginx.conf` to replace `http://backend:8000` with the backend service URL from Step 7.

2. Rebuild and push the frontend image:
   ```bash
   docker build -t us-central1-docker.pkg.dev/transportation-dashboard/transportation-repo/frontend:latest -f Dockerfile.frontend .
   docker push us-central1-docker.pkg.dev/transportation-dashboard/transportation-repo/frontend:latest
   ```

3. Deploy the frontend service:
   ```bash
   gcloud run deploy frontend \
     --image=us-central1-docker.pkg.dev/transportation-dashboard/transportation-repo/frontend:latest \
     --region=us-central1 \
     --platform=managed \
     --allow-unauthenticated
   ```

4. Get the frontend service URL:
   ```bash
   gcloud run services describe frontend --region=us-central1 --format='value(status.url)'
   ```
   This is the public URL for your application.

## Step 9: Set Up Cloud Scheduler for PDF Processing (Optional)

If you need to periodically process PDFs:

1. Create a service account:
   ```bash
   gcloud iam service-accounts create pdf-processor \
     --display-name="PDF Processor Service Account"
   ```

2. Grant the service account permissions:
   ```bash
   gcloud projects add-iam-policy-binding transportation-dashboard \
     --member="serviceAccount:pdf-processor@transportation-dashboard.iam.gserviceaccount.com" \
     --role="roles/run.invoker"
   ```

3. Create a Cloud Scheduler job:
   ```bash
   gcloud scheduler jobs create http process-pdfs \
     --schedule="*/30 * * * *" \
     --uri="https://backend-url/api/pdf/process-all" \
     --http-method=POST \
     --oidc-service-account-email="pdf-processor@transportation-dashboard.iam.gserviceaccount.com" \
     --oidc-token-audience="https://backend-url"
   ```
   Replace `backend-url` with the backend service URL from Step 7.

## Step 10: Set Up Custom Domain (Optional)

1. Map your custom domain to the frontend service:
   ```bash
   gcloud beta run domain-mappings create \
     --service=frontend \
     --region=us-central1 \
     --domain=your-domain.com
   ```

2. Follow the instructions to verify domain ownership and configure DNS records.

## Step 11: Set Up Monitoring and Logging

1. Set up Cloud Monitoring:
   ```bash
   gcloud monitoring dashboards create \
     --config-from-file=dashboard.json
   ```

2. Set up alerts:
   ```bash
   gcloud alpha monitoring policies create \
     --policy-from-file=alerts.json
   ```

## Step 12: Set Up CI/CD with Cloud Build (Optional)

1. Connect your GitHub repository:
   ```bash
   gcloud builds triggers create github \
     --repo-name=your-repo-name \
     --repo-owner=your-github-username \
     --branch-pattern="^main$" \
     --build-config=cloudbuild.yaml
   ```

2. Create a `cloudbuild.yaml` file in your repository:
   ```yaml
   steps:
   # Build backend
   - name: 'gcr.io/cloud-builders/docker'
     args: ['build', '-t', 'us-central1-docker.pkg.dev/$PROJECT_ID/transportation-repo/backend:$COMMIT_SHA', '-f', 'Dockerfile.backend', '.']
   
   # Build frontend
   - name: 'gcr.io/cloud-builders/docker'
     args: ['build', '-t', 'us-central1-docker.pkg.dev/$PROJECT_ID/transportation-repo/frontend:$COMMIT_SHA', '-f', 'Dockerfile.frontend', '.']
   
   # Push images
   - name: 'gcr.io/cloud-builders/docker'
     args: ['push', 'us-central1-docker.pkg.dev/$PROJECT_ID/transportation-repo/backend:$COMMIT_SHA']
   - name: 'gcr.io/cloud-builders/docker'
     args: ['push', 'us-central1-docker.pkg.dev/$PROJECT_ID/transportation-repo/frontend:$COMMIT_SHA']
   
   # Deploy backend
   - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
     entrypoint: gcloud
     args:
     - 'run'
     - 'deploy'
     - 'backend'
     - '--image=us-central1-docker.pkg.dev/$PROJECT_ID/transportation-repo/backend:$COMMIT_SHA'
     - '--region=us-central1'
     - '--platform=managed'
   
   # Deploy frontend
   - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
     entrypoint: gcloud
     args:
     - 'run'
     - 'deploy'
     - 'frontend'
     - '--image=us-central1-docker.pkg.dev/$PROJECT_ID/transportation-repo/frontend:$COMMIT_SHA'
     - '--region=us-central1'
     - '--platform=managed'
   
   images:
   - 'us-central1-docker.pkg.dev/$PROJECT_ID/transportation-repo/backend:$COMMIT_SHA'
   - 'us-central1-docker.pkg.dev/$PROJECT_ID/transportation-repo/frontend:$COMMIT_SHA'
   ```

## Troubleshooting

### Database Connection Issues

If the backend cannot connect to the database:

1. Check the connection string format:
   ```
   postgresql://transportation-user:your-secure-user-password@/transportation?host=/cloudsql/YOUR_CONNECTION_NAME
   ```

2. Verify the Cloud SQL instance is running:
   ```bash
   gcloud sql instances describe transportation-db --format='value(state)'
   ```

3. Check that the Cloud Run service has the Cloud SQL connection:
   ```bash
   gcloud run services describe backend --region=us-central1
   ```

### API Errors

If you see 500 errors from the API:

1. Check the Cloud Run logs:
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=backend" --limit=10
   ```

2. Verify environment variables are set correctly:
   ```bash
   gcloud run services describe backend --region=us-central1 --format='value(spec.template.spec.containers[0].env)'
   ```

### Frontend Issues

If the frontend cannot connect to the backend:

1. Check the Nginx configuration to ensure it's pointing to the correct backend URL.
2. Verify CORS settings in the backend FastAPI application.
3. Check browser console for network errors.

## Cost Optimization

To optimize costs:

1. Use Cloud Run's auto-scaling to scale to zero when not in use.
2. Choose the appropriate Cloud SQL tier based on your workload.
3. Set up budget alerts to monitor spending.
4. Consider using Compute Engine with a managed instance group for higher workloads.

## Security Best Practices

1. Use service accounts with minimal permissions.
2. Store secrets in Secret Manager instead of environment variables.
3. Enable Cloud Armor for web application firewall protection.
4. Set up VPC Service Controls for additional network security.
5. Regularly update dependencies and container images.
