from __future__ import annotations
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# from tqdm.notebook import tqdm
from utilities import Logger, Decorators


log = Logger.log


class WebScraper:
    def __init__(self, root_link, topic_class, article_class):
        self.root_link = root_link
        self.__topic_class = topic_class
        self.__article_class = article_class
        self.topics = None
        self.curr_topic = None
        self.curr_topic_link = None
        self.curr_article_link = None
        self.curr_article_all_links = None
        self.curr_raw_article = None

    def get_topics(self, keep_with_base=True) -> WebScraper:
        """
        Sends a request to the root link to receive an overview of all topics covered by the newspaper.
        Exemplary topics might be "politics, economy, sport, and so on"
        It does so by executing the following steps:

            - Send a request to the root page
            - receive a Beautifulsoup object and parse it to html
            - filter out all entries that have no hyperlink references
            - Optionally keep only page references that contain the root directory link
            - at the end, it calls ``_write_topic_links_to_dict`` which creates a dictionary in which topic is
            the dictionary key and the topics hyperlink is the value

        :param keep_with_base: a flag which indicates if only hyperlinks, which have the root link inside are kept
        :type keep_with_base: bool
        :return: a WebScraper object whose ``topic`` attribute contains a dictionary of each topic found
        and its corresponding hyperlink
        :rtype: WebScraper
        """
        log.info("Retrieving all topics from webpage")
        page = requests.get(self.root_link)
        soup = BeautifulSoup(page.content, "html.parser")
        html = soup.find_all("a", class_=f"{self.__topic_class}")
        self.topics = [link.attrs["href"] for link in html if "href" in link.attrs]
        if keep_with_base:
            self.topics = [
                article for article in self.topics if self.root_link in article
            ]
        self._write_topic_links_to_dict()
        return self

    def _write_topic_links_to_dict(self) -> WebScraper:
        """
        Converts the list of hyperlinks to the respective topic section to a dictionary in which the topic is the key
        and the link is the value.

        It does so by splitting the link and setting the last split element (i.e. the topic) as a new dictionary key.

        :return:
        """
        keys = []
        for topic_link in self.topics:
            splitted = topic_link.split("/")
            splitted = [d for d in splitted if d]
            keys.append(splitted[-1])
        self.topics = dict(zip(keys, self.topics))
        return self

    def drop_topics(self, topics: list) -> None:
        """
        Drops unwanted topics from the ``topics`` attribute

        :param topics: a list of topics which shall be dropped from the scraper
        :type topics: list
        :return: the object which no longer has the topics defined in this function in its ``topics`` attribute
        :rtype: None
        """
        assert isinstance(topics, list)
        for topic in topics:
            log.info(f"Dropping topic {topic} from topics")
            self.topics.pop(topic, None)

    def keep_topics(self, topics: list) -> None:
        """
        Keeps only the topics specified in this function it the ``topics`` attribute

        :param topics: a list of topics which shall be kept in the scraper
        :type topics: list
        :return: the object which now only has the topics defined here in its ``topics`` attribute
        :rtype: None
        """
        assert isinstance(topics, list)
        log.info(f"Keeping all topics from list {topics}")
        self.topics = {key: val for key, val in self.topics.items() if key in topics}

    def set_curr_article(self, article: str) -> WebScraper:
        """
        Sets ``curr_article_link`` attribute to the article argument

        :param article: the link of the article which shall be held in the ``curr_article_link`` attribute
        :type article: str
        :return: the object with a potential change in its ``curr_article_link`` attribute
        :rtype: WebScraper
        """
        self.curr_article_link = article
        return self

    def set_topic(self, topic: str) -> WebScraper:
        """
        Resets the ``curr_topic`` and the ``curr_topic_link`` to the topic provided by the function.

        :param topic: the topic and its corresponding hyperlink which shall be set in the ``curr_topic`` and
        ``curr_topic_link`` attributes
        :type topic: str
        :raises Exception if the topic is not found in the topic list
        :return: the object whose attributes ``curr_topic`` and ``curr_topic`` have been reset
        :rtype: WebScraper
        """
        try:
            log.info(f"Setting current topic to {topic}")
            self.curr_topic = topic
            self.curr_topic_link = self.topics[topic]
            return self
        except Exception as e:
            log.error(f"Could not set topic to {topic}. Reason: {e}")
            raise e

    def get_articles_of_topic(self, keep_with_base=True) -> WebScraper:
        """
        For the topic set in the ``curr_topic`` attribute, this function retrieves all articles links from the web page.
        It does so by executing the following steps

            - Send a request to the topic page
            - receive a Beautifulsoup object and parse it to html
            - filter out all entries that have no hyperlink references
            - Optionally keep only page references that contain the root directory link

        :param keep_with_base: a flag which indicates if only hyperlinks, which have the root link inside are kept
        :type keep_with_base: bool
        :return: the object whose ``curr_article_all_links`` attribute now has all hyperlinks to
        articles for the ``curr_topic`` attribute
        :rtype: WebScraper
        """
        log.info(f"Fetching all articles of topic {self.curr_topic}")
        page = requests.get(self.curr_topic_link)
        soup = BeautifulSoup(page.content, "html.parser")
        html = soup.find_all("a", class_=f"{self.__article_class}")
        self.curr_article_all_links = [
            link.attrs["href"] for link in html if "href" in link.attrs
        ]
        if keep_with_base:
            self.curr_article_all_links = [
                article
                for article in self.curr_article_all_links
                if self.root_link in article
            ]
        log.info(
            f"Successfully retrieved {len(self.curr_article_all_links)} different articles"
        )
        return self

    """
    def _get_articles(self, link, keep_with_base=True):
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')
        html = soup.find_all('a', class_=f"{self.__article_class}")
        self.articles_links = [link.attrs['href'] for link in html if 'href' in link.attrs]
        if keep_with_base:
            self.articles_links = [article for article in self.articles_links if self.root_link in article]
        return self
    
    
    def download(self, link):
        log.info(f'Downloading article from {link}')
        page = requests.get(link)
        self.curr_raw_article = BeautifulSoup(page.content, 'html.parser')
        return self
    """

    def download_current_article(self) -> WebScraper:
        """
        Downloads the article whose hyperlink is currently set in the ``self.curr_article_link`` attribute
        The raw article is written into the ``curr_raw_article`` attribute

        :return: the object with the article written into its `´curr_raw_article`` attribute
        :rtype: WebScraper
        """
        # log.info(f'Handling: "{self.curr_article_link}"')
        page = requests.get(self.curr_article_link)
        self.curr_raw_article = BeautifulSoup(page.content, "html.parser")
        return self


