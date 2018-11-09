#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
import json
import string

import requests

__author__ = 'liangriyu'


class TsdbClient(object):
    """
    时序数据库客户端工具类
    """

    _valid_metric_chars = set(string.ascii_letters + string.digits + '-_./')

    def __init__(self, host, port=4242):
        self.host = host
        self.port = int(port)



    def put(self, datapoints, query_string='summary', sync_timeout=60000):
        """
        写入数据
        :param datapoints: 数据点 json 或 jsonArray
        :param query_string: eg summary,details,sync
        :param sync_timeout: query_string为sync时生效
        :return:
        """
        self._check_points(datapoints)
        if query_string == 'sync':
            query_string = str(query_string).join(["&",str(sync_timeout)])
        put_url = "http://" + self.host + ":" + str(self.port) + "/api/put?" + query_string
        result = requests.post(put_url, json=datapoints)
        return result.text;

    def query(self,req_params):
        """
        查询数据点
        参考实例：http://opentsdb.net/docs/build/html/user_guide/query/examples.html
        :param req_params: 请求参数体
        :return: jsonArray eg:if empty return [] else return ["metric": "","tags": {},"aggregatedTags": [],"dps": [],...]
        """
        return self._do_requests(req_params)

    def delete(self, metric, start, end=None, tags=None):
        """
        删除数据
        :param metric: 待删除metric
        :param start: 开始时间戳（必须）
        :param end: 结束时间戳（可选）
        :param tags: 过滤标签（可选,类型Map）
        :return:
        """
        req_params = {'start': start, 'queries': [{'metric': metric, 'aggregator': 'none'}], 'delete': 'true'}
        if end:
            req_params["end"]=end
        if tags:
            req_params["queries"][0]['tags'] = tags
        return self._do_requests(req_params)

    def query_suggest(self, type, q=None, max=25):
        """
        查询 Metric,Tagk,Tagv
        :param type:需要查询的类型，metrics，tagk，tagv
        :param q:前缀过滤
        :param max:最大返回个数
        :return: 查询到的字符串数组
        """
        req_params = {
            "type": type,
            "max": max
        }
        if q:
            req_params["q"] = str(q)
        return self._do_requests(req_params,"suggest")

    def _check_points(self, datapoints):
        """
        校验datapoints
        :param datapoints: 数据点 json 或 jsonArray
        :return:
        """
        if isinstance(datapoints, str):
            datapoints = json.load(datapoints)
        if isinstance(datapoints, list):
            for datapoint in datapoints:
                assert all(c in self._valid_metric_chars for c in datapoint["metric"]), "invalid metric error for " + str(datapoint)
                assert datapoint["tags"] != {}, "Need at least one tag"+str(datapoint)
        else:
            assert all(c in self._valid_metric_chars for c in datapoints["metric"]), "invalid metric error for " + str(
                datapoints)
            assert datapoints["tags"] != {}, "Need at least one tag"+str(datapoints)

    def _do_requests(self,req_params,option='query'):
        """
        查询请求
        :param req_params: 请求参数体
        :param option: 操作选项 如 query,suggest等
        :return:
        """
        if isinstance(req_params, str):
            req_params=json.loads(req_params)
        if "start" in req_params:
            req_params["start"] = int(req_params["start"])
        if "end" in req_params:
            req_params["end"] = int(req_params["end"])
        url = "http://" + self.host + ":" + str(self.port) + "/api/" + option
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        result = requests.post(url, json=req_params, headers=headers)
        rs = json.loads(result.text)
        return rs



