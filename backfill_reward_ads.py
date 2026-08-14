from google.cloud import bigquery

# 2026-08-14 사용자 제공 엑셀(뷰티렐라 CPI 캠페인_Daily report_20260810.xlsx, '버즈빌' 탭)에서
# 수기로 옮긴 리워드 광고(버즈빌) 일별/OS별 데이터. 8/1~8/9 (캠페인 시작일부터 리포트 생성일 전날까지).
# 버즈빌은 CPI 고정단가(250원) 네트워크라 impressions 데이터가 없음 -> impressions/cpm/ctr은 0으로 적재.
AOS_CAMPAIGN = "버즈빌 CPI_AOS"
IOS_CAMPAIGN = "버즈빌 CPI_iOS"

# (date, clicks, installs, spend)
AOS_ROWS = [
    ("2026-08-01", 488, 311, 77750),
    ("2026-08-02", 472, 311, 77750),
    ("2026-08-03", 458, 311, 77750),
    ("2026-08-04", 448, 312, 78000),
    ("2026-08-05", 462, 312, 78000),
    ("2026-08-06", 261, 172, 43000),
    ("2026-08-07", 275, 173, 43250),
    ("2026-08-08", 249, 173, 43250),
    ("2026-08-09", 266, 172, 43000),
]

IOS_ROWS = [
    ("2026-08-01", 171, 78, 19500),
    ("2026-08-02", 149, 57, 14250),
    ("2026-08-03", 117, 78, 19500),
    ("2026-08-04", 99, 79, 19750),
    ("2026-08-05", 117, 78, 19500),
    ("2026-08-06", 277, 218, 54500),
    ("2026-08-07", 267, 219, 54750),
    ("2026-08-08", 281, 217, 54250),
    ("2026-08-09", 278, 217, 54250),
]


def delete_existing_range(client, table_id, start_date, end_date):
    query = f"DELETE FROM `{table_id}` WHERE date BETWEEN @start AND @end"
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("start", "DATE", start_date),
            bigquery.ScalarQueryParameter("end", "DATE", end_date),
        ]
    )
    client.query(query, job_config=job_config).result()


def upload_to_bigquery(client, table_id, rows):
    schema = [
        bigquery.SchemaField("date", "DATE"),
        bigquery.SchemaField("campaign_name", "STRING"),
        bigquery.SchemaField("impressions", "INTEGER"),
        bigquery.SchemaField("clicks", "INTEGER"),
        bigquery.SchemaField("spend", "FLOAT"),
        bigquery.SchemaField("cpc", "FLOAT"),
        bigquery.SchemaField("cpm", "FLOAT"),
        bigquery.SchemaField("ctr", "FLOAT"),
        bigquery.SchemaField("installs", "INTEGER"),
    ]
    job_config = bigquery.LoadJobConfig(schema=schema, write_disposition="WRITE_APPEND")
    job = client.load_table_from_json(rows, table_id, job_config=job_config)
    job.result()
    print(f"{len(rows)}행 BigQuery 적재 완료")


if __name__ == "__main__":
    client = bigquery.Client()
    table_id = "beautyrella-dashboard.beautyrella_ads.reward_ads"

    print("기존 8/1~8/9 범위 삭제 중 (중복 방지)...")
    try:
        delete_existing_range(client, table_id, "2026-08-01", "2026-08-09")
    except Exception as e:
        print(f"삭제 중 오류 (테이블이 아직 없으면 정상): {e}")

    def build_rows(rows, campaign_name):
        out = []
        for date_str, clicks, installs, spend in rows:
            out.append({
                "date": date_str,
                "campaign_name": campaign_name,
                "impressions": 0,
                "clicks": clicks,
                "spend": float(spend),
                "cpc": round(spend / clicks, 2) if clicks else 0.0,
                "cpm": 0.0,
                "ctr": 0.0,
                "installs": installs,
            })
        return out

    payload = build_rows(AOS_ROWS, AOS_CAMPAIGN) + build_rows(IOS_ROWS, IOS_CAMPAIGN)
    upload_to_bigquery(client, table_id, payload)
