from django.core.management.base import BaseCommand, CommandError
from forumTopics.models import  Topics, ForumUsers
import datetime
import logging
import logging.config
import time

DICTLOGCONFIG={
"version":1,
        "handlers":{
            "fileHandler":{
                "class":"logging.FileHandler",
                "formatter":"myFormatter",
                "filename":"/home/odo/djhelpdesk/forumTopics/djhelpdeskclearDB.log"
            }
        },
        "loggers":{
            "clearDB":{
                "handlers":["fileHandler"],
                "level":"INFO",
            }
        },
        "formatters":{
            "myFormatter":{
                "format":"[%(asctime)s] - %(levelname)s - %(message)s"
            }
        }
}

class Command(BaseCommand):

    def handle(self, *args, **options):
        logging.config.dictConfig(DICTLOGCONFIG)
        logger = logging.getLogger("clearDB")
        today = datetime.date.today()
        yearAgo = today
        yearAgo = yearAgo.replace(year=yearAgo.year - 1)
        deleteCandidates = Topics.objects.filter(datePost__datetz_lt=yearAgo).defer('id', 'user_id')
        logger.info("%d candidates for deletion" % (len(deleteCandidates)))
        count = 0;
        for topic in deleteCandidates:
            userCount = Topics.objects.filter(user__id=topic.user_id).count()
            if userCount == 1:
                count += 1
                ForumUsers.objects.filter(id=topic.user_id).delete()
            print(topic.id)
            Topics.objects.filter(id=topic.id).delete()
        logger.info("delete %d topics, %d forumUsers" % (len(deleteCandidates), count))

        fileName = DICTLOGCONFIG['handlers']['fileHandler']['filename']
        linesToWrite = []
        countLines = 0
        with open(fileName, 'r') as f:
            lines = f.readlines()
            for line in list(reversed(lines)):
                linesToWrite.append(line)
                countLines += 1
                if countLines > 100: break
        with open(fileName, 'w') as f:
            for line in list(reversed(linesToWrite)):
                f.write(line)




