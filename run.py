import tornado
from service import main


if __name__ == "__main__":
    app = main.make_app(autoreload=True)
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
