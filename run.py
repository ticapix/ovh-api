import tornado
from service import main


if __name__ == "__main__":
    app = main.make_app(autoreload=True)
    app.listen(8000, address="0.0.0.0")
    tornado.ioloop.IOLoop.current().start()
