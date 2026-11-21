import requests
import json
from datetime import datetime

AUTH = ('admin', 'admin')
r = requests.post('http://localhost:3000/api/ds/query', auth=AUTH, json={
    'queries': [{
        'datasource': {'type': 'grafana-postgresql-datasource', 'uid': 'retail-dw-pg'},
        'rawSql': """SELECT 
    DATE_TRUNC('month', d.full_date)::timestamp AS "time",
    ROUND(SUM(f.net_amount)::numeric, 2) AS "Net Revenue (£)",
    ROUND(SUM(f.return_amount)::numeric, 2) AS "Return Loss (£)"
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY 1
ORDER BY "time" ASC;""",
        'format': 'table'
    }]
})

print('Status:', r.status_code)
if r.status_code == 200:
    frames = r.json().get('results', {}).get('A', {}).get('frames', [])
    for f in frames:
        schema = f.get('schema', {})
        data = f.get('data', {}).get('values', [])
        fields = [field['name'] for field in schema.get('fields', [])]
        print('Fields:', fields)
        rows = list(zip(*data))
        for row in rows:
            ts = datetime.fromtimestamp(row[0]/1000.0) if isinstance(row[0], (int, float)) else row[0]
            print(f"Time: {ts} | Net Revenue: {row[1]} | Return Loss: {row[2]}")
