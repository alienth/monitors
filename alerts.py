#!/usr/bin/python

import ConfigParser
import logging
import logging.handlers
import os
import sys
import time

import wessex

__all__ = ["harold", "config"]

harold = None
config = None

def init(config_path='production.ini'):
    global config, harold
    config = load_config(path=config_path)
    if config.has_section('logging'):
        configure_logging(config)
    harold = get_harold(config)

def load_config(path='production.ini'):
    config = ConfigParser.RawConfigParser()
    config.read([path])
    return config

def get_harold(config):
    harold_host = config.get('harold', 'host')
    harold_port = config.getint('harold', 'port')
    harold_secret = config.get('harold', 'secret')
    return wessex.Harold(
        host=harold_host, port=harold_port, secret=harold_secret)

class StreamLoggingFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        timestamp = time.strftime(datefmt)
        return timestamp % dict(ms=(1000 * record.created) % 1000)

def _get_logging_handler(config):
    mode = config.get('logging', 'mode')
    if mode == 'file':
        return logging.FileHandler(config.get('logging', 'file'))
    elif mode == 'stderr':
        return logging.StreamHandler()
    elif mode == 'syslog':
        return logging.handlers.SysLogHandler(
            config.get('logging', 'syslog_addr'))
    else:
        raise ValueError('unsupported logging mode: %r' % mode)

def _get_logging_formatter(config):
    mode = config.get('logging', 'mode')
    if mode == 'syslog':
        app_name = os.path.basename(sys.argv[0])
        return logging.Formatter(
            '%s: [%%(levelname)s] %%(message)s' % app_name)
    else:
        return StreamLoggingFormatter(
            '%(levelname).1s%(asctime)s: %(message)s',
            '%m%d %H:%M:%S.%%(ms)03d')

def _get_logging_level(config):
    if config.has_option('logging', 'level'):
        return config.get('logging', 'level')
    else:
        return logging.INFO

def configure_logging(config):
    ch = _get_logging_handler(config)
    ch.setFormatter(_get_logging_formatter(config))
    logger = logging.getLogger()
    logger.setLevel(_get_logging_level(config))
    logger.addHandler(ch)
    return logger
