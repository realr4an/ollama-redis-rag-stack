# Cloud Deployment Playbook

## Azure Container Apps (ACA)
1. **Build & Push Images**
   ```bash
   az acr login --name <registry>
   docker build -t <registry>.azurecr.io/rag-backend:latest backend
   docker build -t <registry>.azurecr.io/rag-frontend:latest frontend
   docker push <registry>.azurecr.io/rag-backend:latest
   docker push <registry>.azurecr.io/rag-frontend:latest
   ```
2. **Provision ACA Environment**
   ```bash
   az containerapp env create \
     --name rag-env \
     --resource-group rag-rg \
     --location westeurope
   ```
3. **Deploy Backend & Frontend**
   ```bash
   az containerapp create \
     --name rag-backend \
     --environment rag-env \
     --image <registry>.azurecr.io/rag-backend:latest \
     --resource-group rag-rg \
     --target-port 8000 \
     --ingress external \
     --env-vars $(cat .env | xargs)
   az containerapp create \
     --name rag-frontend \
     --environment rag-env \
     --image <registry>.azurecr.io/rag-frontend:latest \
     --resource-group rag-rg \
     --target-port 80 \
     --ingress external \
     --env-vars VITE_API_BASE_URL=https://<backend-host>
   ```
4. **Managed Redis / Ollama**
   - Use Azure Cache for Redis (Enterprise) with vector similarity.
   - Host Ollama on GPU VM or AKS node pool; update `OLLAMA_HOST`.

## AKS / Kubernetes
- Helm chart (`charts/warehouse-rag`) can be reused.
- Override values via `values.azure.yaml` (example):
  ```yaml
  image:
    repository: <registry>.azurecr.io/rag-backend
    tag: latest
  frontend:
    repository: <registry>.azurecr.io/rag-frontend
    tag: latest
  service:
    type: LoadBalancer
  ```
- Deploy:
  ```bash
  helm upgrade --install rag charts/warehouse-rag -f values.azure.yaml
  ```
- Attach Azure Monitor / App Insights for metrics.

## Automation Tips
- Use GitHub Actions OIDC + `azure/login` for push & deploy.
- Store secrets in Azure Key Vault; mount via `az containerapp secret set`.
- Scale-to-zero for ACA to control costs; configure min/max replicas per workload.
