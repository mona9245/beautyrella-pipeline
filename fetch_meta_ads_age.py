import os
import json
import requests
from google.cloud import bigquery
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))

ACCESS_TOKEN = os.environ["META_ACCESS_TOKEN"]
AD_ACCOUNT_ID = os.environ["META_AD_ACCOUNT_ID"]

BACKFILL_MODE = os.environ.get("BACKFILL_MODE", "false").lower() == "true"
BACKFILL_START = os.environ.get("BACKFILL_START", "2026-08-01")
BACKFILL_END = os.environ.get("BACKFILL_END", "2026-08-31")
ROLLING_DAYS = int(os.environ.get("ROLLING_DAYS", "7"))

def fetch_meta_ads_age(since, until):
    url = f"https://graph.facebook.com/v19.0/{AD_ACCOUNT_ID}/insights"
    params = {
        "access_token": ACCESS_TOKEN,
        "time_range": json.dumps({"since": since, "until": until}),
        "fields": "impressions,clicks,spend,actions",
        "breakdowns": "age",
        "level": "account",
        "limit": 500,
    }
    response = requests.get(url, params=params)
    data = response.json()
    print(f"API 응답 - {json.dumps(data, ensure_ascii=False)[:500]}")
    if "error" in data:
        raise Exception(f"Meta API 오류 - {data['error']['message']}")
    rows = []
    for item in data.get("data", []):
        rows.append({
            "date": since,
            "age_range": item.get("age", "Unknown"),
            "impressions": int(item.get("impressions", 0)),
            "clicks": int(item.get("clicks", 0)),
            "spend": float(item.get("spend", 0)),
            "installs": int(next((a["value"] for a in item.get("actions", []) if a["action_type"] == "mobile_app_install"), 0)),
        })
    return rows

def delete_existing_date(date_str):
    client = bigquery.Client()
    table_id = "beautyrella-dashboard.beautyrella_ads.meta_ads_age"
    query = f"DELETE FROM `{table_id}` WHERE date = @date"
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("date", "DATE", date_str)]
    )
    client.query(query, job_config=job_config).result()

def upload_to_bigquery(rows):
    client = bigquery.Client()
    table_id = "beautyrella-dashboard.beautyrella_ads.meta_ads_age"
    schema = [
        bigquery.SchemaField("date", "DATE"),
        bigquery.SchemaField("age_range", "STRING"),
        bigquery.SchemaField("spend", "FLOAT"),
        bigquery.SchemaField("installs", "INTEGER"),
        bigquery.SchemaField("clicks", "INTEGER"),
        bigquery.SchemaField("impressions", "INTEGER"),
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
        start = datetime.strptime(BACKFILL_START, "%Y-%m-%d")
        end = datetime.strptime(BACKFILL_END, "%Y-%m-%d")
        current = start
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            print(f"{date_str} 데이터 가져오는 중...")
            try:
                rows = fetch_meta_ads_age(date_str, date_str)
            except Exception as e:
                print(f"{date_str} - 가져오기 실패, 다음 날짜로 진행: {e}")
                current += timedelta(days=1)
                continue
            delete_existing_date(date_str)
            if rows:
                upload_to_bigquery(rows)
            else:
                print(f"{date_str} - 데이터 없음")
            current += timedelta(days=1)
    else:
        # 최근 N일치를 매번 삭제 후 재수집 — 메타의 소급 설치 반영(최대 7일)을 따라잡기 위함
        today_kst = datetime.now(KST)
        for i in range(1, ROLLING_DAYS + 1):
            date_str = (today_kst - timedelta(days=i)).strftime("%Y-%m-%d")
            print(f"{date_str} 데이터 갱신 중...")
            try:
                rows = fetch_meta_ads_age(date_str, date_str)
            except Exception as e:
                print(f"{date_str} - 가져오기 실패, 다음 날짜로 진행: {e}")
                continue
            delete_existing_date(date_str)
            if rows:
                upload_to_bigquery(rows)
            else:
                print(f"{date_str} - 데이터 없음")
