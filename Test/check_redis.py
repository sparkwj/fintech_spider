#!/usr/bin/env python3
# coding: utf-8
# File: check_redis.py
# Author: lxw
# Date: 5/31/17 9:41 PM

import redis


class CheckRedis:
    REDIS_HOST = "192.168.1.29"
    # REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    REDIS_KEY_DOC_ID = "DOC_ID_HASH"
    REDIS_KEY_TASKS = "TASKS_HASH"
    REDIS_KEY_CNKI = "CNKI_PATENT"
    pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)
    REDIS_URI = redis.Redis(connection_pool=pool)

    def check_doc_id_redis(self):
        success_count = 0
        timeout_count = 0
        zero_count = 0
        for item in self.REDIS_URI.hscan_iter(self.REDIS_KEY_DOC_ID):
            # print(type(item), item)   # <class 'tuple'> (b'65d07ad1-09f1-45d6-8c9f-6fe379e146f1', b'0')
            doc_id = item[0].decode("utf-8")
            flag_code_timestamp = int(item[1].decode("utf-8"))
            if flag_code_timestamp == -1:
                success_count += 1
            elif flag_code_timestamp == 0:
                zero_count += 1
            else:    # flag_code_timestamp > 0  -> timestamp
                timeout_count += 1
                print(doc_id, flag_code_timestamp)
        print("success_count: {0}, zero_count: {1}, timeout_count: {2}".format(success_count, zero_count, timeout_count))

    def check_tasks_redis(self):
        success_count = 0
        success_1_count = 0
        success_2_count = 0
        success_3_count = 0
        timeout_count = 0
        zero_count = 0
        for item in self.REDIS_URI.hscan_iter(self.REDIS_KEY_TASKS):
            # print(type(item), item)    # <class 'tuple'> (b'{"Param": "\\u5f53\\u4e8b\\u4eba:\\u4e2d\\u56fd\\u77f3\\u6cb9\\u5316\\u5de5\\u80a1\\u4efd\\u6709\\u9650\\u516c\\u53f8", "Index": "12", "case_parties": "600028", "abbr_full_category": "full"}', b'-1_0'
            task = item[0].decode("utf-8")
            left_right = item[1].decode("utf-8")
            left_right = left_right.split("_")
            left = int(left_right[0])
            right = int(left_right[1])
            if left == 0:
                zero_count += 1
            elif left < 0:
                success_count += 1
                if left == -1:
                    success_1_count += 1
                elif left == -2:
                    success_2_count += 1
                elif left == -3:
                    success_3_count += 1
            else:
                timeout_count += 1
                print("retry {0} times. last time to crawl: {1}".format(left, right))
        print("success_count: {0}, zero_count: {1}, timeout_count: {2}".format(success_count, zero_count, timeout_count))
        print("success_1_count: {0}, success_2_count: {1}, success_3_count: {2}".format(success_1_count, success_2_count, success_3_count))

    def check_cnki_redis(self):
        success_count = 0
        zero_count = 0
        error_count = 0
        for item in self.REDIS_URI.hscan_iter(self.REDIS_KEY_CNKI):
            # print(type(item), item)   # <class 'tuple'> (b'600469||\xe9\xa3\x8e\xe7\xa5\x9e\xe8\xbd\xae\xe8\x83\x8e\xe8\x82\xa1\xe4\xbb\xbd\xe6\x9c\x89\xe9\x99\x90\xe5\x85\xac\xe5\x8f\xb8||-/kns/detail/detail.aspx?QueryID=0&CurRec=387&dbcode=scpd&dbname=SCPD0407&filename=CN3639826||full', b'-1')
            url = item[0].decode("utf-8")
            flag_code = int(item[1].decode("utf-8"))
            if flag_code == -1:
                success_count += 1
            elif flag_code == 0:
                zero_count += 1
            else:    # flag_code == -2  -> error
                error_count += 1
                print("[error] url:", url)
        print("success_count: {0}, zero_count: {1}, error_count: {2}".format(success_count, zero_count, error_count))
        # 20170614 success_count: 110402, zero_count: 8613, error_count: 0


if __name__ == "__main__":
    cr = CheckRedis()
    # cr.check_doc_id_redis()
    # cr.check_tasks_redis()
    cr.check_cnki_redis()

