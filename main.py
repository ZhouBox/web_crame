import tornado.ioloop
import tornado.web
import tornado.gen
import cv2

from tornado.options import define,  options

define("port", default = 5000, help = "run in tornado on xxxx port", type = int)
define("id", default = 0, help = "camera id", type = int)


def auth(func):
    def _auth(self):
        if not self.current_user:
            re = {"code" : 404, "message" : "login failed!"}
            self.write(re)
        else:
            func(self)
    return _auth;


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")



class LoginHandler(BaseHandler):
    def get(self):
        self.write('<html><body><form action="/login" method="post">'
                   'Name: <input type="text" name="name">'
                   '<input type="submit" value="Sign in">'
                   '</form></body></html>')

    def post(self):
        name = self.get_argument("name", "error")
        if name == "error":
            re = {"code" : 404, "message" : "login failed!"}
        else:
            self.set_secure_cookie("user", name)
            re = {"code" : 200, "message" : "login successfully!"}
        self.write(re)



class CameraHandler(BaseHandler):
    @auth
    def get(self):
        ret, image = self.application.cap.read()
	if ret:
            self.set_header("Content-Type", "image/jpeg")
            self.set_header("Refresh", "1") 
	    self.set_header("content-transfer-encoding", "binary")
            r, i = cv2.imencode('.jpg', image)
	    if r:
                self.write(bytes(i.data))
            else:
                selt.write('Sorry, encode faily!')
        else:
	    self.write('Sorry, get camera data faily!')



class Application(tornado.web.Application):
    def __init__(self, camera_id):
        handlers = [('/camera', CameraHandler), ('/login', LoginHandler)]
        self.cap = cv2.VideoCapture(camera_id)
        self.camera_id = camera_id;
        tornado.web.Application.__init__(self, handlers, debug = True ,cookie_secret = "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o")

    def __del__(self):
        self.cap.release()


if __name__ == '__main__':
    tornado.options.parse_command_line();
    app = Application(options.id)
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
