import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
#from tqdm.notebook import tqdm
from utilities import Logger, Decorators


log = Logger.log
class WebScraper:
    def __init__(self, root_link, topic_class, article_class):
        self.root_link = root_link
        self.__topic_class = topic_class
        self.__article_class = article_class
        self.topics = None
        self.curr_topic = None
        self.curr_link = None
        self.curr_article_links = None
        self.curr_raw_article = None

    def get_topics(self, keep_with_base=True):
        log.info('Retrieving all topics from webpage')
        page = requests.get(self.root_link)
        soup = BeautifulSoup(page.content, 'html.parser')
        html = soup.find_all('a', class_=f"{self.__topic_class}")
        self.topics = [link.attrs['href'] for link in html if 'href' in link.attrs]
        if keep_with_base:
            self.topics = [article for article in self.topics if self.root_link in article]
        self._get_topic_per_topic_link()
        return self

    def drop_topics(self, topics):
        assert isinstance(topics, list)
        for topic in topics:
            log.info(f'Dropping topic {topic} from topics')
            self.topics.pop(topic, None)

    def keep_topics(self, topics):
        assert isinstance(topics, list)
        log.info(f'Keeping all topics from list {topics}')
        self.topics = {key: val for key, val in self.topics.items() if key in topics}

    def set_topic(self, topic):
        try:
            log.info(f'Setting curren topic to {topic}')
            self.curr_topic = topic
            self.curr_link = self.topics[topic]
            return self
        except Exception as e:
            log.error(f'Could not set topic to {topic}. Reason: {e}')
            raise e

    def get_articles_of_topic(self, keep_with_base=True):
        log.info(f'Fetching all articles of topic {self.curr_topic}')
        page = requests.get(self.curr_link)
        soup = BeautifulSoup(page.content, 'html.parser')
        html = soup.find_all('a', class_=f"{self.__article_class}")
        self.curr_article_links = [link.attrs['href'] for link in html if 'href' in link.attrs]
        if keep_with_base:
            self.curr_article_links = [article for article in self.curr_article_links if self.root_link in article]
        log.info(f'Successfully retrieved {len(self.curr_article_links)} different articles')
        return self

    def _get_topic_per_topic_link(self):
        keys = []
        for topic_link in self.topics:
            splitted = topic_link.split('/')
            splitted = [d for d in splitted if d]
            keys.append(splitted[-1])
        self.topics = dict(zip(keys, self.topics))
        return self

    def _get_articles(self, link, keep_with_base=True):
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')
        html = soup.find_all('a', class_=f"{self.__article_class}")
        self.articles_links = [link.attrs['href'] for link in html if 'href' in link.attrs]
        if keep_with_base:
            self.articles_links = [article for article in self.articles_links if self.root_link in article]
        return self

    def download(self, link):
        # log.info(f'Downloading article from {link}')
        page = requests.get(link)
        self.curr_raw_article = BeautifulSoup(page.content, 'html.parser')
        return self

    # def download_all_current_articles(self,*func):
    #    pass
    # for j in range()


class Response_Parser(WebScraper):
    def __init__(self, root_link, topic_class, article_class, parser):
        super().__init__(root_link, topic_class, article_class)
        self.parser = parser

    def basic_parse_DL(self):
        parsed_values = {}
        for entity, key_words in self.parser.items():
            value = self.curr_raw_article.find_all(f'{key_words["id"]}', class_=f'{key_words["keyword"]}')
            if value:
                if not key_words['parse_attr']:
                    parsed_values[entity] = self.get_text(value)
                else:
                    parsed_values[entity] = self.get_attr(value, key_words['attribute'])
        return parsed_values

    @staticmethod
    def get_text(result):
        if len(result) == 1:
            result = result[0]
            return result.text.strip()
        else:
            return None

    @staticmethod
    def get_attr(result, attribute):
        result = [r.get_attribute_list(attribute) for r in result]
        result = [item for sublist in result for item in sublist if item]
        result = list(set(result))
        return result[0] if len(result) == 1 else result


class FAZ_Scraper(Response_Parser):
    def __init__(self, root_link, topic_class, article_class, parser, advanced_parser):
        super().__init__(root_link, topic_class, article_class, parser)
        self.advanced_parser = advanced_parser

    def download_all_current_articles(self):
        result_list = []
        # print(f'Downloading all articles from topic {self.curr_topic}')
        for article in tqdm(self.curr_article_links):
            self.download(article)
            self.parse_faz_article()
            result_list.append(self.parsed_values)
        return result_list

    def parse_faz_article(self):
        # log.info('Parsing current article')
        base = self.basic_parse_DL()
        nested = self.get_faz_text()
        self.parsed_values = {**base, **nested}
        self.parsed_values['section'] = self.curr_topic
        self.parsed_values['newspaper'] = 'faz'

    def get_faz_text(self):
        return_dict = {}
        html = self.curr_raw_article.find_all('p', class_="atc-TextParagraph")
        return_dict['paragraphfs'] = len(html)
        return_dict['external_references'] = self._get_ext_reference(html)
        return_dict['nr_external_references'] = len(return_dict['external_references'])
        return_dict['text'] = "".join([r.text for r in html])
        return return_dict

    @staticmethod
    def _get_ext_reference(html):
        refs = [r.find_all('a', class_='rtr-entity') for r in html]
        refs = [item for sublist in refs for item in sublist]
        refs = [r.text for r in refs]
        return refs