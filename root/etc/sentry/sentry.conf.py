# This file is just Python, with a touch of Django which means
# you can inherit and tweak settings to your hearts content.

# For Docker, the following environment variables are supported:
#  SENTRY_POSTGRES_HOST
#  SENTRY_POSTGRES_PORT
#  SENTRY_DB_NAME
#  SENTRY_DB_USER
#  SENTRY_DB_PASSWORD
#  SENTRY_RABBITMQ_HOST
#  SENTRY_RABBITMQ_USERNAME
#  SENTRY_RABBITMQ_PASSWORD
#  SENTRY_RABBITMQ_VHOST
#  SENTRY_REDIS_HOST
#  SENTRY_REDIS_PASSWORD
#  SENTRY_REDIS_PORT
#  SENTRY_REDIS_DB
#  SENTRY_MEMCACHED_HOST
#  SENTRY_MEMCACHED_PORT
#  SENTRY_FILESTORE_DIR
#  SENTRY_SERVER_EMAIL
#  SENTRY_EMAIL_HOST
#  SENTRY_EMAIL_PORT
#  SENTRY_EMAIL_USER
#  SENTRY_EMAIL_PASSWORD
#  SENTRY_EMAIL_USE_TLS
#  SENTRY_ENABLE_EMAIL_REPLIES
#  SENTRY_SMTP_HOSTNAME
#  SENTRY_MAILGUN_API_KEY
#  SENTRY_SINGLE_ORGANIZATION
#  SENTRY_SECRET_KEY
#  SLACK_CLIENT_ID
#  SLACK_CLIENT_SECRET
#  SLACK_VERIFICATION_TOKEN
#  GITHUB_APP_ID
#  GITHUB_API_SECRET
#  BITBUCKET_CONSUMER_KEY
#  BITBUCKET_CONSUMER_SECRET

from sentry.conf.server import *

import os
import os.path

CONF_ROOT = os.path.dirname(__file__)

postgres = env('SENTRY_POSTGRES_HOST')
if postgres:
    DATABASES = {
        'default': {
            'ENGINE': 'sentry.db.postgres',
            'HOST': postgres,
            'NAME': (env('SENTRY_DB_NAME') or 'postgres'),
            'USER': (env('SENTRY_DB_USER') or 'postgres'),
            'PASSWORD': (env('SENTRY_DB_PASSWORD') or ''),
            'PORT': (env('SENTRY_POSTGRES_PORT') or '5432'),
            'OPTIONS': {
                'autocommit': True,
            },
        },
    }
else:
    raise Exception('Error: SENTRY_POSTGRES_HOST is undefined')

# You should not change this setting after your database has been created
# unless you have altered all schemas first
SENTRY_USE_BIG_INTS = True

# If you're expecting any kind of real traffic on Sentry, we highly recommend
# configuring the CACHES and Redis settings

###########
# General #
###########

# Instruct Sentry that this install intends to be run by a single organization
# and thus various UI optimizations should be enabled.
SENTRY_SINGLE_ORGANIZATION = env('SENTRY_SINGLE_ORGANIZATION', True)

#########
# Redis #
#########

# Generic Redis configuration used as defaults for various things including:
# Buffers, Quotas, TSDB

redis = env('SENTRY_REDIS_HOST')
if redis:
    redis_password = env('SENTRY_REDIS_PASSWORD') or ''
    redis_port = env('SENTRY_REDIS_PORT') or '6379'
    redis_db = env('SENTRY_REDIS_DB') or '0'
    SENTRY_OPTIONS.update({
        'redis.clusters': {
            'default': {
                'hosts': {
                    0: {
                        'host': redis,
                        'password': redis_password,
                        'port': redis_port,
                        'db': redis_db,
                    },
                },
            },
        },
    })
else:
    raise Exception('Error: SENTRY_REDIS_HOST is undefined')

#########
# Cache #
#########

# Sentry currently utilizes two separate mechanisms. While CACHES is not a
# requirement, it will optimize several high throughput patterns.

memcached = env('SENTRY_MEMCACHED_HOST')
if memcached:
    memcached_port = (env('SENTRY_MEMCACHED_PORT') or '11211')
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': [memcached + ':' + memcached_port],
            'TIMEOUT': 3600,
        }
    }

