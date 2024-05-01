#!/usr/bin/env python3
import contextlib
import multiprocessing
import os
import time

from lxml import html
import urllib.request
import urllib.error


def cachedFetch(url, localPath, verbose=True):
    if os.path.exists(localPath):
        return 'Cached ' + url
    with contextlib.suppress(OSError):
        os.makedirs(os.path.split(localPath)[0])
    if verbose:
        print('Fetching %s ...' % url)
    finished = False
    sleepTime = 1
    data = None
    while not (finished):
        try:
            response = urllib.request.urlopen(url)
            data = response.read()
            finished = True
        except urllib.error.URLError as e:
            time.sleep(sleepTime)
            sleepTime *= 2
            print(
                f'Fetching hit a snag fetching the page, retrying due to: {e.reason}'
            )
    if data:
        with open(localPath, 'wb') as f:
            f.write(data)
    return 'Fetched ' + url


def cachedRead(url, localPath):
    cachedFetch(url, localPath)
    return open(localPath, 'rb')


def mpFetch(args):
    return cachedFetch(*args, verbose=False)


def iterateAllPageURLs():
    with cachedRead('http://www.spec.org/cpu95/results/cpu95.html',
                    os.path.join('scraped', 'cpu95.html')) as f:
        doc = html.parse(f)
        print('Scanning cpu95.html ...')
    for elem, attr, link, pos in doc.getroot().iterlinks():
        if link.lower().endswith('.asc') or link.lower().endswith('.html'):
            yield 'http://www.spec.org' + link, os.path.join(
                'scraped', 'cpu95',
                link.split('/')[-1])

    with cachedRead('http://www.spec.org/cpu2000/results/cpu2000.html',
                    os.path.join('scraped', 'cpu2000.html')) as f:
        print('Scanning cpu2000.html ...')
        doc = html.parse(f)
    for elem, attr, link, pos in doc.getroot().iterlinks():
        if link.lower().endswith('.asc'):
            yield 'http://www.spec.org/cpu2000/results/' + link, os.path.join(
                'scraped', 'cpu2000',
                link.split('/')[-1])

    with cachedRead('http://www.spec.org/cpu2006/results/cpu2006.html',
                    os.path.join('scraped', 'cpu2006.html')) as f:
        print('Scanning cpu2006.html ...')
        doc = html.parse(f)
    for elem, attr, link, pos in doc.getroot().iterlinks():
        if link.lower().endswith('.txt'):
            yield 'http://www.spec.org/cpu2006/results/' + link, os.path.join(
                'scraped', 'cpu2006',
                link.split('/')[-1])

    with cachedRead('http://www.spec.org/cpu2017/results/cpu2017.html',
                    os.path.join('scraped', 'cpu2017.html')) as f:
        print('Scanning cpu2017.html ...')
        doc = html.parse(f)
    for elem, attr, link, pos in doc.getroot().iterlinks():
        if link.lower().endswith('.txt'):
            yield 'http://www.spec.org/cpu2017/results/' + link, os.path.join(
                'scraped', 'cpu2017',
                link.split('/')[-1])


if __name__ == '__main__':
    allPageURLs = list(iterateAllPageURLs())
    pool = multiprocessing.Pool(20)
    for i, result in enumerate(pool.imap_unordered(mpFetch, allPageURLs)):
        print('%d/%d ... %s' % (i + 1, len(allPageURLs), result))
