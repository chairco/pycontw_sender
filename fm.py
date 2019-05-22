#-*- coding: utf-8 -*-
import csv
import logging

from functools import wraps

logger = logging.getLogger(__name__)


def filters(f=None):
    def deco(func):
        @wraps(func)
        def new_function(*args, **kwargs):
            talks = func(*args, **kwargs)
            if f is not None:
                ignore = [t['id'] for t in read_csv(f)]
                logger.info(f"Ignore talks: {len(ignore)}, f is {f}")
            else:
                ignore = []
                logger.info(f"No ignore tals, f is {f}")
            talks = [talk for talk in talks if talk['id'] not in ignore]
            logger.info(f"Totall talk is {len(talks)}")
            return talks
        return new_function
    return deco


def read_csv(f):
    """read csv file
    """
    # because is text file so need use 'rt' open not 'rb'
    with open(f, 'rt') as csvfile:
        # save to a list
        talks = [talk for talk in csv.DictReader(csvfile)]

    return talks


# test
@filters('TalkProposal-2019-05-21.csv')
def get_talks():
    f = 'TalkProposal-2019-05-22.csv'
    talks = read_csv(f)
    return talks


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    f = get_talks()