class ResponseParser(WebScraper):
    def __init__(self, root_link, topic_class, article_class, parser):
        super().__init__(root_link, topic_class, article_class)
        self.parser = parser

    def basic_parse(self) -> str:
        """
        A parser method to perform basic parsing. When we are talking about basic parsing, that means that the text is
        directly retrieved from the HTML document. The parser dictionary includes the necessary information for the
        parsing. It holds the following key:value pairs:

            - "id": is the basic argument used by the ``find_all`` method of the Beautifulsoup object.
            It is the identifier inside the HTML document
            - "keyword": is the keyword used as the second argument in the ``find_all`` method
            - "parse_attr": is a Boolean flag indicating if further parsing in an already parsed text is necessary.
            This is done by yielding another key with the corresponding attribute inside the object
            - "attribute": is only set if parse_attr is set to True. Indicates the attribute to parse in an already parsed text

        :return: the parsed value
        """
        parsed_values = {}
        for entity, key_words in self.parser.items():
            value = self.curr_raw_article.find_all(
                f'{key_words["id"]}', class_=f'{key_words["keyword"]}'
            )
            if value:
                if not key_words["parse_attr"]:
                    parsed_values[entity] = self.get_text(value)
                else:
                    parsed_values[entity] = self.get_attr(value, key_words["attribute"])
        return parsed_values

    @staticmethod
    def get_text(result: BeautifulSoup) -> str:
        """
        returns the text content of a downloaded article

        :param result: the BeautifulSoup downloaded object
        :type result: BeautifulSoup
        :return: the parsed text content
        :type: str
        """
        if len(result) == 1:
            result = result[0]
            return result.text.strip()
        else:
            return None

    @staticmethod
    def get_attr(result, attribute):
        """
        Further parses a text by parsing only text with respect to the attribute provided
        
        :param result: The resulting object from the Beautifulsoup download
        :type result: BeautifulSoup
        :param attribute: the attribute the text is supposed to parses. Only text with a reference to the 
        attribute is parsed
        :type attribute: str
        :return: the resulting text after parsing for the given attribute
        :rtype str
        """
        result = [r.get_attribute_list(attribute) for r in result]
        result = [item for sublist in result for item in sublist if item]
        result = list(set(result))
        return result[0] if len(result) == 1 else result