# A primary cache is required for things such as processing events
SENTRY_CACHE = 'sentry.cache.redis.RedisCache'

#########
# Queue #
#########

# See https://docs.getsentry.com/on-premise/server/queue/ for more
# information on configuring your queue broker and workers. Sentry relies
# on a Python framework called Celery to manage queues.

rabbitmq = env('SENTRY_RABBITMQ_HOST')
if rabbitmq:
    BROKER_URL = ('amqp://' + (env('SENTRY_RABBITMQ_USERNAME') or 'guest') +
                  ':' + (env('SENTRY_RABBITMQ_PASSWORD') or 'guest') + '@' +
                  rabbitmq + '/' + (env('SENTRY_RABBITMQ_VHOST') or '/'))
else:
    BROKER_URL = 'redis://:' + redis_password + '@' + redis + ':' + redis_port + '/' + redis_db

###############
# Rate Limits #
###############

# Rate limits apply to notification handlers and are enforced per-project
# automatically.

SENTRY_RATELIMITER = 'sentry.ratelimits.redis.RedisRateLimiter'

##################
# Update Buffers #
##################

# Buffers (combined with queueing) act as an intermediate layer between the
# database and the storage API. They will greatly improve efficiency on large
# numbers of the same events being sent to the API in a short amount of time.
# (read: if you send any kind of real data to Sentry, you should enable buffers)

SENTRY_BUFFER = 'sentry.buffer.redis.RedisBuffer'

##########
# Quotas #
##########

# Quotas allow you to rate limit individual projects or the Sentry install as
# a whole.

SENTRY_QUOTAS = 'sentry.quotas.redis.RedisQuota'

########
# TSDB #
########

# The TSDB is used for building charts as well as making things like per-rate
# alerts possible.

SENTRY_TSDB = 'sentry.tsdb.redis.RedisTSDB'

###########
# Digests #
###########

# The digest backend powers notification summaries.

SENTRY_DIGESTS = 'sentry.digests.backends.redis.RedisBackend'

################
# File storage #
################

# Uploaded media uses these `filestore` settings. The available
# backends are either `filesystem` or `s3`.

if env('SENTRY_FILESTORE_DIR'):
    SENTRY_OPTIONS['filestore.backend'] = 'filesystem'
    SENTRY_OPTIONS['filestore.options'] = {
        'location': env('SENTRY_FILESTORE_DIR')
    }

##############
# Web Server #
##############

# If you're using a reverse SSL proxy, you should enable the X-Forwarded-Proto
# header and set `SENTRY_USE_SSL=1`

SENTRY_WEB_HOST = '0.0.0.0'
SENTRY_WEB_PORT = 9000
SENTRY_WEB_OPTIONS = {
    'workers': 5  # the number of web workers
}

if env('SENTRY_USE_SSL'):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

###############
# Mail Server #
###############

mail_host = env('SENTRY_EMAIL_HOST')
if mail_host:
    SENTRY_OPTIONS['mail.host'] = mail_host
    SENTRY_OPTIONS['mail.backend'] = 'smtp'
    SENTRY_OPTIONS['mail.password'] = env('SENTRY_EMAIL_PASSWORD') or ''
    SENTRY_OPTIONS['mail.username'] = env('SENTRY_EMAIL_USER') or ''
    SENTRY_OPTIONS['mail.port'] = int(env('SENTRY_EMAIL_PORT') or 25)
    SENTRY_OPTIONS['mail.use-tls'] = env('SENTRY_EMAIL_USE_TLS', False)
else:
    SENTRY_OPTIONS['mail.backend'] = 'dummy'

# The email address to send on behalf of
SENTRY_OPTIONS['mail.from'] = env('SENTRY_SERVER_EMAIL') or 'root@localhost'

SENTRY_OPTIONS['mail.enable-replies'] = env('SENTRY_ENABLE_EMAIL_REPLIES',
                                            False)

if SENTRY_OPTIONS['mail.enable-replies']:
    SENTRY_OPTIONS['mail.reply-hostname'] = env('SENTRY_SMTP_HOSTNAME') or ''

#####################
# SLACK INTEGRATION #
#####################

slack = env('SLACK_CLIENT_ID') and env('SLACK_CLIENT_SECRET')
if slack:
    SENTRY_OPTIONS['slack.client-id'] = env('SLACK_CLIENT_ID')
    SENTRY_OPTIONS['slack.client-secret'] = env('SLACK_CLIENT_SECRET')
    SENTRY_OPTIONS['slack.verification-token'] = env(
        'SLACK_VERIFICATION_TOKEN') or ''

