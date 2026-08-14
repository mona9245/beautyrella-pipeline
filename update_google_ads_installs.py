from google.cloud import bigquery

# 2026-08-14 AppsFlyer(hq1.appsflyer.com, googleadwords_int 미디어소스, Android 앱만 -
# iOS는 해당 채널 설치 0건 확인)에서 확인한 실제 설치수로 google_ads.installs 갱신.
# 구글애즈 자체 집계(957) 대비 앱스플라이어 실측(845)이 더 낮게 나와 (약 12% 과다집계),
# 대시보드 표기 기준을 앱스플라이어로 통일하기 위함.
AOS_CAMPAIGN = "26년 7월_뷰티렐라_[AOS]앱다운유도_앱설치_단일이미지_AOS_논타겟"
IOS_CAMPAIGN = "26년 7월_뷰티렐라_[iOS]앱다운유도_앱설치_단일이미지_iOS_논타켓"

AOS_INSTALLS = {
    "2026-07-31": 0,
    "2026-08-01": 14,
    "2026-08-02": 9,
    "2026-08-03": 19,
    "2026-08-04": 21,
    "2026-08-05": 36,
    "2026-08-06": 33,
    "2026-08-07": 64,
    "2026-08-08": 44,
    "2026-08-09": 66,
    "2026-08-10": 45,
    "2026-08-11": 64,
    "2026-08-12": 124,
    "2026-08-13": 140,
    "2026-08-14": 166,
}

# iOS는 앱스플라이어 기준 googleadwords_int 채널 설치 0건 (전체 기간)
IOS_INSTALLS = {date_str: 0 for date_str in AOS_INSTALLS}


def update_installs(client, table_id, date_str, campaign_name, installs):
    query = f"""
        UPDATE `{table_id}`
        SET installs = @installs
        WHERE date = @date AND campaign_name = @campaign_name
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("installs", "INT64", installs),
            bigquery.ScalarQueryParameter("date", "DATE", date_str),
            bigquery.ScalarQueryParameter("campaign_name", "STRING", campaign_name),
        ]
    )
    client.query(query, job_config=job_config).result()


if __name__ == "__main__":
    client = bigquery.Client()
    table_id = "beautyrella-dashboard.beautyrella_ads.google_ads"

    for date_str, installs in AOS_INSTALLS.items():
        update_installs(client, table_id, date_str, AOS_CAMPAIGN, installs)
        print(f"{date_str} AOS installs -> {installs}")

    for date_str, installs in IOS_INSTALLS.items():
        update_installs(client, table_id, date_str, IOS_CAMPAIGN, installs)
        print(f"{date_str} iOS installs -> {installs}")

    print("앱스플라이어 기준 installs 업데이트 완료")
