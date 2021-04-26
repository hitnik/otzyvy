import datetime
import aiohttp
import asyncio
import async_timeout
from bs4 import BeautifulSoup
import re
from concurrent.futures import ALL_COMPLETED
from queue import Queue, Empty
import queue
from sqlalchemy import create_engine, MetaData, Table,func
from  sqlalchemy.exc import SQLAlchemyError
import sqlalchemy.orm
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy import and_
from threading import Thread
import threading
import random
import time
import logging
import logging.config
import pytz
import urllib.request
import gzip
from bs4 import UnicodeDammit
import sys
import os
from urllib.parse import urlsplit, urlunsplit

DICTLOGCONFIG={
"version":1,
        "handlers":{
            "fileHandler":{
                "class":"logging.FileHandler",
				"encoding": "utf8",
                "formatter":"myFormatter",
                "filename":"./parser.log"
            }
        },
        "loggers":{
            "parser":{
                "handlers":["fileHandler"],
                "level":"ERROR",
            },
            "sqlalchemy":{
                "handlers":["fileHandler"],
                "level":"ERROR",
            }
        },
        "formatters":{
            "myFormatter":{
                "format":"[%(asctime)s] - %(levelname)s - %(message)s"
            }
        }
}


SQL_DATABASE = os.getenv('POSTGRES_DB')
SQL_USER = os.getenv('POSTGRES_USER')
SQL_PASSWORD = os.getenv('POSTGRES_PASSWORD')
SQL_HOST = os.getenv('SQL_HOST')
SQL_PORT = os.getenv('SQL_PORT')

DB_STRING = 'postgresql+psycopg2://' + SQL_USER + ':' + SQL_PASSWORD + '@' + SQL_HOST + '/' + SQL_DATABASE


RU_MONTH_VALUES = {
    'января': 1,
    'февраля': 2,
    'марта': 3,
    'апреля': 4,
    'мая': 5,
    'июня': 6,
    'июля': 7,
    'августа': 8,
    'сентября': 9,
    'октября': 10,
    'ноября': 11,
    'декабря': 12,
}

SITE_NAME = {
    'onliner': 'onliner.by',
    'providers': 'providers.by',
    'otzyvy': 'otzyvy.by',
}

HEADERS = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate',
           'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pl;q=0.6,be;q=0.5',
           'Connection': 'keep-alive',
           'Cookie': '_ym_uid=15133407201047879625; caltat=14d6a4fffffd4743b8ae3bc14311cd43; _ga=GA1.2.504420028.1513340718; PHPSESSID=elmpstnonb3sgghv2fccga0em4; _gid=GA1.2.1784003027.1515861623; _ym_isad=2; _ym_visorc_155730=w; __atuvc=4%7C50%2C5%7C51%2C40%7C2%2C20%7C3; __atuvs=5a5b285f231ed266002; pa=1515880691552.59420.8417430268990136providers.by0.053914998342112774+5; tmr_detect=0%7C1515925222838; __ar_v4=Z3P3TINHFRAMFDXZYF2TX6%3A20180113%3A4%7CH3D6WDXSVVDRTO4GVKQUDP%3A20180113%3A4%7CYYD3BVUVYFHDDLFD6Y5AJQ%3A20180113%3A4',
           'DNT': '1',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
           }

# TIMESTART = 30
# TIMEEND = 50

TIMESTART = 300
TIMEEND = 500

newThread = True


class Post:
    postId = 0
    userId = 0
    user = ''
    dateTime = None
    postContent = ''

    def __str__(self):
        return str(self.postId + ' ' + self.userId + ' ' + self.user + ' ' +
                   datetime.datetime.strftime(self.dateTime, "%Y.%m.%d %H:%M:%S") + ' ' + self.postContent)


class ForumURL(object):
    def __init__(self, id, name, url, site_id, isActive, pages, pagesTotal):
        self.id = id
        self.name = name
        self.url = url
        self.site_id = site_id
        self.isActive = isActive
        self.pages = pages
        self.pagesTotal = pagesTotal


