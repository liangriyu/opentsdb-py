import time

from datetime import datetime
import random

from tsdb.tsdb_client import TsdbClient

if __name__ == "__main__":
    date_format = "%Y-%m-%d %H:%M:%S"
    date_format_d = "%Y-%m-%d"
    client = TsdbClient("hdc-data1")
    #-------------put-------------------
    dps=[]
    ts = time.mktime(datetime.now().timetuple())
    for i in range(0,1):
        dp = {
            "metric": "sys.cpu.nice",
            "timestamp": ts-10000,
            "value": random.randint(1, 20),
            "tags": {
                "host": "hdc1",
                "cpu": "xx"
            }
        }
        dps.append(dp)
        # time.sleep(1)
    # result = client.put(dps,"details")
    #--------------query--------------------
    start = time.mktime(datetime.strptime("2011-11-07 1:00:00",date_format).timetuple())
    end = time.mktime(datetime.strptime("2018-11-07 11:00:00", date_format).timetuple())
    req_params = {'start': start,'end': end, 'queries': [{'metric': 'sys.cpu.nice', 'aggregator': 'none'}]}
    print(req_params)
    result = client.query(req_params)
    print(result)

    #--------------delete---------------------
    # del_tags= {
		# 'host': 'web01',
		# 'dc': 'lga'
    # }
    # # result = client.delete("sys.cpu.nice",start=start,tags=del_tags)
    # result = client.delete("sys.cpu.nice", start=1346840400, end=1541476371)
    # print(result)
    # time.sleep(5)#避免下面请求过快导致查询结果是删除之前的
    # result = client.query(req_params)
    # print(result)

    #-------------suggest----------------------
    result = client.query_suggest("metrics")
    print(result)