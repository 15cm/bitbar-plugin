#!/usr/bin/env PYTHONIOENCODING=UTF-8 your_path_to_python3
# -*- coding: utf-8 -*-

# Bitbar Metadata
# <bitbar.title>Aria2</bitbar.title>
# <bitbar.version>v1.0</bitbar.version>
# <bitbar.author>sinkerine</bitbar.author>
# <bitbar.author.github>15cm</bitbar.author.github>
# <bitbar.desc>Monitor Aria2 Tasks</bitbar.desc>
# <bitbar.dependencies>python3</bitbar.dependencies>
# <bitbar.abouturl>https://github.com/15cm/bitbar-plugin/tree/master/aria2</bitbar.abouturl>

from aria2 import Aria2
import os

host = 'localhost'
port = 6800
secret = 'your token'
title_format = '💻 ⬇️' + '%s/s'

def bytes_to_readable(speed_in_bytes, precision = 1):
    width = 5
    display_format = '%{0}.{1}f %s'.format(width, precision)
    if(speed_in_bytes > 1e9):
        return display_format % (speed_in_bytes / 1e9, 'GB')
    elif(speed_in_bytes > 1e6):
        return display_format % (speed_in_bytes / 1e6, 'MB')
    else:
        return display_format % (speed_in_bytes / 1e3, 'KB')

class Task:
    def __init__(self, type, path, size, completed_size, dl_speed):
        self.type = type
        self.name = os.path.basename(path)
        self.size = size
        self.percentage = completed_size / size
        self.dl_speed = dl_speed

    def __str__(self):
        stype_dict = {
            'active': '📶',
            'waiting': '🕒',
            'paused': '⏸',
            'complete': '✅'
        }
        name_width = 40
        progress_bar_width = 20
        progress_bar_length = int(self.percentage * progress_bar_width)

        sname = '%-{0}.{0}s'.format(name_width) % self.name
        # Padding task name with '...' if it is too long
        if len(self.name) > name_width:
            sname = sname[0:-3] + '...'
        stype = stype_dict[self.type] if self.type in stype_dict else '❎'
        ssize = bytes_to_readable(self.size)
        sprogress = ('[%-{0}s]%-5.1f'.format(progress_bar_width) % \
                    ('=' * progress_bar_length, self.percentage * 100)) + '%'
        stask = '%s %s %s %s' % (sname, stype, ssize, sprogress)
        if self.type == 'active':
            sspeed = '  ⬇️ %s/s' % bytes_to_readable(self.dl_speed)
            stask += sspeed
        return stask

if __name__ == '__main__':
    aria2 = Aria2(host, port, secret)
    global_stat = aria2.getGlobalStat()
    [active_tasks, waiting_tasks, stopped_tasks] = [[Task(t['status'], t['files'][0]['path'],
                              int(t['totalLength']), int(t['completedLength']),
                                                                      int(t['downloadSpeed'])) for t in t_list if 'files' in t and t['files'] and int(t['totalLength']) > 0]
                        for t_list in (aria2.tellActive(), aria2.tellWaiting(), aria2.tellStopped())]
    print(title_format % bytes_to_readable(int(global_stat['downloadSpeed'])) + '|')
    print('---')
    print('Active Tasks|color="#1b42eb"')
    for task in active_tasks:
        print('%s|font="Monaco"' % task)
    print('---')
    print('---')
    print('Other Tasks|color="#7553fc"')
    print('---')
    for task in waiting_tasks:
        print('%s|font="Monaco"' % task)
    for task in stopped_tasks:
        print('%s|font="Monaco"' % task)
