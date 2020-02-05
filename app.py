from Webscraper import FAZ_Scraper
from utilities import Logger
from pymongo import MongoClient
from tqdm import tqdm

log = Logger.log
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
faz_nested_parser = {
    'text' : {
        'text' : ('p','atc-TextParagraph'),
        'ref' : ('a','rtr-entity')
    }
}

scraper = FAZ_Scraper(root_link=faz_dic['root_link'],
                      topic_class=faz_dic['topic_link'],
                      article_class=faz_dic['article_link'],
                      parser=faz_base_parser,
                     advanced_parser=faz_nested_parser)

def run_scraper():
    client = MongoClient('localhost', 27017)
    mongo_collection = client.test_scraper
    mongo_db = mongo_collection.db
    scraper = FAZ_Scraper(root_link=faz_dic['root_link'],
                      topic_class=faz_dic['topic_link'],
                      article_class=faz_dic['article_link'],
                      parser=faz_base_parser,
                     advanced_parser=faz_nested_parser)
    scraper.get_topics()
    for topic in tqdm(scraper.topics):
        scraper.set_topic(topic).get_articles_of_topic()
        results= scraper.download_all_current_articles()
        log.info(f'Writing a total of {len(results)} into db {mongo_db} for topic {scraper.curr_topic}')
        mongo_db.insert_many(results)

if __name__ == '__main__':
    run_scraper()