# -*- coding: utf-8 -*-

#!/usr/bin/env python

__author__ = 'cbb'

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import web
import os, time, hashlib
from main import run_all
from util.codeConvert import GetTime



from datetime import datetime; now = datetime.now()
from web import form

db = web.database(dbn='mysql', user='root', pw='root', db='awesome')
render = web.template.render("./www/templates")

urls = (
    '/', 'index',
    '/menu', 'Menu',
    '/download', 'download',
    '/upload', 'Upload',
    '/result', 'resultList',
    '/run_video_search', 'run_video_search'

)

app = web.application(urls, globals())

login = form.Form(
    form.Textbox('username'),
    form.Password('password'),
    form.Button('Login'),

    validators = [form.Validator("UserName o r Passwords can't null.", lambda i: len(i.password) > 0 and len(i.username) > 0)]

)

class index:

    def GET(self):

        try:

            cookies = web.cookies().get('videosite')
            if not cookies == None:
                web.seeother('/menu')
                return
        except Exception, e:
            print str(e)

        f = login()
        return render.formtest(f)

    def POST(self):
        f = login()
        if not f.validates():
            return render.formtest(f)
        else:
            users = db.query("select * from users where name='%s' and password='%s'" % (f.username.value, f.password.value))
            # for user in users:
            #     print user.id, user.name
            if len(users) > 0:
                expires = int(time.time() + 86400)
                web.setcookie('videosite', hashlib.md5('%s-%s-%s' % (f.username.value, f.password.value, str(expires))).hexdigest(), 86400)
                web.seeother('/menu')

class Menu:

    def GET(self):
        return """<html><head>video menu</head><body>
                <li>
                <a target="_self" href="/upload">upload key</a>
                </li>
                <li>
                <a target="_self" href="/run_video_search">run video search</a>
                </li>
                <li>
                <a target="_self" href="/result">result list</a>
                </li>
                </body></html>"""

# class Index:
#     def GET(self):
#         cookies = web.cookies().get('videosite')
#         if cookies == None:
#             web.seeother('/')
#             return
#
#         return """<html><head>videosearch</head><body>
#                 <li>
#                 <a target="_self" href="/upload">upload</a>
#                 </li>
#                 <li>
#                 <a target="_self" href="/run_video_search">run video search</a>
#                 </li>
#                 <li>
#                 <a target="_self" href="/result">result list</a>
#                 </li>
#                 </body></html>"""


class run_video_search:
    def GET(self):
        run_all()
        return 'Hello, ' + 'Video' + '!'


BUF_SIZE = 262144

class download:
    def GET(self, file_name):
        cookies = web.cookies().get('videosite')
        if cookies == None:
            web.seeother('/')
            return

        #file_name = 'qq_video.xlsx'
        file_path = os.path.join('./data', file_name)
        f = None
        try:
            f = open(file_path, "rb")
            web.header('Content-Type','application/octet-stream')
            web.header('Content-disposition', 'attachment; filename=%s' % file_name)
            while True:
                c = f.read(BUF_SIZE)
                if c:
                    yield c
                else:
                    break
        except Exception, e:
            print e
            yield 'Error'
        finally:
            if f:
                f.close()

class Upload:
    def GET(self):
        return """<html><head></head><body>
                <form method="POST" enctype="multipart/form-data" action="">
                <input type="file" name="myfile" />
                <br/>
                <input type="submit" />
                </form>
                </body></html>"""

    def POST(self):
        x = web.input(myfile={})
        web.debug(x['myfile'].filename)
        web.debug(x['myfile'].value)
        web.debug(x['myfile'].file.read())
        raise web.seeother('/')

class resultList:

    def GET(self):
        #获取文件列表
        files = os.listdir('./data')
        files = [f for f in files if '.xlsx' in f]

        posts = []
        for f in files:
            statinfo = os.stat('./data/%s' % f)
            item = FileItem()
            item.file_name = f
            item.modify_time = GetTime(statinfo.st_ctime)
            posts.append(item)

        return render.list(posts)
        # template = "$def with (infos)\nHello $name"


        template = '''$def with(rows)

        $for row in rows:
            <li>
                <a href="/data/$row.file_name">$row.file_name  $row.modify_time</a>

            </li>
        '''
        hello = web.template.Template(template)
        return hello(posts)

class FileItem:
    def __init__(self):
        self.file_name = ''
        self.modify_time = ''


if __name__ == "__main__":
    app.run()