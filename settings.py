from subprocess import getoutput
YC_TOKEN = getoutput('yc iam create-token')
YC_CLOUD_ID = getoutput('yc config get cloud-id')
YC_FOLDER_ID = getoutput('yc config get folder-id')

LogConfig = {
    'version': 1,
    'formatters': {
        'details': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s::%(name)s::%(levelname)s::%(message)s',
            'incremental': True,
        },
    },
    'handlers': {
        'rotate': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'root.log',
            'mode': 'w',
            'level': 'DEBUG',
            'maxBytes': 204800,
            'backupCount': 3,
            'formatter': 'details',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'details',
        },
    },
    'loggers': {
        '': {
            'level': 'NOTSET',
            'handlers': ['rotate', 'console'],
        },
    }
}