# if 'GITHUB_APP_ID' in os.environ:
#     GITHUB_EXTENDED_PERMISSIONS = ['repo']
#     GITHUB_APP_ID = env('GITHUB_APP_ID')
#     GITHUB_API_SECRET = env('GITHUB_API_SECRET')

# if 'BITBUCKET_CONSUMER_KEY' in os.environ:
#     BITBUCKET_CONSUMER_KEY = env('BITBUCKET_CONSUMER_KEY')
#     BITBUCKET_CONSUMER_SECRET = env('BITBUCKET_CONSUMER_SECRET')

##
# LDAP Auth
##

ldap_server = env('AUTH_LDAP_SERVER_URI')
if ldap_server:
    import ldap
    from django_auth_ldap.config import LDAPSearch, GroupOfUniqueNamesType, GroupOfNamesType

    AUTH_LDAP_SERVER_URI = ldap_server

    if env('AUTH_LDAP_BIND_DN'):
        AUTH_LDAP_BIND_DN = env('AUTH_LDAP_BIND_DN')
    else:
        raise Exception('Error: AUTH_LDAP_BIND_DN is undefined')

    if env('AUTH_LDAP_BIND_PASSWORD'):
        AUTH_LDAP_BIND_PASSWORD = env('AUTH_LDAP_BIND_PASSWORD')
    else:
        raise Exception('Error: AUTH_LDAP_BIND_PASSWORD is undefined')

    if env('AUTH_LDAP_DEFAULT_SENTRY_ORGANIZATION'):
        AUTH_LDAP_DEFAULT_SENTRY_ORGANIZATION = env(
            'AUTH_LDAP_DEFAULT_SENTRY_ORGANIZATION')
    else:
        raise Exception(
            'Error: AUTH_LDAP_DEFAULT_SENTRY_ORGANIZATION is undefined')

    if env('AUTH_LDAP_DEFAULT_EMAIL_DOMAIN'):
        AUTH_LDAP_DEFAULT_EMAIL_DOMAIN = env('AUTH_LDAP_DEFAULT_EMAIL_DOMAIN')
    else:
        raise Exception('Error: AUTH_LDAP_DEFAULT_EMAIL_DOMAIN is undefined')

    user_container = env('AUTH_LDAP_USER_CONTAINER')
    if user_container:
        AUTH_LDAP_USER_SEARCH = LDAPSearch(
            user_container,
            ldap.SCOPE_SUBTREE,
            '(sAMAccountName=%(user)s)',
        )
        AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
            user_container,
            ldap.SCOPE_SUBTREE,
            '(objectClass=group)',
        )
    else:
        raise Exception('Error: AUTH_LDAP_USER_CONTAINER is undefined')

    AUTH_LDAP_USER_ATTR_MAP = {
        'first_name': 'givenName',
        'last_name': 'sn',
        'email': 'mail',
        'name': 'displayName',
    }

    AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()
    AUTH_LDAP_DENY_GROUP = None
    AUTH_LDAP_MIRROR_GROUPS = False  # does not work with Sentry
    AUTH_LDAP_FIND_GROUP_PERMS = False
    AUTH_LDAP_CACHE_GROUPS = False
    AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600
    AUTH_LDAP_SENTRY_ORGANIZATION_ROLE_TYPE = 'member'
    AUTH_LDAP_SENTRY_ORGANIZATION_GLOBAL_ACCESS = False
    AUTH_LDAP_SENTRY_SUBSCRIBE_BY_DEFAULT = False
    AUTHENTICATION_BACKENDS = AUTHENTICATION_BACKENDS + (
        'sentry_ldap_auth.backend.SentryLdapBackend', )

# If this value ever becomes compromised, it's important to regenerate your
# SENTRY_SECRET_KEY. Changing this value will result in all current sessions
# being invalidated.

secret_key = env('SENTRY_SECRET_KEY')
if secret_key:
    SENTRY_OPTIONS['system.secret-key'] = secret_key
else:
    raise Exception('''Error: SENTRY_SECRET_KEY is undefined, run
                       `sentry config generate-secret-key`''')
