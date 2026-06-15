import os
import json
import requests
from google.cloud import bigquery
from datetime import datetime, timedelta

ACCESS_TOKEN = os.environ["META_ACCESS_TOKEN"]
AD_ACCOUNT_ID = os.environ["META_AD_ACCOUNT_ID"]

def fetch_meta_ads():
    yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    url = f"https://graph.facebook.com/v19.0/{AD_ACCOUNT_ID}/insights"
    params = {
        "access_token": ACCESS_TOKEN,
        "time_range": json.dumps({"since": yesterday, "until": yesterday}),
        "fields": "campaign_name,adset_name,ad_name,impressions,clicks,spend,reach,cpc,cpm,ctr",
        "level": "ad",
        "limit": 500,
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if "error" in data:
        raise Exception(f"Meta API 오류 - {data['error']['message']}")
    
    rows = []
    for item in data.get("data", []):
        rows.append({
            "date": yesterday,
            "campaign_name": item.get("campaign_name", ""),
            "adset_name": item.get("adset_name", ""),
            "ad_name": item.get("ad_name", ""),
            "impressions": int(item.get("impressions", 0)),
            "clicks": int(item.get("clicks", 0)),
            "spend": float(item.get("spend", 0)),
            "reach": int(item.get("reach", 0)),
            "cpc": float(item.get("cpc", 0)),
            "cpm": float(item.get("cpm", 0)),
            "ctr": float(item.get("ctr", 0)),
        })
    
    return rows

def upload_to_bigquery(rows):
    client = bigquery.Client()
    table_id = "beautyrella-dashboard.beautyrella_ads.meta_ads"
    
    schema = [
        bigquery.SchemaField("date", "DATE"),
        bigquery.SchemaField("campaign_name", "STRING"),
        bigquery.SchemaField("adset_name", "STRING"),
        bigquery.SchemaField("ad_name", "STRING"),
        bigquery.SchemaField("impressions", "INTEGER"),
        bigquery.SchemaField("clicks", "INTEGER"),
        bigquery.SchemaField("spend", "FLOAT"),
        bigquery.SchemaField("reach", "INTEGER"),
        bigquery.SchemaField("cpc", "FLOAT"),
        bigquery.SchemaField("cpm", "FLOAT"),
        bigquery.SchemaField("ctr", "FLOAT"),
    ]
    
    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition="WRITE_APPEND",
    )
    
    job = client.load_table_from_json(rows, table_id, job_config=job_config)
    job.result()
    print(f"{len(rows)}행 BigQuery 적재 완료")

if __name__ == "__main__":
    rows = fetch_meta_ads()
    if rows:
        upload_to_bigquery(rows)
    else:
        print("데이터 없음")
