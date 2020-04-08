from Webscraper import FAZ_Scraper
from utilities import Logger, Decorators, read_config
from pymongo import MongoClient
import argparse
import json
from tqdm import tqdm
import argparse
from time import gmtime, strftime

log = Logger.log
conf = read_config('config.yaml')
faz_dic = conf['faz_dic']
faz_base_parser = conf['faz_base_parser']
"""
faz_dic = {
        'root_link': "https://www.faz.net",
        'topic_link' : 'lay-MegaMenu_SectionTitleLink',
        'article_link': 'js-hlp-LinkSwap js-tsr-Base_ContentLink tsr-Base_ContentLink',
    }

faz_base_parser = {
    'time' : {
        'id' : 'time',
        'keyword' : "atc-MetaTime",
        'parse_attr': False
        },
    'headline' : {
        'id' : 'span',
        'keyword' : "atc-HeadlineText",
        'parse_attr': False
        },
    'headline_emphasis':{
        'id' : 'span',
        'keyword' : "atc-HeadlineEmphasisText",
        'parse_attr': False
        },
    'author':{
        'id' : 'a',
        'keyword' : "atc-MetaAuthorLink",
        'parse_attr': False
        },
    'comments' : {
        'id' : 'ul',
        'keyword' : "ctn-PageFunctions_List js-sharebuttons",
        'attribute' :'data-comment-value',
        'parse_attr': True
        },
    'recommendation' : {
        'id' : 'ul',
        'keyword' : "ctn-PageFunctions_List js-sharebuttons",
        'attribute' :'data-empfehlen-value',
        'parse_attr': True
        }
}
"""
scraper = FAZ_Scraper(root_link=faz_dic['root_link'],
                      topic_class=faz_dic['topic_link'],
                      article_class=faz_dic['article_link'],
                      parser=faz_base_parser)


def convert_arg_str_to_bool(arg):
    return 1 if arg =="y" else 0

@Decorators.run_time
def run_scraper(write_json, write_mongo, host, port, collection, database):
    log.info(f'Running the Web Scraper with the following arguments:\nWrite to JSON:{write_json}\nWrite to MongoDB:{write_mongo}\nHost:{host}\nPort:{port}'
             f'\ncolletion:{collection}\ndatabase:{database}')

    if convert_arg_str_to_bool(write_mongo):
        client = MongoClient(host, port)
        mongo_collection = client[collection]
        mongo_db = mongo_collection.get_collection(database)
    scraper = FAZ_Scraper(root_link=faz_dic['root_link'],
                      topic_class=faz_dic['topic_link'],
                      article_class=faz_dic['article_link'],
                      parser=faz_base_parser)
    scraper.get_topics()
    for topic in tqdm(scraper.topics):
        scraper.set_topic(topic).get_articles_of_topic()
        results= scraper.download_all_articles_from_curr_topic()
        if convert_arg_str_to_bool(write_json):
            ts = strftime("%Y%m%d%H%M%S", gmtime())
            outfile = f"{topic}_{ts}.json"
            log.info(f'Writing data to "{outfile}"' )
            with open(outfile, 'w') as fp:
                json.dump(results, fp)
        if convert_arg_str_to_bool(write_mongo):
            try:
                log.info(f'Writing a total of {len(results)} into db {mongo_db} for topic {scraper.curr_topic}')
                mongo_db.insert_many(results)
            except Exception as e:
                log.error(e)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Setup a Mongo database.')
    parser.add_argument(
        "--write_json",
        "-json",
        default="y",
        type=str,
        choices=["n","y"],
        help="A flag indicating if the result data shall be written to disk in a JSON file. y if yes, else n"
    )
    parser.add_argument(
        "--write_db",
        "-db",
        default="n",
        type=str,
        choices=["n","y"],
        help="A flag indicating if the result data shall be written into a MongoDB database. y if yes, else n"
    )
    parser.add_argument(
        "--host",
        "-hst",
        default='localhost',
        help="If the file written to a MongoDB, specify host here"
    )
    parser.add_argument(
        "--port",
        "-p",
        default=27017,
        type=int,
        help='If the file written to a MongoDB, specify port here'
    )
    parser.add_argument(
        "--collection",
        "-c",
        default="test_scraper",
        type=str,
        required=False,
        help="If the file written to a MongoDB, specify the collection here"
    )
    parser.add_argument(
        "--database",
        '-d',
        default='db',
        type=str,
        required=False,
        help="If the file written to a MongoDB, specify the database here"
    )
    args = parser.parse_args()
    run_scraper(
        args.write_json,
        args.write_db,
        args.host,
        args.port,
        args.collection,
        args.database
    )
    #write_json, write_mongo, host, port, collection, database