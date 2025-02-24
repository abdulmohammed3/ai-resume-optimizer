# GitHub Container Registry Setup Guide

## 1. Create Personal Access Token (PAT)

1. Go to GitHub.com and navigate to Settings > Developer settings > Personal access tokens > Tokens (classic)
2. Click "Generate new token (classic)"
3. Give your token a descriptive name (e.g., "GHCR Access")
4. Set expiration as needed
5. Select the following scopes:
   - `write:packages`
   - `read:packages`
   - `delete:packages`
   - `repo` (if repository is private)
6. Click "Generate token"
7. **Important**: Copy and save your token immediately! You won't be able to see it again.

## 2. Authenticate with GHCR

```bash
# Login to GHCR using your GitHub username and PAT
echo "YOUR_PAT" | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

## 3. Tag Images for GHCR

```bash
# Tag backend image
docker tag ai-resume-optimizer-flask:v1.0.0 ghcr.io/YOUR_GITHUB_USERNAME/ai-resume-optimizer-flask:v1.0.0

# Tag frontend image
docker tag ai-resume-optimizer-frontend:v1.0.0 ghcr.io/YOUR_GITHUB_USERNAME/ai-resume-optimizer-frontend:v1.0.0
```

## 4. Push Images to GHCR

```bash
# Push backend image
docker push ghcr.io/YOUR_GITHUB_USERNAME/ai-resume-optimizer-flask:v1.0.0

# Push frontend image
docker push ghcr.io/YOUR_GITHUB_USERNAME/ai-resume-optimizer-frontend:v1.0.0
```

## 5. Update docker-compose.yml

After pushing, update your docker-compose.yml to use the GHCR images:

```yaml
services:
  flask-backend:
    image: ghcr.io/YOUR_GITHUB_USERNAME/ai-resume-optimizer-flask:v1.0.0
    # ... rest of config

  react-frontend:
    image: ghcr.io/YOUR_GITHUB_USERNAME/ai-resume-optimizer-frontend:v1.0.0
    # ... rest of config
```

## Notes
- Make your repository public or configure appropriate permissions if private
- Images in GHCR will be linked to your GitHub repository
- You can manage packages through GitHub's package settings