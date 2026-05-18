from os import environ
from multiprocessing import Process
import logging

from otree.main import setup
from otree.cli.prodserver1of2 import run_asgi_server
from otree.tasks import Worker

dburl = environ.get('DATABASE_URL')
assert dburl.startswith("postgres")

addr = environ.get('HOST', "0.0.0.0")
port = environ.get('PORT', "8000")


class WorkerProcess(Process):
    def __init__(self):
        super().__init__()
        self.worker = Worker(port)

    def run(self):
        self.worker.listen()


setup()

logging.getLogger('root').setLevel(logging.DEBUG)

worker = WorkerProcess()
worker.start()

run_asgi_server(addr, port)
