# EmotCare - Cloudflare Deployment Guide

This guide will walk you through deploying the EmotCare application to Cloudflare using Wrangler CLI.

## Prerequisites

1. Node.js and npm installed
2. Cloudflare account
3. Wrangler CLI installed

## Setup Steps

### 1. Install Wrangler CLI

```bash
npm install -g wrangler
```

### 2. Login to Cloudflare

```bash
wrangler login
```

### 3. Create KV Namespace

```bash
wrangler kv:namespace create "emotcare-kv"
```

After running this command, update the ID in wrangler.toml with the one returned.

### 4. Deploy to Cloudflare Workers

```bash
wrangler deploy
```

## Redis Configuration

The application is already configured to use Upstash Redis with the following URL:
`redis://default:AZrAAAIjcDE0ODA0MzFiMWVmYmI0NjU2OTM4NjMyNmM3ODBmZDFiNXAxMA@talented-shrimp-39616.upstash.io:6379`

## Email Configuration

The application uses Gmail for sending emails with these credentials:
- Email: faceauth01@gmail.com
- Password: tavx rome qann smoq

## Troubleshooting

If you encounter any issues during deployment:

1. Check Cloudflare Workers logs in the Cloudflare dashboard
2. Make sure all environment variables are correctly set in wrangler.toml
3. Verify Redis connection by running a test connection
