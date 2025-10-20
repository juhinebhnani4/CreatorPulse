# 🚀 Production Deployment Checklist

**Last Updated:** January 20, 2025
**Version:** 1.0.0
**Status:** Ready for Production

This comprehensive checklist ensures your CreatorPulse AI Newsletter system is production-ready.

---

## 📋 Table of Contents

1. [Pre-Deployment Verification](#pre-deployment-verification)
2. [Environment Setup](#environment-setup)
3. [Database Configuration](#database-configuration)
4. [Security Hardening](#security-hardening)
5. [Performance Optimization](#performance-optimization)
6. [Monitoring & Logging](#monitoring--logging)
7. [Deployment Steps](#deployment-steps)
8. [Post-Deployment Verification](#post-deployment-verification)
9. [Rollback Plan](#rollback-plan)

---

## ✅ Pre-Deployment Verification

### Code Quality Checks

- [ ] **Run all tests**
  ```bash
  cd scraper-scripts
  .venv\Scripts\activate  # Windows
  source .venv/bin/activate  # Mac/Linux
  python tests/test_integrations.py
  ```
  **Expected:** 6/6 tests passing

- [ ] **Check syntax on all Python files**
  ```bash
  python -m py_compile backend/**/*.py
  python -m py_compile src/**/*.py
  ```

- [ ] **Review git status**
  ```bash
  git status
  git log --oneline -10
  ```
  **Verify:** All changes committed, clean working directory

- [ ] **Code review completed**
  - Review all HIGH priority implementations
  - Review MEDIUM priority implementations
  - Check for TODO comments or debug code

### Documentation Review

- [ ] **Read deployment guide**
  - [ ] Review `docs/DEPLOYMENT_GUIDE.md`
  - [ ] Understand all features and usage
  - [ ] Note configuration requirements

- [ ] **Review rate limiting guide**
  - [ ] Read `docs/RATE_LIMITING_GUIDE.md`
  - [ ] Understand rate limit values
  - [ ] Plan Redis setup for production

- [ ] **API documentation updated**
  - [ ] FastAPI /docs endpoint working
  - [ ] All endpoints documented
  - [ ] Examples provided

---

## 🔧 Environment Setup

### Python Environment

- [ ] **Python version verified**
  ```bash
  python --version
  # Expected: Python 3.13+ (3.13.8 tested)
  ```

- [ ] **Virtual environment created**
  ```bash
  python -m venv .venv
  .venv\Scripts\activate  # Windows
  source .venv/bin/activate  # Mac/Linux
  ```

- [ ] **Dependencies installed**
  ```bash
  pip install -r requirements.txt
  pip install slowapi redis  # For rate limiting
  ```

### Environment Variables (.env)

Create production `.env` file with all required keys:

#### Required Variables

- [ ] **Database Configuration**
  ```bash
  SUPABASE_URL=https://your-project.supabase.co
  SUPABASE_KEY=your-anon-key
  SUPABASE_SERVICE_KEY=your-service-role-key
  ```

- [ ] **API Keys**
  ```bash
  # Choose one: OpenAI or OpenRouter
  OPENAI_API_KEY=sk-...
  # OR
  OPENROUTER_API_KEY=sk-or-v1-...
  USE_OPENROUTER=false  # or true
  ```

- [ ] **Security Keys**
  ```bash
  SECRET_KEY=your-jwt-secret-key-here
  ANALYTICS_SECRET_KEY=your-hmac-secret-key-here
  ```

- [ ] **Email Configuration** (choose one)
  ```bash
  # SMTP
  SMTP_SERVER=smtp.gmail.com
  SMTP_PORT=587
  SMTP_USERNAME=your-email@gmail.com
  SMTP_PASSWORD=your-app-password
  FROM_EMAIL=your-email@gmail.com

  # OR SendGrid
  SENDGRID_API_KEY=SG.your-key-here
  USE_SENDGRID=true
  ```

#### Optional Configuration

- [ ] **Performance Tuning**
  ```bash
  # Trend boosting (default 1.3 = 30%)
  TREND_SCORE_BOOST_MULTIPLIER=1.3

  # Max trends to fetch (default 5)
  MAX_TRENDS_TO_FETCH=5

  # Content fetch multiplier (default 2)
  CONTENT_FETCH_MULTIPLIER=2
  ```

- [ ] **Rate Limiting**
  ```bash
  DEFAULT_RATE_LIMIT=100/minute
  NEWSLETTER_GENERATION_LIMIT=5/minute
  TREND_DETECTION_LIMIT=10/minute
  STYLE_TRAINING_LIMIT=10/minute
  ANALYTICS_EVENT_LIMIT=1000/minute

  # For production - use Redis
  RATE_LIMIT_STORAGE_URI=redis://localhost:6379
  ```

- [ ] **Logging**
  ```bash
  LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
  ENVIRONMENT=production
  ```

### Verify Environment Variables

- [ ] **Test loading**
  ```python
  from dotenv import load_dotenv
  import os

  load_dotenv()

  # Check critical keys
  assert os.getenv("SUPABASE_URL"), "SUPABASE_URL missing"
  assert os.getenv("ANALYTICS_SECRET_KEY"), "ANALYTICS_SECRET_KEY missing"
  print("✅ All required environment variables set")
  ```

---

## 🗄️ Database Configuration

### Supabase Setup

- [ ] **Database schema deployed**
  - [ ] Run migrations: `alembic upgrade head`
  - [ ] Verify all tables exist
  - [ ] Check indexes created

- [ ] **Row Level Security (RLS) enabled**
  - [ ] workspaces table RLS policies
  - [ ] newsletters table RLS policies
  - [ ] content_items table RLS policies
  - [ ] trends table RLS policies
  - [ ] style_profiles table RLS policies
  - [ ] feedback table RLS policies

- [ ] **Database backups configured**
  - [ ] Supabase automatic backups enabled
  - [ ] Backup retention period set (30 days recommended)
  - [ ] Test restore procedure

- [ ] **Connection pooling configured**
  - [ ] Max connections set appropriately
  - [ ] Connection timeout configured
  - [ ] Idle timeout configured

### Test Database Connectivity

- [ ] **Test queries**
  ```python
  from src.ai_newsletter.database.supabase_client import SupabaseManager

  db = SupabaseManager()

  # Test read
  workspaces = db.list_workspaces(limit=1)
  print(f"✅ Database read successful: {len(workspaces)} workspaces")

  # Test write (optional - use test workspace)
  # test_workspace = db.create_workspace(...)
  ```

---

## 🔒 Security Hardening

### Authentication & Authorization

- [ ] **JWT secret key rotated**
  - [ ] Generate new production secret key
  - [ ] Never use example/development keys
  - [ ] Store securely (env vars, not in code)

- [ ] **HMAC secret key generated**
  ```python
  import secrets
  print(secrets.token_hex(32))
  # Add to .env as ANALYTICS_SECRET_KEY
  ```

- [ ] **API key security**
  - [ ] OpenAI/OpenRouter keys are production keys
  - [ ] Keys have usage limits/monitoring enabled
  - [ ] Keys are workspace-specific if possible

- [ ] **CORS configured**
  ```python
  # In backend/main.py
  from fastapi.middleware.cors import CORSMiddleware

  app.add_middleware(
      CORSMiddleware,
      allow_origins=["https://yourdomain.com"],  # Specific domains only!
      allow_credentials=True,
      allow_methods=["GET", "POST", "PUT", "DELETE"],
      allow_headers=["*"],
  )
  ```

### Input Validation

- [ ] **Pydantic models for all endpoints**
  - [ ] Request validation enabled
  - [ ] Response validation enabled
  - [ ] Error messages don't leak sensitive info

- [ ] **SQL injection prevention**
  - [ ] Using Supabase ORM (not raw SQL)
  - [ ] All queries parameterized
  - [ ] No string concatenation in queries

- [ ] **XSS prevention**
  - [ ] HTML content sanitized
  - [ ] User input escaped
  - [ ] Content Security Policy headers set

### Secrets Management

- [ ] **Environment variables secured**
  - [ ] .env file in .gitignore ✅ (already done)
  - [ ] Production secrets never committed to git
  - [ ] Use secret management service (AWS Secrets Manager, etc.)

- [ ] **API keys rotation plan**
  - [ ] Document key rotation procedure
  - [ ] Schedule regular rotation (90 days)
  - [ ] Test rotation in staging first

---

## ⚡ Performance Optimization

### Caching

- [ ] **Redis setup for rate limiting**
  ```bash
  # Install Redis
  docker run -d --name redis -p 6379:6379 redis:alpine

  # Or use managed Redis (AWS ElastiCache, Redis Cloud, etc.)
  ```

- [ ] **Configure Redis connection**
  ```bash
  RATE_LIMIT_STORAGE_URI=redis://localhost:6379
  ```

- [ ] **Test Redis connectivity**
  ```python
  import redis
  r = redis.from_url("redis://localhost:6379")
  r.set("test", "value")
  assert r.get("test") == b"value"
  print("✅ Redis connection successful")
  ```

### Database Optimization

- [ ] **Query optimization**
  - [ ] Indexes on frequently queried columns
  - [ ] EXPLAIN ANALYZE on slow queries
  - [ ] Pagination on large result sets

- [ ] **Connection pooling**
  - [ ] Supabase client connection pool configured
  - [ ] Max connections appropriate for load
  - [ ] Connection recycling enabled

### API Performance

- [ ] **Response compression enabled**
  ```python
  from fastapi.middleware.gzip import GZipMiddleware
  app.add_middleware(GZipMiddleware, minimum_size=1000)
  ```

- [ ] **Async/await used consistently**
  - [ ] All I/O operations async
  - [ ] No blocking calls in async functions
  - [ ] Database calls are async

---

## 📊 Monitoring & Logging

### Logging Configuration

- [ ] **Structured logging enabled**
  ```python
  import logging

  logging.basicConfig(
      level=logging.INFO,
      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
      handlers=[
          logging.FileHandler('logs/app.log'),
          logging.StreamHandler()
      ]
  )
  ```

- [ ] **Log rotation configured**
  ```python
  from logging.handlers import RotatingFileHandler

  handler = RotatingFileHandler(
      'logs/app.log',
      maxBytes=10*1024*1024,  # 10MB
      backupCount=5
  )
  ```

- [ ] **Sensitive data redacted**
  - [ ] API keys not logged
  - [ ] Passwords not logged
  - [ ] User emails masked in logs

### Error Tracking

- [ ] **Error monitoring service integrated**
  - [ ] Sentry, Rollbar, or similar
  - [ ] Error grouping configured
  - [ ] Alerts set up for critical errors

- [ ] **Exception handling comprehensive**
  - [ ] All endpoints have try/catch
  - [ ] Errors logged with context
  - [ ] User-friendly error messages returned

### Performance Monitoring

- [ ] **Metrics collection**
  - [ ] Request latency tracked
  - [ ] Database query times monitored
  - [ ] AI model response times logged

- [ ] **Health check endpoint**
  ```python
  @app.get("/health")
  async def health_check():
      return {
          "status": "healthy",
          "timestamp": datetime.utcnow(),
          "version": "1.0.0"
      }
  ```

- [ ] **Database health check**
  ```python
  @app.get("/health/db")
  async def db_health():
      try:
          db = SupabaseManager()
          db.list_workspaces(limit=1)
          return {"status": "healthy", "database": "connected"}
      except Exception as e:
          return {"status": "unhealthy", "error": str(e)}
  ```

### Analytics

- [ ] **Usage analytics tracked**
  - [ ] Newsletter generation counts
  - [ ] Trend detection usage
  - [ ] Style profile applications
  - [ ] Rate limit hits (429 errors)

- [ ] **Business metrics dashboards**
  - [ ] Daily active users
  - [ ] Newsletters generated per day
  - [ ] API response times
  - [ ] Error rates

---

## 🚀 Deployment Steps

### Pre-Deployment

- [ ] **Backup existing system** (if applicable)
  - [ ] Database snapshot
  - [ ] Code backup
  - [ ] Configuration backup

- [ ] **Staging deployment test** (recommended)
  - [ ] Deploy to staging environment
  - [ ] Run full test suite
  - [ ] Test all critical user flows
  - [ ] Load testing

### Server Setup

- [ ] **Choose deployment platform**
  - [ ] AWS (EC2, ECS, Lambda)
  - [ ] Google Cloud (Compute Engine, Cloud Run)
  - [ ] Azure (App Service)
  - [ ] Heroku
  - [ ] DigitalOcean
  - [ ] Railway
  - [ ] Render

- [ ] **Server specifications**
  - Minimum recommended:
    - [ ] 2 CPU cores
    - [ ] 4GB RAM
    - [ ] 20GB storage
    - [ ] Redis instance

- [ ] **Install system dependencies**
  ```bash
  # Ubuntu/Debian
  sudo apt update
  sudo apt install python3.13 python3-pip python3-venv redis-server nginx

  # Enable services
  sudo systemctl enable redis-server
  sudo systemctl start redis-server
  ```

### Application Deployment

#### Option A: Direct Deployment

- [ ] **Clone repository**
  ```bash
  cd /var/www
  git clone https://github.com/yourusername/scraper-scripts.git
  cd scraper-scripts
  ```

- [ ] **Set up virtual environment**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  pip install slowapi redis gunicorn
  ```

- [ ] **Copy production .env**
  ```bash
  cp .env.production .env
  # Or use secret management service
  ```

- [ ] **Run migrations**
  ```bash
  alembic upgrade head
  ```

- [ ] **Start application**
  ```bash
  # Using Gunicorn
  gunicorn backend.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log
  ```

#### Option B: Docker Deployment

- [ ] **Build Docker image**
  ```dockerfile
  # Create Dockerfile
  FROM python:3.13-slim

  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt

  COPY . .

  EXPOSE 8000
  CMD ["gunicorn", "backend.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
  ```

- [ ] **Build and push**
  ```bash
  docker build -t creatorpulse-backend:latest .
  docker tag creatorpulse-backend:latest your-registry/creatorpulse-backend:latest
  docker push your-registry/creatorpulse-backend:latest
  ```

- [ ] **Create docker-compose.yml**
  ```yaml
  version: '3.8'
  services:
    backend:
      image: your-registry/creatorpulse-backend:latest
      ports:
        - "8000:8000"
      env_file:
        - .env
      depends_on:
        - redis

    redis:
      image: redis:alpine
      ports:
        - "6379:6379"
  ```

- [ ] **Deploy**
  ```bash
  docker-compose up -d
  ```

### Reverse Proxy Setup (Nginx)

- [ ] **Configure Nginx**
  ```nginx
  # /etc/nginx/sites-available/creatorpulse
  server {
      listen 80;
      server_name api.yourdomain.com;

      location / {
          proxy_pass http://localhost:8000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }
  }
  ```

- [ ] **Enable site**
  ```bash
  sudo ln -s /etc/nginx/sites-available/creatorpulse /etc/nginx/sites-enabled/
  sudo nginx -t
  sudo systemctl reload nginx
  ```

### SSL/TLS Setup

- [ ] **Install Certbot**
  ```bash
  sudo apt install certbot python3-certbot-nginx
  ```

- [ ] **Obtain certificate**
  ```bash
  sudo certbot --nginx -d api.yourdomain.com
  ```

- [ ] **Auto-renewal enabled**
  ```bash
  sudo certbot renew --dry-run
  ```

### Process Management

- [ ] **Create systemd service**
  ```ini
  # /etc/systemd/system/creatorpulse.service
  [Unit]
  Description=CreatorPulse Backend API
  After=network.target redis.service

  [Service]
  Type=notify
  User=www-data
  WorkingDirectory=/var/www/scraper-scripts
  Environment="PATH=/var/www/scraper-scripts/.venv/bin"
  ExecStart=/var/www/scraper-scripts/.venv/bin/gunicorn backend.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
  Restart=always

  [Install]
  WantedBy=multi-user.target
  ```

- [ ] **Enable and start service**
  ```bash
  sudo systemctl daemon-reload
  sudo systemctl enable creatorpulse
  sudo systemctl start creatorpulse
  sudo systemctl status creatorpulse
  ```

---

## ✓ Post-Deployment Verification

### Functional Testing

- [ ] **Health check endpoint**
  ```bash
  curl https://api.yourdomain.com/health
  # Expected: {"status": "healthy", ...}
  ```

- [ ] **Database connectivity**
  ```bash
  curl https://api.yourdomain.com/health/db
  # Expected: {"status": "healthy", "database": "connected"}
  ```

- [ ] **API documentation accessible**
  ```bash
  # Open in browser
  https://api.yourdomain.com/docs
  ```

### Feature Testing

- [ ] **Authentication works**
  - [ ] Signup new user
  - [ ] Login existing user
  - [ ] JWT token received and valid

- [ ] **Newsletter generation**
  - [ ] Create test newsletter
  - [ ] Verify trends applied
  - [ ] Verify style profile used
  - [ ] Check feedback adjustments

- [ ] **Analytics tracking**
  - [ ] Generate HMAC token
  - [ ] Record analytics event
  - [ ] Verify event stored

- [ ] **Rate limiting active**
  ```bash
  # Test rate limit (should get 429 after 5 requests)
  for i in {1..10}; do
    curl -X POST https://api.yourdomain.com/api/v1/newsletters/generate
  done
  ```

### Performance Testing

- [ ] **Response times acceptable**
  - [ ] GET /health < 100ms
  - [ ] POST /generate < 10s (with AI)
  - [ ] GET /newsletters < 500ms

- [ ] **Load testing**
  ```bash
  # Using Apache Bench
  ab -n 1000 -c 10 https://api.yourdomain.com/health

  # Or use k6, Locust, etc.
  ```

- [ ] **Database performance**
  - [ ] Query times monitored
  - [ ] No slow queries (>1s)
  - [ ] Connection pool not exhausted

### Security Verification

- [ ] **SSL certificate valid**
  ```bash
  openssl s_client -connect api.yourdomain.com:443 -servername api.yourdomain.com
  ```

- [ ] **Security headers present**
  ```bash
  curl -I https://api.yourdomain.com
  # Should include:
  # X-Content-Type-Options: nosniff
  # X-Frame-Options: DENY
  # Strict-Transport-Security: max-age=31536000
  ```

- [ ] **No sensitive data exposed**
  - [ ] Error messages don't leak stack traces
  - [ ] API keys not in responses
  - [ ] Database connection strings not exposed

### Monitoring Verification

- [ ] **Logs being written**
  ```bash
  tail -f logs/app.log
  tail -f logs/error.log
  ```

- [ ] **Metrics being collected**
  - [ ] Request counts incrementing
  - [ ] Response times tracked
  - [ ] Error rates monitored

- [ ] **Alerts configured**
  - [ ] High error rate alert
  - [ ] Service down alert
  - [ ] Database connection failure alert
  - [ ] Disk space alert

---

## 🔄 Rollback Plan

### Preparation

- [ ] **Document current version**
  ```bash
  git log -1 --oneline > DEPLOYED_VERSION.txt
  ```

- [ ] **Database migration rollback tested**
  ```bash
  alembic downgrade -1  # Test in staging first
  ```

### Rollback Procedure

If issues occur after deployment:

1. **Stop application**
   ```bash
   sudo systemctl stop creatorpulse
   ```

2. **Restore previous code**
   ```bash
   git checkout <previous-commit-hash>
   ```

3. **Rollback database** (if migrations ran)
   ```bash
   alembic downgrade -1
   ```

4. **Restart application**
   ```bash
   sudo systemctl start creatorpulse
   ```

5. **Verify rollback successful**
   ```bash
   curl https://api.yourdomain.com/health
   ```

### Communication

- [ ] **Notify stakeholders** of rollback
- [ ] **Document issues** encountered
- [ ] **Schedule post-mortem** meeting

---

## 📝 Post-Deployment Tasks

### Documentation

- [ ] **Update deployment documentation**
  - [ ] Record deployment date and version
  - [ ] Document any issues encountered
  - [ ] Update troubleshooting guide

- [ ] **Update runbook**
  - [ ] Common operations documented
  - [ ] Emergency procedures updated
  - [ ] Contact information current

### Monitoring Setup

- [ ] **Set up uptime monitoring**
  - [ ] Pingdom, UptimeRobot, or similar
  - [ ] Check every 5 minutes
  - [ ] Alert on 2+ failures

- [ ] **Configure log aggregation**
  - [ ] Elasticsearch + Kibana
  - [ ] Splunk
  - [ ] CloudWatch Logs
  - [ ] Datadog

- [ ] **Set up APM** (Application Performance Monitoring)
  - [ ] New Relic
  - [ ] Datadog
  - [ ] AppDynamics

### User Communication

- [ ] **Announce launch** (if new system)
- [ ] **Send migration guide** (if upgrading)
- [ ] **Provide support channel**
  - [ ] Email
  - [ ] Slack/Discord
  - [ ] Documentation site

### Ongoing Maintenance

- [ ] **Schedule regular backups**
  - [ ] Database: Daily
  - [ ] Code: On every deployment
  - [ ] Configs: Weekly

- [ ] **Plan for updates**
  - [ ] Security patches: As soon as possible
  - [ ] Dependency updates: Monthly
  - [ ] Feature releases: As needed

- [ ] **Monitor costs**
  - [ ] OpenAI/OpenRouter API usage
  - [ ] Server costs
  - [ ] Database storage
  - [ ] Redis/cache costs

---

## 🎯 Success Criteria

Your deployment is successful when:

- [x] All tests passing (6/6)
- [ ] Application accessible via HTTPS
- [ ] Health checks returning 200 OK
- [ ] Authentication working
- [ ] Newsletter generation functional
- [ ] Trends integration working
- [ ] Style profiles applying
- [ ] Feedback learning active
- [ ] Analytics tracking secured
- [ ] Rate limiting protecting endpoints
- [ ] Logs being written
- [ ] Monitoring active
- [ ] Alerts configured
- [ ] No critical errors in logs
- [ ] Response times < SLA
- [ ] Database queries performant
- [ ] SSL certificate valid
- [ ] Users can access system

---

## 📞 Support Contacts

**Emergency Contacts:**
- Primary: [Your Name] - [email/phone]
- Secondary: [Team Lead] - [email/phone]

**Service Contacts:**
- Supabase Support: support@supabase.com
- OpenAI Support: support@openai.com
- Hosting Provider: [your hosting support]

**Escalation Path:**
1. Check logs and monitoring
2. Review recent deployments
3. Contact primary on-call
4. Escalate to team lead if needed
5. Engage vendor support if infrastructure issue

---

## ✅ Final Sign-Off

- [ ] **Deployment completed by:** _________________ Date: _________
- [ ] **Verification completed by:** _________________ Date: _________
- [ ] **Approved for production by:** _________________ Date: _________

---

## 📚 Additional Resources

- **Deployment Guide:** `docs/DEPLOYMENT_GUIDE.md`
- **Rate Limiting Guide:** `docs/RATE_LIMITING_GUIDE.md`
- **Test Suite:** `tests/test_integrations.py`
- **Git Repository:** [Your repo URL]
- **Documentation Site:** [Your docs URL]

---

**🎉 Congratulations on your production deployment!**

Remember to:
- Monitor closely for the first 24-48 hours
- Respond quickly to any alerts
- Collect user feedback
- Iterate and improve

Your CreatorPulse AI Newsletter system is now live! 🚀
