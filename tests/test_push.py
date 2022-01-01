import settings
from util.push import push
from util.push import strategy
import logging


def test_push():
    settings.init()
    push("测试")


def test_strategy():
    settings.init()
    strategy("")
    strategy("1")


logging.basicConfig(format='%(asctime)s %(message)s', filename='../sequoia.log')
logging.getLogger().setLevel(logging.INFO)