class SiteMeta:
    def __init__(self, forumURL: ForumURL, html):
        self.forumURL = forumURL
        self.html = html


class ForumUser(object):
    def __init__(self, id, name, site_id):
        self.id = id
        self.name = name
        self.site_id = site_id

    def __str__(self):
        return str(self.id) + ' ' + self.name + " " + str(self.site_id)


class PostMeta():
    def __init__(self, forumURL: ForumURL, postlist, pagesFromSite):
        self.postList = postlist
        self.forumURL = forumURL
        self.pagesFromSite = pagesFromSite


class Topic(object):
    def __init__(self, id, user_id, topicText, site_id, datePost, dateModified,url):
        self.id = id
        self.user_id = user_id
        self.topicText = topicText
        self.site_id = site_id
        self.datePost = datePost
        self.dateModified = dateModified
        self.url=url


class Site(object):
    def __init__(self, id, name, short):
        self.id = id
        self.name = name
        self.short = short



class DBcontrolller:
    def __init__(self, *args, **kwargs):
        self.engine = create_engine(*args, **kwargs)

        metadata = MetaData(self.engine)
        self.forum = Table('forumTopics_forums', metadata, autoload=True)
        mapper(ForumURL, self.forum)
        self.forumUsers = Table('forumTopics_forumusers', metadata, autoload=True)
        mapper(ForumUser, self.forumUsers)
        self.forumTopics = Table('forumTopics_topics', metadata, autoload=True)
        mapper(Topic, self.forumTopics)
        self.sites = Table('forumTopics_sites', metadata, autoload=True)
        mapper(Site, self.sites)

    def dispose(self):
        self.engine.dispose()

    def getSession(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session

    def selectListOfForumsFromDB(self):
        """
        get list of all URLs of forums
        :return: list of ForumURL
        """
        session = self.getSession()
        result = session.query(ForumURL).filter(ForumURL.isActive == '1').all()
        # logger = logging.getLogger("parser")
        # logger.info("get %d records of Forums from DB" % len(result))
        session.close()
        return result

    def insertForumUserToDB(self, userToSave : ForumUser, session):
        """
            try to insert ForumUser object to DB
        :param userToSave:
        :return: result of insert ForumUser object to DB
        """

        userFromDB = session.query(ForumUser).filter(and_(ForumUser.name == userToSave.name,
                                                          ForumUser.site_id == userToSave.site_id)).scalar()
        if userFromDB == None:
            userFromDB = session.query(ForumUser).filter(ForumUser.id == userToSave.id).scalar()
            if userFromDB:
                userFromDB.name = userToSave.name
                session.commit()
                result = userFromDB.id
            else:
                session.add(userToSave)
                session.commit()
                result = userToSave.id
        else:
            result = userFromDB.id
        return result

    def insertTopicToDB(self, topic: Topic, session):
        topicFromDB = session.query(Topic).filter(Topic.id == topic.id).scalar()
        result = True
        if topicFromDB == None:
            session.add(topic)
            session.commit()
        else:
            result = False
        return result

    def updateForumEntry(self, forumURL: ForumURL, session):
        # logger = logging.getLogger("parser")
        # session = self.getSession()
        query = session.query(ForumURL).filter(ForumURL.id == forumURL.id)
        query = query.update({self.forum.c.pages.name: forumURL.pages,
                              self.forum.c.pagesTotal: forumURL.pagesTotal})
        session.commit()
        session.close()
        # logger.info('%s put to DB pages: %d, totalPages: %d' % (forumURL.name, forumURL.pages, forumURL.pagesTotal))

    def getSiteByID(self, id):
        session = self.getSession()
        query = session.query(Site).filter(Site.id == id)
        result = query.one()
        session.close()
        return result

    def clearMappers(self):
        sqlalchemy.orm.clear_mappers()


class URLProcessor():
    def onlinerCreateURL(self, forumURL: ForumURL):
        if forumURL.pages == forumURL.pagesTotal \
                and forumURL.pagesTotal > 0:
            url = forumURL.url + str(forumURL.pages * 20 - 20)
        elif forumURL.pages > 0 and newThread:
            url = forumURL.url + str((forumURL.pages) * 20 - 20)
        elif forumURL.pages > 0:
            url = forumURL.url + str((forumURL.pages + 1) * 20 - 20)
        elif forumURL.pages == 0:
            url = forumURL.url + str(forumURL.pages)

        return url

    def providersCreateURL(self, forumURL: ForumURL):
        if forumURL.pages == forumURL.pagesTotal \
                and forumURL.pagesTotal > 0:
            url = forumURL.url + '1/'
        elif forumURL.pages == 1 and forumURL.pagesTotal > 0:
            url = forumURL.url + str(forumURL.pagesTotal) + '/'
        elif forumURL.pages > 0:
            url = forumURL.url + str(forumURL.pagesTotal - forumURL.pages) + '/'
        elif forumURL.pages == 0:
            url = forumURL.url + '1/'
        return url

    def otzyvyCreateURL(self, forumURL: ForumURL):
        if forumURL.pages == forumURL.pagesTotal \
                and forumURL.pagesTotal > 0:
            url = forumURL.url + '0.html'
        elif forumURL.pages == 1 and forumURL.pagesTotal > 0:
            url = forumURL.url + str(forumURL.pagesTotal) + '.html'
        elif forumURL.pages > 0:
            url = forumURL.url + str(forumURL.pagesTotal - forumURL.pages - 1) + '.html'
        elif forumURL.pages == 0:
            url = forumURL.url + '0.html'
        return url

    @staticmethod
    async def aURLtoHTML(forumURL: ForumURL):
        async def fetch(session, url):
            with async_timeout.timeout(30):
                async with session.get(url) as response:
                    return await response.read()


        async with aiohttp.ClientSession(headers=HEADERS) as session:
            html = await fetch(session, forumURL.url)
            siteMeta = SiteMeta(forumURL, html)
            # logger = logging.getLogger("parser")
            # logger.info('get %d bytes html' % len(html))
            return siteMeta

    @staticmethod
    def URLtoHTML(forumURL: ForumURL):
        req = urllib.request.Request(forumURL.url, headers=HEADERS)
        with urllib.request.urlopen(req) as response:
            if response.info().get('Content-Encoding') == 'gzip':
                html = gzip.decompress(response.read())
            elif response.info().get('Content-Encoding') == 'deflate':
                html = response.read()
            elif response.info().get('Content-Encoding'):
                print('Encoding type unknown')
            else:
                html = response.read()
        siteMeta = SiteMeta(forumURL, html)
        # logger = logging.getLogger("parser")
        # logger.info('get %d bytes html' % len(html))
        return siteMeta

    @staticmethod
    def makeTopicURL(siteid, postId, urlRaw):
        if siteid == 1:
            url = re.sub(r'start=\d+$', 'p=' + str(postId), urlRaw)
            return url
        elif siteid == 2:
            url = re.sub(r'page/\d+/$', str(postId), urlRaw)
            url += '/'
            return url
        elif siteid == 3:
            string = 'comments/' + str(postId) + '.html'
            url = re.sub(r'show/20/page/\d+.html$', string, urlRaw)
            return url
        else:
            return ''


class ForumScrapper:

    def __dateFromStringToDate(self, dateString):
        for k, v in RU_MONTH_VALUES.items():
            dateString = dateString.replace(k, str(v))
        d = datetime.datetime.strptime(dateString, '%d %m %Y %H:%M')
        threeHours= datetime.timedelta(hours=3)
        d = d - threeHours
        date = d.replace(tzinfo=pytz.utc)
        # d = pytz.timezone('Europe/Minsk').localize(d, is_dst=True)
        return date

    @staticmethod
    def scrapeTopics(siteMeta: SiteMeta, loop):

        dammit = UnicodeDammit(siteMeta.html)
        if dammit.unicode_markup:
            soup = BeautifulSoup(dammit.unicode_markup, 'html.parser')
        else:
            soup = BeautifulSoup(siteMeta.html, 'html.parser')
        forumScrapper = ForumScrapper()
        for k, v in SITE_NAME.items():
            if re.search(v, siteMeta.forumURL.url):
                str = k
                strPages = k + "Pages"
                scrape = getattr(forumScrapper, str)
                getPages = getattr(forumScrapper, strPages)
                posts = scrape(soup, loop)
                pagesFromSite = getPages(soup)
                forumURL = siteMeta.forumURL
                if pagesFromSite:
                    postMeta = PostMeta(forumURL, posts, pagesFromSite)
                else:
                    postMeta = PostMeta(forumURL, posts, forumURL.pagesTotal)
                return postMeta

    def onlinerPages(self, soup: BeautifulSoup):
        temp = soup.find(class_='pages-fastnav')
        if temp:
            allLi = temp.find_all('li')
            if re.match(r'\d+', allLi[-1].get_text()):
                pagesTotal = int(allLi[-1].get_text())
            else:
                pagesTotal = int(allLi[-2].get_text())
            return pagesTotal
        else:return None

    def onliner(self, soup: BeautifulSoup, loop):
        postsList = soup.find_all(class_='msgpost')
        # logger = logging.getLogger("parser")
        if len(postsList) == 0:
            return None
        # logger.info('postlist len %d' % len(postsList))
        postsList.pop(0)

        async def findPosts(postSoup):
            post = Post()
            await asyncio.sleep(0)
            post.userId = postSoup.contents[1].attrs['data-user_id']
            post.user = postSoup.find('a').text
            postMessage = BeautifulSoup(postSoup.find(class_="msgpost-txt-i").decode(), 'html.parser')
            post.dateTime = self.__dateFromStringToDate(postMessage.span.text)
            post.postId = postMessage.small.attrs['id']
            postContent = ""
            for child in postMessage.find(class_='content').children:
                postContent += str(child)
            post.postContent = postContent

            return post

        async def fetch():
            futures = [findPosts(i) for i in postsList]
            try:
                done, _ = await asyncio.wait(futures, return_when=ALL_COMPLETED)
            except ValueError as e:
                # logger = logging.getLogger("parser")
                # logger.exception(e)
                return None
            list = []
            for i in done:
                list.append(i.result())
            return list

        result = loop.run_until_complete(fetch())
        return result

    def providersPages(self, soup: BeautifulSoup):
        pagesTotal = 0
        temp = soup.find(class_='navigation')
        try:
            allLi = temp.find_all('li')
        except AttributeError:
            # logger = logging.getLogger("parser")
            # logger.error('can\'t get pages from providers.by ')
            return pagesTotal
        if re.match(r'\w+', allLi[-1].get_text()):
            pagesTotal = int(allLi[-1].get_text())
        else:
            pagesTotal = int(allLi[-2].get_text())
        return pagesTotal

    def providers(self, soup: BeautifulSoup, loop):
        # logger = logging.getLogger("parser")
        postsList = soup.find_all(class_='hreview')
        if len(postsList) == 0:
            # logger = logging.getLogger("parser")
            # logger.error('no topics on this page of providers.by')
            return None
        # logger.info('postlist len %d' % len(postsList))

        async def findPosts(postSoup):
            post = Post()
            await asyncio.sleep(0)
            id = re.findall(r'/(\d+)/$', postSoup.find('a').get('href'))[0]
            post.postId = id
            post.userId = id
            post.user = re.sub("^\s+|\n|\r|\s+$", '', postSoup.find(class_='reviewer vcard').span.text)
            post.dateTime = self.__dateFromStringToDate(postSoup.find(class_='date').text.replace(',', ''))
            post.postContent = postSoup.find(class_='plus').decode()
            post.postContent += postSoup.find(class_='minus').decode()
            post.postContent += postSoup.find(class_='result').decode()
            return post

        async def fetch():
            futures = [findPosts(i) for i in postsList]
            try:
                done, _ = await asyncio.wait(futures, return_when=ALL_COMPLETED)
            except ValueError:
                return None
            list = []
            for i in done:
                list.append(i.result())
            return list

        result = loop.run_until_complete(fetch())
        return result
    # Если будут ошибки, убрать if temp

    def otzyvyPages(self, soup: BeautifulSoup):

        pagesTotal = 0
        temp = soup.find(class_='otz')
        if temp:
            nobr = temp.find('nobr').text
            rawstring = re.search(r'\d+$', nobr).group()
            if int(rawstring) % 20 > 0:
                pagesTotal = int(rawstring) // 20 + 1
            else:
                pagesTotal = int(rawstring) // 20
        return pagesTotal

    def otzyvy(self, soup: BeautifulSoup, loop):
        # logger = logging.getLogger("parser")
        postsList = soup.find_all(class_='otzyv')
        if len(postsList) == 0:
            # logger.error('no topics on this page of otzyvy.by.by')
            return None
        # logger.info('postlist len %d' % len(postsList))

        async def findPosts(postSoup):
            post = Post()
            await asyncio.sleep(0)
            temp = postSoup.find_all('a')
            for i in temp:
                match = re.search(r'/internet_provajdery/5840/comments/', i.decode())
                if match:
                    id = (re.search(r'/5840/comments/(\d+)\.html', i.decode()).group(1))
                    post.postId = id
                    post.userId = id
            dateTimeString = postSoup.find(class_='dtreviewed').text.replace('.', ' ')
            post.dateTime = self.__dateFromStringToDate(dateTimeString)
            post.user = postSoup.find(class_='vcard').text
            post.postContent = postSoup.find(class_='description').text
            return post

        async def fetch():
            futures = [findPosts(i) for i in postsList]
            try:
                done, _ = await asyncio.wait(futures, return_when=ALL_COMPLETED)
            except ValueError:
                return None
            list = []
            for i in done:
                list.append(i.result())
            return list

        result = loop.run_until_complete(fetch())
        return result


def converImgUrls(url, html):

    html = '<div>'+html+'</div>'
    bs = BeautifulSoup(html, 'html.parser')
    images = bs.find_all('img')

    for img in images:
        src = img.attrs['src']
        if src and re.match(r'./', src):
            src = re.sub(r'^\.', '', src)
            img.attrs['src'] = urlunsplit((url.scheme, url.netloc, src, '', ''))
    return str(bs)


def fetchParser(dbcontrol, loop):
    # logger = logging.getLogger("parser")

    try:
        forumURLList = dbcontrol.selectListOfForumsFromDB()
    except SQLAlchemyError:
        pass
    list = [i for i in range(len(forumURLList))]
    random.shuffle(list)
    # logger.info(list)
    for i in list:
        # logger.info("Put to QUEUE")
        timeDelay = random.randrange(TIMESTART, TIMEEND)
        # logger.info(forumURLList[i].name)
        # logger.info('fetching urlToSitemeta')
        forumURL = forumURLList[i]
        processor = URLProcessor()
        for k, v in SITE_NAME.items():
            if re.search(v, forumURL.url):
                str = k + "CreateURL"
                createURL = getattr(processor, str)
                forumURL.url = createURL(forumURL)
        # logger.info(forumURL.url)
        # logger.info("FETCHING URL!!!!!!!!!")
        # siteMeta = processor.URLtoHTML(forumURL)

        async def asynchronous():
            futures = [URLProcessor.aURLtoHTML(forumURL)]
            done, _ = await asyncio.wait(
                futures, return_when=ALL_COMPLETED)
            for i in done.__iter__():
                 return i.result()

        try:
            siteMeta = loop.run_until_complete(asynchronous())
        except asyncio.TimeoutError:
            loop.stop()
            continue
        except (RuntimeError, ConnectionRefusedError,
                aiohttp.client_exceptions.ClientConnectionError,
                OSError,
                ):
            continue

        # logger.info('FETCHING siteMetaToTopisc')
        postMeta = ForumScrapper.scrapeTopics(siteMeta, loop)
        del(siteMeta)
        # logger.info(postMeta.forumURL.pagesTotal)
        if postMeta.postList:
            # logger.info('%d topics scrapped' % len(postMeta.postList))
            # logger.info('fetching insert to DB')
            forumURL = postMeta.forumURL
            postList = postMeta.postList
            pagesFromSite = postMeta.pagesFromSite
            # print(newThread)
            if forumURL.pages < pagesFromSite \
                    and len(postList) > 0 and (not newThread):
                forumURL.pages += 1
            if forumURL.pagesTotal < pagesFromSite:
                forumURL.pagesTotal = pagesFromSite
            site = dbcontrol.getSiteByID(forumURL.site_id)
            session = dbcontrol.getSession()
            countTrue = 0
            countFalse = 0
            url_split = urlsplit(forumURL.url)

            for post in postList:

                shortName = site.short
                userId = shortName + post.userId
                user = post.user
                forumUser = ForumUser(userId, user, site.id)
                try:
                    userId = dbcontrol.insertForumUserToDB(forumUser, session)
                except SQLAlchemyError as e:
                    # logger.exception('failed to SQL query ' + e)
                    pass
                topicId = shortName + post.postId
                topicURL=URLProcessor.makeTopicURL(forumURL.site_id,
                                                   post.postId, forumURL.url)

                topic = Topic(topicId, userId,
                              converImgUrls(url_split, post.postContent), forumURL.id,
                              post.dateTime,
                              datetime.datetime.utcnow().replace(tzinfo=pytz.timezone('Europe/Minsk')),
                              topicURL)

                # print(topic.topicText)

                try:
                    if dbcontrol.insertTopicToDB(topic, session):
                        countTrue += 1
                    else:
                        countFalse += 1
                except SQLAlchemyError as e:
                    # print('failed to SQL query ' + str(e))
                    pass

            # logger.info("inserted %d topics of %d" % (countTrue, len(postList)))
            # print('!!!!!!!!! %d' % (countTrue+countFalse))
            if len(postList) == (countTrue + countFalse):
                try:
                    dbcontrol.updateForumEntry(forumURL, session)
                    # print('urlEntryUpdated')
                except SQLAlchemyError as e:
                    print('failed to to SQL query ' + str(e))
                    pass

            session.close()
            time.sleep(timeDelay)

        else:
            time.sleep(timeDelay)
            continue


def main():
    # logging.config.dictConfig(DICTLOGCONFIG)
    # logger = logging.getLogger("parser")
    # loggerSQL = logging.getLogger("sqlalchemy")

    # logger.info('Parser Started')
    global newThread
    countIter = 0
    while True:
        countIter += 1
        dbcontrol = DBcontrolller(DB_STRING, encoding='utf8', echo=False)
        ioloop = asyncio.get_event_loop()

        fetchParser(dbcontrol, ioloop)
        newThread = False
        dbcontrol.dispose()
        dbcontrol.clearMappers()
        time.sleep(5)


        if countIter > 50:
            countIter = 0
            fileName = DICTLOGCONFIG['handlers']['fileHandler']['filename']
            linesToWrite = []
            countLines = 0
            with open(fileName, 'r') as f:
                lines = f.readlines()
                for line in list(reversed(lines)):
                    linesToWrite.append(line)
                    countLines += 1
                    if countLines > 1000: break
            with open(fileName, 'w') as f:
                for line in list(reversed(linesToWrite)):
                    f.write(line)

if __name__ == "__main__":
    main()