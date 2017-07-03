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
                # print(doc_id, flag_code_timestamp)
        print("\n\nsuccess_count: {0}, zero_count: {1}, timeout_count: {2}, total: {3}".format(success_count, zero_count, timeout_count, success_count+zero_count+timeout_count))
        # 20170630_0855 success_count: 217798, zero_count: 906276, timeout_count: 111403, total: 1235477
        # 20170703_1500 success_count: 232367, zero_count: 1001587, timeout_count: 105284, total: 133923


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
                # print("retry {0} times. last time to crawl: {1}".format(left, right))
        print("\n\nsuccess_count: {0}, zero_count: {1}, timeout_count: {2}".format(success_count, zero_count, timeout_count))
        print("success_1_count: {0}, success_2_count: {1}, success_3_count: {2}".format(success_1_count, success_2_count, success_3_count))
        print("total:{}".format(zero_count+success_count+timeout_count))
        # 20170630_0855
        # success_count: 68184, zero_count: 22265, timeout_count: 3863
        # success_1_count: 64718, success_2_count: 3016, success_3_count: 450
        # total:94312
        # 20170703_1500
        # success_count: 75240, zero_count: 22419, timeout_count: 2120
        # success_1_count: 71592, success_2_count: 3179, success_3_count: 469
        # total:99779

    def check_cnki_redis(self):
        success_count = 0
        zero_count = 0
        error_count = 0
        for item in self.REDIS_URI.hscan_iter(self.REDIS_KEY_CNKI):
            # print(type(item), item)   # <class 'tuple'> (b'600469||\xe9\xa3\x8e\xe7\xa5\x9e\xe8\xbd\xae\xe8\x83\x8e\xe8\x82\xa1\xe4\xbb\xbd\xe6\x9c\x89\xe9\x99\x90\xe5\x85\xac\xe5\x8f\xb8||-/kns/detail/detail.aspx?QueryID=0&CurRec=387&dbcode=scpd&dbname=SCPD0407&filename=CN3639826||full', b'-1')
            # print(type(item), item)   # <class 'tuple'> (b'600469||\xe9\xa3\x8e\xe7\xa5\x9e\xe8\xbd\xae\xe8\x83\x8e\xe8\x82\xa1\xe4\xbb\xbd\xe6\x9c\x89\xe9\x99\x90\xe5\x85\xac\xe5\x8f\xb8||-/kns/detail/detail.aspx?QueryID=0&CurRec=387&dbcode=scpd&dbname=SCPD0407&filename=CN3639826||full', b'-1')
            if item[0].decode("utf-8").startswith("900951"):
                print(item)
                # print(item[0].decode("utf-8").split("||")[1])
                # self.REDIS_URI.hset(self.REDIS_KEY_CNKI, item[0], 0)  # 601398
            url = item[0].decode("utf-8")
            flag_code = int(item[1].decode("utf-8"))
            if flag_code == -1:
                success_count += 1
            elif flag_code == 0:
                zero_count += 1
            else:    # flag_code == -2  -> error
                error_count += 1
                print("[error] url:", url)
        print("\n\nsuccess_count: {0}, zero_count: {1}, error_count: {2}".format(success_count, zero_count, error_count))
        # 20170629_1107 success_count: 148536, zero_count: 3237, error_count: 0
        # 20170630_0855 success_count: 151823, zero_count: 0, error_count: 0

    def add_new_into_cnki_redis(self):
        code = 601398
        name = "中国工商银行"
        redis_field_str = "{0}||{1}||+||abbr".format(code, name)
        self.REDIS_URI.hset(self.REDIS_KEY_CNKI, redis_field_str, 0)

        name = "中国工商银行股份有限公司"
        redis_field_str = "{0}||{1}||+||abbr".format(code, name)
        self.REDIS_URI.hset(self.REDIS_KEY_CNKI, redis_field_str, 0)

    def check_tasks(self):
        with open("./result.md", "w") as f:
            for item in self.REDIS_URI.hscan_iter(self.REDIS_KEY_TASKS):
                # print(type(item), item)    # <class 'tuple'> (b'{"Param": "\\u5f53\\u4e8b\\u4eba:\\u4e2d\\u56fd\\u77f3\\u6cb9\\u5316\\u5de5\\u80a1\\u4efd\\u6709\\u9650\\u516c\\u53f8", "Index": "12", "case_parties": "600028", "abbr_full_category": "full"}', b'-1_0'
                task = item[0].decode("utf-8")
                left_right = item[1].decode("utf-8")
                if left_right == "0_0":
                    f.write("{0}\t{1}\n".format(task, left_right))
                if '{"Param": "\u5f53\u4e8b\u4eba:\u592a\u5e73\u6d0b,\u6848\u4ef6\u7c7b\u578b:\u6c11\u4e8b\u6848\u4ef6,\u6cd5\u9662\u5c42\u7ea7:\u57fa\u5c42\u6cd5\u9662,\u88c1\u5224\u65e5\u671f:2014-12-30 TO 2014-12-30", "Index": "2", "case_parties": "601099", "abbr_full_category": "abbr_single"}' in task:
                    print(task, left_right)


if __name__ == "__main__":
    cr = CheckRedis()
    cr.check_doc_id_redis()
    cr.check_tasks_redis()
    # cr.add_new_into_cnki_redis()
    cr.check_cnki_redis()
    # cr.check_tasks()

