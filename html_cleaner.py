import argparse
import codecs
import os
import re
import multiprocessing
import logging
from typing import Tuple
from bs4 import BeautifulSoup


L = logging.getLogger(__name__)


def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+', help='files')
    ap.add_argument('--processor', type=int, default=1, help='number of process')
    ap.add_argument('--encoding', help='fallback to this encoding')
    ap.add_argument('--no-script', action='store_true', help='remove js')
    ap.add_argument('-r', '--recursive', action='store_true', help='recusive into directory')
    ap.add_argument('-p', '--pattern', default=r'.+\.html?$', help='glob pattern')
    return ap.parse_args()


def read_file(filename, encoding=None) -> Tuple[str, str]:
    with open(filename, 'rb') as fp:
        data = fp.read()

    guesses = ['utf8', 'gb18030']
    if encoding is not None:
        if encoding in guesses:
            guesses.remove(encoding)
        guesses.insert(0, encoding)

    for guess in guesses:
        try:
            return data.decode(guess), guess
        except UnicodeDecodeError:
            pass

    if encoding is not None:
        with open(filename, 'rt', encoding=encoding, errors='warn_error') as fp:
            return fp.read(), encoding
    else:
        raise Exception('Unknown encoding: ' + filename)


def consumer(args, filename):
    try:
        return do_file(args, filename)
    except Exception:
        L.exception('do_file: %s', filename)


PRESERVE_CHARS = \
    '\u3000'    # full width space
PRESERVE_PLACEHOLDER = ''.join(chr(x) for x in range(0x10FFFD, 0x10FFFD - len(PRESERVE_CHARS), -1))
PRESERVE_TRANS = str.maketrans(PRESERVE_CHARS, PRESERVE_PLACEHOLDER)
PRESERVE_RECOVER = str.maketrans(PRESERVE_PLACEHOLDER, PRESERVE_CHARS)


def do_file(args, filename):
    L.debug('consume file: %s', filename)

    # read file
    content, encoding = read_file(filename, encoding=args.encoding)
    L.debug('file read as %s: %s', encoding, filename)

    # translate preserved chars
    content = content.translate(PRESERVE_TRANS)

    # parse html
    # 'lxml', 'html.parser'
    soup = BeautifulSoup(content, 'html5lib')

    # clean up
    if args.no_script:
        for node in soup.find_all('script'):
            node.extract()

    # output
    out = soup.prettify()

    # recover preserved chars
    out = out.translate(PRESERVE_RECOVER)

    # write file
    if out != content:
        with open(filename, 'wt') as fp:
            fp.write(out)
        L.debug('file written: %s', filename)
    else:
        L.debug('file already clean: %s', filename)


def producer(args, pool: multiprocessing.Pool, filename):
    L.debug('produce: %s', filename)

    if not os.path.isdir(filename):
        pool.apply_async(consumer, args=(args, filename))
        return

    # recursive into dirs
    if os.path.isdir(filename):
        if not args.recursive:
            raise Exception('file is directory: ' + filename)
        for root, dirs, files in os.walk(filename):
            for subfile in files:
                if re.match(args.pattern, subfile, re.IGNORECASE) is None:
                    continue

                subpath = os.path.join(root, subfile)
                L.debug('produce: %s', subpath)
                pool.apply_async(consumer, args=(args, subpath))


def on_codecs_error(exc):
    L.warning('decode error: %s', exc)
    return codecs.replace_errors(exc)


def init():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)5s %(asctime)s.%(msecs)03d [%(processName)s:%(process)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    codecs.register_error('warn_error', on_codecs_error)


def main():
    init()

    args = get_args()

    pool = multiprocessing.Pool(processes=args.processor, initializer=init)
    for filename in args.files:
        producer(args, pool, filename)
    L.debug('producer done')

    pool.close()
    pool.join()
    L.debug('pool joined')


if __name__ == '__main__':
    main()
