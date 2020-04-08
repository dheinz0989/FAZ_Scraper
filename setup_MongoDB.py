import argparse
from pymongo import MongoClient
from utilities import Logger

log = Logger.log
def setup(host,port,collection,database):
    try:
        log.info(f'Setting up a Mongo client data base with the followng arguments:\nHost:{host}\nPort:{port}\ncolletion:{collection}\ndatabase:{database}')
        client = MongoClient(host, port)
        client_collection = client[collection]
        client_collection.create_collection(database)
    except Exception as e:
        log.warning(f'Failed for the following reason:\n{e}')
        raise e


if __name__ =="__main__":
    parser = argparse.ArgumentParser(description='Setup a Mongo database.')
    parser.add_argument(
        "--host",
        default='localhost',
        help="The host the Mongo client useds to connect"
    )
    parser.add_argument(
        "--port",
        default=27017,
        type=int,
        help='The port used for the Mongo client connection'
    )
    parser.add_argument(
        "--collection",
        default="test_collection",
        type=str,
        required=False
    )
    parser.add_argument(
        "--database",
        default='faz_articles',
        type=str,
        required=False
    )
    args = parser.parse_args()
    setup(
        args.host,
        args.port,
        args.collection,
        args.database
    )
    print(args.port)

