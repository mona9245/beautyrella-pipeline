from google.cloud import bigquery

# 2026-08-14 Google Ads 콘솔(ads.google.com)에서 수기로 긁은 데이터 (7/31~8/14)
# Developer Token 승인 전까지 임시 수동 백필. 설치수는 Google Ads 자체 집계로
# AppsFlyer 수치와 불일치 확인됨 - 별도 확인 필요, 참고용으로만 사용할 것.
ROWS = [
    # (date, campaign_name, impressions, clicks, spend, installs)
    ("2026-07-31", "26년 7월_뷰티렐라_[AOS]앱다운유도_앱설치_단일이미지_AOS_논타겟", 67, 0, 0, 0),
    ("2026-08-01", "26년 7월_뷰티렐라_[AOS]앱다운유도_앱설치_단일이미지_AOS_논타겟", 2014, 172, 48113, 48),
    ("2026-08-02", "26년 7월_뷰티렐라_[AOS]앱다운유도_앱설치_단일이미지_AOS_논타겟", 2670, 166, 46284, 57),
    ("2026-08-03", "26년 7월_뷰티렐라_[AOS]앱다운유도_앱설치_단일이미지_AOS_논타겟", 3110, 165, 40676, 43),
    ("2026-08-04", "26년 7월_뷰티렐라_[AOS]앱다운유도_앱설치_단일이미지_AOS_논타겟", 5194, 276, 47704, 60),
    ("2026-08-05", "26년 7월_뷰티렐라_[AOS]앱다운유도_앱설치_단일이미지_AOS_논타겟", 7009, 368, 46637, 48),
    ("2026-08-06", "26년 7월_뷰티렐라_[AOS]앱다운유도_앱설치_단일이미지_AOS_논타겟", 4799, 309, 51315, 23),
    ("2026-08-07", "26년 7월_뷰티렐라_[AOS]앱다운유도_앱설치_단일이미지_AOS_논타겟", 7285, 330, 55178, 40),
    ("2026-08-08", "26년 7월_뷰티렐라_[AOS]앱다운유도_앱설치_단일이미지_AOS_논타겟", 10367, 525, 64870, 41),
    ("2026-08-09", "26년 7월_뷰티렐라_[AOS]앱다운유도_앱설치_단일이미지_AOS_논타겟", 12326, 648, 69853, 62),
    ("2026-08-10", "26년 7월_뷰티렐라_[AOS]앱다운유도_앱설치_단일이미지_AOS_논타겟", 8393, 450, 66984, 42),
    ("2026-08-11", "26년 7월_뷰티렐라_[AOS]앱다운유도_앱설치_단일이미지_AOS_논타겟", 7754, 326, 78808, 72),
    ("2026-08-12", "26년 7월_뷰티렐라_[AOS]앱다운유도_앱설치_단일이미지_AOS_논타겟", 15798, 321, 102225, 135),
    ("2026-08-13", "26년 7월_뷰티렐라_[AOS]앱다운유도_앱설치_단일이미지_AOS_논타겟", 18316, 325, 103913, 137),
    ("2026-08-14", "26년 7월_뷰티렐라_[AOS]앱다운유도_앱설치_단일이미지_AOS_논타겟", 25116, 360, 104214, 149),

    ("2026-07-31", "26년 7월_뷰티렐라_[iOS]앱다운유도_앱설치_단일이미지_iOS_논타켓", 1018, 7, 997, 0),
    ("2026-08-01", "26년 7월_뷰티렐라_[iOS]앱다운유도_앱설치_단일이미지_iOS_논타켓", 11672, 103, 25126, 0),
    ("2026-08-02", "26년 7월_뷰티렐라_[iOS]앱다운유도_앱설치_단일이미지_iOS_논타켓", 20182, 171, 36508, 0),
    ("2026-08-03", "26년 7월_뷰티렐라_[iOS]앱다운유도_앱설치_단일이미지_iOS_논타켓", 17299, 96, 14761, 0),
    ("2026-08-04", "26년 7월_뷰티렐라_[iOS]앱다운유도_앱설치_단일이미지_iOS_논타켓", 0, 0, 0, 0),
    ("2026-08-05", "26년 7월_뷰티렐라_[iOS]앱다운유도_앱설치_단일이미지_iOS_논타켓", 283, 5, 365, 0),
    ("2026-08-06", "26년 7월_뷰티렐라_[iOS]앱다운유도_앱설치_단일이미지_iOS_논타켓", 10835, 148, 53822, 0),
    ("2026-08-07", "26년 7월_뷰티렐라_[iOS]앱다운유도_앱설치_단일이미지_iOS_논타켓", 5594, 83, 35722, 0),
    ("2026-08-08", "26년 7월_뷰티렐라_[iOS]앱다운유도_앱설치_단일이미지_iOS_논타켓", 7877, 131, 44265, 0),
    ("2026-08-09", "26년 7월_뷰티렐라_[iOS]앱다운유도_앱설치_단일이미지_iOS_논타켓", 8836, 114, 37885, 0),
    ("2026-08-10", "26년 7월_뷰티렐라_[iOS]앱다운유도_앱설치_단일이미지_iOS_논타켓", 2586, 34, 11939, 0),
    ("2026-08-11", "26년 7월_뷰티렐라_[iOS]앱다운유도_앱설치_단일이미지_iOS_논타켓", 0, 0, 0, 0),
    ("2026-08-12", "26년 7월_뷰티렐라_[iOS]앱다운유도_앱설치_단일이미지_iOS_논타켓", 0, 0, 0, 0),
    ("2026-08-13", "26년 7월_뷰티렐라_[iOS]앱다운유도_앱설치_단일이미지_iOS_논타켓", 0, 0, 0, 0),
    ("2026-08-14", "26년 7월_뷰티렐라_[iOS]앱다운유도_앱설치_단일이미지_iOS_논타켓", 3013, 30, 15617, 0),
]


def delete_existing_range(start_date, end_date):
    client = bigquery.Client()
    table_id = "beautyrella-dashboard.beautyrella_ads.google_ads"
    query = f"DELETE FROM `{table_id}` WHERE date BETWEEN @start AND @end"
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("start", "DATE", start_date),
            bigquery.ScalarQueryParameter("end", "DATE", end_date),
        ]
    )
    client.query(query, job_config=job_config).result()


def upload_to_bigquery(rows):
    client = bigquery.Client()
    table_id = "beautyrella-dashboard.beautyrella_ads.google_ads"
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
    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition="WRITE_APPEND",
    )
    job = client.load_table_from_json(rows, table_id, job_config=job_config)
    job.result()
    print(f"{len(rows)}행 BigQuery 적재 완료")


if __name__ == "__main__":
    print("기존 7/31~8/14 범위 삭제 중 (중복 방지)...")
    try:
        delete_existing_range("2026-07-31", "2026-08-14")
    except Exception as e:
        print(f"삭제 중 오류 (테이블이 아직 없으면 정상): {e}")

    payload = []
    for date_str, campaign_name, impressions, clicks, spend, installs in ROWS:
        cpc = round(spend / clicks, 2) if clicks else 0.0
        cpm = round(spend / impressions * 1000, 2) if impressions else 0.0
        ctr = round(clicks / impressions * 100, 2) if impressions else 0.0
        payload.append({
            "date": date_str,
            "campaign_name": campaign_name,
            "impressions": impressions,
            "clicks": clicks,
            "spend": float(spend),
            "cpc": cpc,
            "cpm": cpm,
            "ctr": ctr,
            "installs": installs,
        })

    upload_to_bigquery(payload)