class FAZ_Scraper(ResponseParser):
    def __init__(self, root_link, topic_class, article_class, parser):
        super().__init__(root_link, topic_class, article_class, parser)

    def download_all_articles_from_curr_topic(self) -> list:
        """
        Downloads all articles in the ``curr_article_all_links``. It does so by executing the following steps: it
        first checks if the article list is non empty and proceeds if so. Returns an empty value if not. If it is not
        empty, it iterates over all single articles and executes the following:

            - set the current article attribute to the article in the iteration loop
            - calls download_current_article which downloads the article whose link is in the current
            article link attribute
            - it calls the ``parse_faz_article`` method which parses the downloaded Beautifulsoup object.
            - it also stores the hyperlink to the article in
            - the final entry is written to a list

        At the end of the iteration, a list of all downloaded article and generated features is generated and returned

        :return: a list of all articles from the current topic
        :rtype: list
        """
        result_list = []
        log.info(f"Downloading all articles from topic {self.curr_topic}")
        if self.curr_article_all_links:
            for article in tqdm(self.curr_article_all_links):
                self.set_curr_article(article)
                self.download_current_article()
                self.parse_faz_article()
                self.parsed_values["link"] = article
                result_list.append(self.parsed_values)
                # log.info(f'Successfully parsed article and added to result list')
            return result_list
        else:
            log.warning("The current article list is empty. Use the")
            return []

    def parse_faz_article(self):
        """
        Parses the response object from the current article hyperlink. It does so by executing the following steps:

            - it calls ``basic_parse`` which handles all basic parsing elements (direct text parsing or parsing a text
            by a given attribute. The returned value are written into the tmp ``base`` variable
            - in a second step, it calls ``get_faz_text`` which retrieves FAZ specific features. The returned values
            are written into the tmp ``advanced`` variable
            - the both temporary variables are merged together
            - metadata as the section, the link and the newspaper is added

        :return:
        """
        # log.info('Parsing current article')
        base = self.basic_parse()
        advanced = self.get_faz_text()
        self.parsed_values = {**base, **advanced}
        self.parsed_values["section"] = self.curr_topic
        self.parsed_values["link"] = self.curr_article_link
        self.parsed_values["newspaper"] = "faz"

    def get_faz_text(self) -> dict:
        """
        Adds some more FAZ specific features to the parsed return value. The following additional features are added

            - ``paragraphs`` captures the number of characters in the string
            - ``external_references``: yields external hyperlink references inside the text section
            - ``nr_external_references``: yields the number of external hyperlink references in the text section
            - ``text``: yields the article's text

        :return: some additional features extracted from the response object
        :rtype: dict
        """
        return_dict = {}
        html = self.curr_raw_article.find_all("p", class_="atc-TextParagraph")
        return_dict["paragraphs"] = len(html)
        return_dict["external_references"] = self._get_ext_reference(html)
        return_dict["nr_external_references"] = len(return_dict["external_references"])
        return_dict["text"] = "".join([r.text for r in html])
        return return_dict

    @staticmethod
    def _get_ext_reference(html: BeautifulSoup) -> list:
        """
        Returns the external references found in the text object.

        :param html: the BeautifulSoup response object
        :type html: BeautifulSoup
        :return: a list of all references in the text
        :rtype: list
        """
        refs = [r.find_all("a", class_="rtr-entity") for r in html]
        refs = [item for sublist in refs for item in sublist]
        refs = [r.text for r in refs]
        return refs
