#!/usr/bin/env python
import base64
import os
import json
import pprint
import traceback

import tornado.gen
import tornado.httpserver
import tornado.ioloop
import tornado.web

from settings import Settings

from tornado.options import define, options, parse_command_line
from tornado.httpclient import HTTPError, AsyncHTTPClient, HTTPRequest

#from uuid import uuid4

define("debug", default=False, help="run in debug mode")
pp = pprint.PrettyPrinter(indent=4)


class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        try:
            print("MainHandler GET")
            self.render("index.html")
        except Exception as e:
            traceback.print_exc()


class CommandHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        print("CommandHandler request.body:{0}".format(self.request.body))
        jbody = json.loads(self.request.body)
        command = jbody.get('command')
        result_object = {"reason":None, "code":200, "data":None}
        if command not in ['get_mockapi_url', 'put_mockapi_url']:
            result_object['reason'] = "{0} command not recognized.".format(command)
            result_object['code'] = 400
        else:
            mockapi_url = jbody.get('url')
            if command == "get_mockapi_url":
                success, data = yield self.get_mockapi_url(mockapi_url)
            elif command == "put_mockapi_url":
                input_data = jbody.get('data')
                success, data = yield self.put_mockapi_url(mockapi_url, input_data)
            if not success:
                result_object['code'] = 400
                result_object['reason'] = data
            else:
                result_object["data"] = data
        res_val = json.dumps(result_object)
        print(res_val)
        self.write(res_val)

    @tornado.gen.coroutine
    def simple_request(self, url, data=None, method="GET"):
        headers={"Content-Type":"application/json"}
        request = HTTPRequest(url, method=method, headers=headers, body=data, request_timeout=40)
        http_client = AsyncHTTPClient()
        response = yield http_client.fetch(request)
        raise tornado.gen.Return(response)
        #return HTTPRequest(url, method=method, headers=headers, request_timeout=40, allow_nonstandard_methods=allow_nonstandard_methods)

    @tornado.gen.coroutine
    def get_mockapi_url(self, url):
        success = False
        data = None
        try:
            response = yield self.simple_request(url)
            print(response)
            print(response.body)
            data = json.loads(response.body)
            success = True
        except Exception as e:
            traceback.print_exc()
            data = "There was an error retrieving the JSON data. Please confirm your mockapi url is correct."
        raise tornado.gen.Return((success, data))

    @tornado.gen.coroutine
    def put_mockapi_url(self, url, input_data):
        success = False
        data = "JSON data should include an 'id' key."
        try:
            print(url)
            print(input_data)
            if input_data["id"]:
                input_data_str = json.dumps(input_data)
                url += "/" + input_data["id"]
                response = yield self.simple_request(url, input_data_str, "PUT")
                print(response)
                print(response.body)
                success = True
                data = "JSON data successfully updated."
        except Exception as e:
            traceback.print_exc()
            data = "There was an error submitting the JSON data."
        raise tornado.gen.Return((success, data))


@tornado.gen.coroutine
def main():
    try:
        parse_command_line()
        app = tornado.web.Application([
                (r"/", MainHandler),
                (r"/command", CommandHandler),
              ],
            template_path=os.path.join(os.path.dirname(__file__), "html_templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            cookie_secret=Settings.cookie_secret,
            xsrf_cookies=False,
            debug=options.debug,
            )
        server = tornado.httpserver.HTTPServer(app)
        server.bind(Settings.port)
        print("main - Serving... on port {0}".format(Settings.port))
        server.start()
        tornado.ioloop.IOLoop.instance().start()
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    main()
