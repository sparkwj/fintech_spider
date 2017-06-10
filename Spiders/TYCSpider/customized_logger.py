#!/usr/bin/env python3
# coding: utf-8
# File: customized_logger.py
# Author: lxw
# Date: 6/9/17 10:52 PM

import logging.config


def get_logger(logger_name):
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'verbose': {
                'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                'datefmt': "%Y-%m-%d %H:%M:%S"
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
            "output": {
                "format": "%(message)s"
            }
        },
        'handlers': {
            'null': {
                'level': 'DEBUG',
                'class': 'logging.NullHandler',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            },
            'file': {
                'level': 'DEBUG',
                # 如果没有使用并发的日志处理类，在多实例的情况下日志会出现缺失
                'class': 'cloghandler.ConcurrentRotatingFileHandler',
                # 当达到10MB时分割日志
                'maxBytes': 1024 * 1024 * 10,
                # 最多保留50份文件
                'backupCount': 50,
                # If delay is true, then file opening is deferred until the first call to emit().
                'delay': True,
                'filename': logger_name+".md",
                'formatter': 'output'
            }
        },
        'loggers': {
            '': {
                'handlers': ['file'],
                'level': 'DEBUG',
            },
        }
    })
    return logging.getLogger(logger_name)
