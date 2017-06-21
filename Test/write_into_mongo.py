#!/usr/bin/env python3
# coding: utf-8
# File: write_into_mongo.py
# Author: lxw
# Date: 6/21/17 9:45 AM

import pymongo

class WriteIntoMongoTest:

    def into_mongo(self, db, data_dict):
        print(data_dict)
        print(len(data_dict))    # Not 2, but 3.
        db["test_write"].insert(data_dict)
        print(data_dict)    # NOTE: the key "_id" is added into data_dict automatically here.
        print(len(data_dict))    # Not 2, but 3.

    def write_into_mongo(self):
        # pymongo.errors.DuplicateKeyError: E11000 duplicate key error collection: scrapy.test_write index: _id_ dup key: { : ObjectId('5949e2812759391e00ab43df')
        conn = pymongo.MongoClient("192.168.1.41", 27017)
        db = conn.scrapy    # dbname: scrapy
        result_dict = {}
        for i in range(10):
            result_dict["key1"] = "abstract"
            result_dict["key2"] = str(i)
            self.into_mongo(db, result_dict)

        """
        # OK: method 1.
        conn = pymongo.MongoClient("192.168.1.41", 27017)
        db = conn.scrapy    # dbname: scrapy
        for i in range(10):
            result_dict = {}
            result_dict["key1"] = "abstract"
            result_dict["key2"] = str(i)
            self.into_mongo(db, result_dict)

        # OK: method 2.
        conn = pymongo.MongoClient("192.168.1.41", 27017)
        db = conn.scrapy    # dbname: scrapy
        result_dict = {}
        for i in range(10):
            if "_id" in result_dict:
                print("_id in result_dict")
                del result_dict["_id"]
            result_dict["key1"] = "abstract"
            result_dict["key2"] = str(i)
            self.into_mongo(db, result_dict)
        """

if __name__ == "__main__":
    twim = WriteIntoMongoTest()
    twim.write_into_mongo()

