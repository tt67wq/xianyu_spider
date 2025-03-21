import requests
import time
import hashlib
import json

token = "7b107aeed10b003b4ae0e437cec0f3bb"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0"

def generate_sign(keywords, pageNumber, timestamp):
    j = timestamp
    h = 34839810  # appKey
    c = {
        "pageNumber": pageNumber,
        "keyword": keywords,
        "fromFilter": "false",
        "rowsPerPage": 30,
        "sortValue": "",
        "sortField": "",
        "customDistance": "",
        "gps": "",
        "propValueStr": {},
        "customGps": "",
        "searchReqFromPage": "pcSearch",
        "extraFilterValue": "{}",
        "userPositionJson": "{}"
    }
    # 使用 JSON 序列化并去除空格
    c_str = json.dumps(c, separators=(',', ':'))
    search_info = f"{token}&{j}&{h}&{c_str}"
    sign = hashlib.md5(search_info.encode()).hexdigest()
    return sign

def generate_url(sign, timestamp):
    url = f"https://h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search/1.0/?jsv=2.7.2&appKey=34839810&t={timestamp}&sign={sign}&v=1.0&type=originaljson&accountSite=xianyu&dataType=json&timeout=20000&api=mtop.taobao.idlemtopsearch.pc.search&sessionOption=AutoLoginOnly&spm_cnt=a21ybx.search.0.0&spm_pre=a21ybx.search.searchHistory.2.19a2127680AbF8&log_id=19a2127680AbF8"
    
    cookies = {
        # "cna": "D1VgIApJGmQBASQJiiCBRM5Q",
        # "mtop_partitioned_detect": "1",
        "_m_h5_tk": "7b107aeed10b003b4ae0e437cec0f3bb_1742309583664",
        "_m_h5_tk_enc": "2cbffcf1c7eb56775eee275d17cb9cc4"
        # "xlly_s": "1",
        # "cookie2": "1ada1ee31e6e0356b15ba3f8323f37f7",
        # "samesite_flag_": "true",
        # "t": "cced748bc744a93eed56ddfe38e7dcc6",
        # "_tb_token_": "e33e6beee78e7",
        # "tfstk": "gsNSgP2KGkFV1xt0rgQql-UmgPcQFk1wRegLSydyJbhJvHUt0uorawfIvum4a0zrwDdQYyPzYWaHO2ULxamFrtzurXcdbGyC_z4u84-b-ildJrhERn4UFhaurXYDuHBaHzxBUuE_vXEKMx3IJXdp9YQfMVmvw2d-JnQj-mhpevdKDn3oPL3LvXQbkm0K9DLu2T02Rm45yuiSHSOKvznX9BF5tYi_qpRp9SuSFyz-cU8zG4MSXxYOjgF_WzFiRWb9dDaUeuu0A1sjM7Z7wxGCOIcz5-ESh8sBGx2YSWHbnG9gSzE7BAFRGaZQDP2iw7IHa02LkWn4wwRIXRziGqVFmQnQHJFrEXxRVqN75WwC4NRZfbSHdEMMOqiNlZ9HKAIky2Cs-9Hoeq02JZ_XQQD-oqGdlZ9HKY3muoQfldoG."
    }
    
    headers = {
        "User-Agent": UA,
        "Referer": "https://www.goofish.com/"
    }
    
    response = requests.get(url, headers=headers, cookies=cookies)
    print(response.json())

if __name__ == "__main__":
    timestamp = int(time.time())
    sign = generate_sign("13mini", 1, timestamp)
    generate_url(sign, timestamp)