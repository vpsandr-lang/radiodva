# 🚀 RADIO DVA — Deployment Guide

## Deploy to Render.com (Recommended)

### Automatic (via API)
```bash
./deploy.sh rnd_PuauSTOlQmzQEsaNnxgshFSHtzJk
```

### Manual (via Dashboard)
1. Go to https://dashboard.render.com
2. Click **New +** → **Web Service**
3. Connect your GitHub: `vpsandr-lang/radiodva`
4. Configure:
   - **Name**: `radiodva`
   - **Runtime**: `Docker`
   - **Branch**: `main`
   - **Plan**: Free
   - **Region**: Frankfurt
   - **Health Check Path**: `/api/health`
5. Add Environment Variable: `PORT = 5050`
6. Click **Create Web Service**

### After Deployment
Your radio will be live at: `https://radiodva.onrender.com`

## Deploy to VPS (Manual)

```bash
# Ubuntu/Debian
apt update && apt install -y python3 python3-pip lame
cd /opt
git clone https://github.com/vpsandr-lang/radiodva.git
cd radiodva
python3 run.py &
```

## Domain Setup (radiodva.ru)
1. Register domain at reg.ru (~200₽/year)
2. Add CNAME record: `radiodva.ru → radiodva.onrender.com`
3. Enable HTTPS in Render dashboard
4. Verify in Yandex.Webmaster

## SEO
- Yandex verification tag is in `index.html` (update the key)
- Google Search Console tag is in `index.html` (update the key)
- Sitemap: `https://radiodva.ru/sitemap.xml`
- Robots.txt: `https://radiodva.ru/robots.txt`
- Schema.org RadioBroadcastService: included in `index.html`
