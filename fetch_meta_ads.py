import os
import json
import requests
from google.cloud import bigquery
from datetime import datetime, timedelta

ACCESS_TOKEN = os.environ["META_ACCESS_TOKEN"]
AD_ACCOUNT_ID = os.environ["META_AD_ACCOUNT_ID"]

# 과거 데이터 적재 시 아래 두 값 수정, 평소엔 yesterday 모드로 자동 실행
BACKFILL_MODE = os.environ.get("BACKFILL_MODE", "false").lower() == "true"
BACKFILL_START = os.environ.get("BACKFILL_START", "2025-02-23")
BACKFILL_END = os.environ.get("BACKFILL_END", "2025-05-31")

def fetch_meta_ads(since, until):
    url = f"https://graph.facebook.com/v19.0/{AD_ACCOUNT_ID}/insights"
    params = {
        "access_token": ACCESS_TOKEN,
        "time_range": json.dumps({"since": since, "until": until}),
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
            "date": since,
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
    if BACKFILL_MODE:
        # 과거 데이터 날짜별 적재
        start = datetime.strptime(BACKFILL_START, "%Y-%m-%d")
        end = datetime.strptime(BACKFILL_END, "%Y-%m-%d")
        current = start
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            print(f"{date_str} 데이터 가져오는 중...")
            rows = fetch_meta_ads(date_str, date_str)
            if rows:
                upload_to_bigquery(rows)
            else:
                print(f"{date_str} - 데이터 없음")
            current += timedelta(days=1)
    else:
        # 평소 자동 실행 - 어제 데이터
        yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        rows = fetch_meta_ads(yesterday, yesterday)
        if rows:
            upload_to_bigquery(rows)
        else:
            print("데이터 없음")
