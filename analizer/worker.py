import multiprocessing as mp
import time
import sqlite3
import os
from .parser import TokensParser

schema = """
CREATE TABLE if not exists `files` (
    `id`    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `filename`  TEXT NOT NULL,
    `fraud` INTEGER NOT NULL,
    `loathing`  REAL NOT NULL
);
"""

class Worker(mp.Process):
    """Main worker
    принимает данные на обработку, после передает в 
    
    Attributes:
        result_queue (TYPE): Description
        task_queue (TYPE): Description
    """
    def __init__(self, task_queue, result_queue):
        mp.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.done = 0

    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                # Poison pill means shutdown
                print ('%s: Exiting, works done %d' % (proc_name, self.done))
                self.task_queue.task_done()
                break
            try:
                self.done += 1
                fraud, loathing = next_task()
                self.result_queue.put(
                    {
                        'filename': next_task.getFileName(),
                        'fraud': fraud,
                        'loathing': loathing
                    }
                )
            except:
                print ('The task "%s" failed' % next_task)

            self.task_queue.task_done()
        return


class SQLiteWorker(mp.Process):
    def __init__(self, sqlite_path, task_queue):
        mp.Process.__init__(self)
        self.task_queue = task_queue
        self.conn = sqlite3.connect(sqlite_path)
        self.conn.execute(schema)
        self.conn.execute("DELETE from files")
        self.conn.commit()
        self.done = 0

    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                print ('%s: Exiting, works done %d' % (proc_name, self.done))
                self.task_queue.task_done()
                break
            self.done += 1
            self.add(next_task['filename'], next_task['fraud'],
                     next_task['loathing'])
            self.task_queue.task_done()
        return

    def add(self, filename, fraud, loathing):
        self.conn.execute(
            "INSERT INTO files ('filename', 'fraud', 'loathing') \
            VALUES ('{0}', '{1}', '{2}')".
            format(filename, fraud, loathing))
        #print ("add %s"%filename)
        self.conn.commit()


class FileProcessor(object):

    def __init__(self, filename, parser):
        self.filename = filename
        self.parser = parser

    def __call__(self):
        text = ''
        with open(self.filename, 'r') as f:
            text = ''.join(line.rstrip() for line in f)
        return self.parser.analize(text)

    def __str__(self):
        return 'Anilizing file %s' % (self.filename)

    def getFileName(self):
        return self.filename


def checkFiles(path):
    if not os.path.isfile(path):
        print ("The path %s isn't file" % path)
        return False
    if os.path.getsize(path) <= 0:
        print ('File %s has zero size' % path)
        return False
    return True
