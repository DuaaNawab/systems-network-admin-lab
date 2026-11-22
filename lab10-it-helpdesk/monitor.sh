#!/bin/sh
echo "=== $(date -u) ==="
echo "--- container health ---"
docker compose ps --format 'table {{.Name}}\t{{.Status}}'
echo "--- CPU and memory ---"
docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'
echo "--- API availability and response time ---"
curl -s -o /dev/null -w "GET /health: HTTP %{http_code}, %{time_total}s\n" http://localhost:8080/health
echo "--- database connectivity (through API health) ---"
curl -s http://localhost:8080/health; echo
echo "--- requests by status code (Nginx access log) ---"
docker compose logs nginx --no-log-prefix 2>/dev/null | grep -oE '" [0-9]{3} ' | sort | uniq -c
echo "--- failed model calls / fallbacks (API log) ---"
docker compose logs api --no-log-prefix 2>/dev/null | grep -cE "WARNING"
docker compose logs api --no-log-prefix 2>/dev/null | grep -E "WARNING" | tail -n 5
echo "--- tickets by status ---"
docker compose exec -T db psql -U helpdesk -d it_helpdesk -c "SELECT status, count(*) FROM support_requests GROUP BY status ORDER BY status;"
