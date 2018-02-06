#!/usr/bin/env python3
import logging

from chat.client import ChatClient


logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s')
LOG = logging.getLogger(__name__)


def main():
    chat = ChatClient()
    chat.run()


if __name__ == '__main__':
    main()
