# -*- coding: utf-8 -*-
import multiprocessing as mp
import sys
import os
from analizer import *

WORKER_NUMBERS = 4
SQLITE_PATH = '/tmp/db.sql'


def run_proc(path):
    # Establish communication queues
    tasks = mp.JoinableQueue()
    results = mp.JoinableQueue()

    symbols_eng_rus = [
        ('a', 'а'), ('A', 'А'), ('B', 'В'), ('c', 'с'),
        ('C', 'С'), ('e', 'е'), ('E', 'Е'), ('H', 'Н'), ('k', 'к'),
        ('K', 'К'), ('p', 'р'), ('P', 'Р'), ('o', 'о'), ('O', 'О'),
        ('M', 'M'), ('T', 'Т'), ('x', 'х'), ('X', 'Х'), ('y', 'у')
    ]
    p_rus = TokensParser('russian', symbols_eng_rus)
    p_rus.addSymbolMap('english', [(b, a) for a, b in symbols_eng_rus])

    # Start consumers
    num_consumers = WORKER_NUMBERS - 1
    print ('Creating %d consumers' % num_consumers)
    processes = [Worker(tasks, results)
                 for i in range(num_consumers)] + \
                [SQLiteWorker(SQLITE_PATH, results)]
    for p in processes:
        p.start()

    # Enqueue jobs
    files = ['%s%s' % (path, f) for f in os.listdir(path)]
    files = [f for f in files if checkFiles(f)]

    # tasks.put(FileProcessor('../text_files/0001.txt', p_rus))
    # tasks.put(FileProcessor('../text_files/0027.txt', p_rus))
    for f in files:
        tasks.put(FileProcessor(f, p_rus))

    for i in range(num_consumers):
        tasks.put(None)

    # Wait for all of the tasks to finish
    tasks.join()
    results.join()

    # Stop the sql process
    results.put(None)


if __name__ == '__main__':
    run_proc('text_files/')
    sys.exit(0)
