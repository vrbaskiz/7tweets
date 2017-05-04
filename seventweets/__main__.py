"""
SevenTweets is twitter-like service where each participant controls
its own node. They are connected and known to each other by discovery.

All user data is always stored in its own node. Other nodes can search 
and return data from other nodes and display them, but node that owns 
data has to be online.
"""
import sys
import argparse
import logging
from seventweets.application import app
from seventweets.migrations import migrate

LOG_FORMAT = ('%(asctime)-15s %(levelname)s: '
              '%(message)s [%(filename)s:%(lineno)d]')


logger = logging.getLogger(__name__)


def main(argv):
    logging.basicConfig(
        level=logging.DEBUG,
        format=LOG_FORMAT,
    )

    logger.info('Starting seventweets with parameters: %s', ', '.join(argv))

    parser = argparse.ArgumentParser(
        description=__doc__)
    subparsers = parser.add_subparsers(dest="command")
    run_parser = subparsers.add_parser('runserver')
    migrate_parser = subparsers.add_parser('migrate')

    migrate_parser.add_argument('-d', '--direction', dest='direction',
                                choices=['up', 'down'], default='up',
                                metavar='DIRECTION',
                                help='To perform up or down migrations.')

    args = parser.parse_args(argv)
    if args.command == 'migrate':
        migrate(args.direction)
    elif args.command == 'runserver':
        app.run()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
