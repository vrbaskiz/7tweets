import argparse
from seventweets.application import app
from seventweets.init_db import init

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Starting db initialization and running servers ')
    subparsers = parser.add_subparsers(dest="command")
    init_parser = subparsers.add_parser('init_db')
    run_parser = subparsers.add_parser('run_server')

    args = parser.parse_args()
    if args.command == 'init_db':
        init()
    elif args.command == 'run_server':
        app.run()
