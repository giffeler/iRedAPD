from unittest.mock import patch

from conftest import settings

import tools
from libs import utils
from tests import utils as test_utils


def test_engine_tcp_tls_unchanged():
    settings.vmail_db_socket = ''
    settings.vmail_db_use_ssl = True
    with patch.object(utils, 'create_engine') as create:
        utils.create_db_engine('vmail')
    assert create.call_args.args[0].endswith('?charset=utf8&ssl_verify_cert=False')
    assert 'connect_args' not in create.call_args.kwargs


def test_engine_socket_credentials_are_not_url_interpolated():
    settings.vmail_db_password = 'a@b:/?#%'
    with patch.object(utils, 'create_engine') as create:
        utils.create_db_engine('vmail')
    assert create.call_args.args[0].password == 'a@b:/?#%'
    assert create.call_args.kwargs['connect_args'] == {'unix_socket': settings.vmail_db_socket}


def test_postgres_factories_receive_no_mysql_socket():
    settings.backend = 'pgsql'
    settings.SQL_DB_DRIVER = 'psycopg2'
    with patch.object(utils, 'create_engine') as create:
        utils.create_db_engine('vmail')
    assert create.call_args.args[0].startswith('postgresql+psycopg2://')
    assert 'connect_args' not in create.call_args.kwargs
    with patch.object(tools, 'sql_dbn', 'postgres'):
        for make in [tools.get_db_conn, test_utils.get_db_conn]:
            conn = make('vmail')
            assert 'unix_socket' not in conn.keywords


def test_tools_tcp_tls_unchanged():
    settings.vmail_db_socket = ''
    settings.vmail_db_use_ssl = True
    assert tools.get_db_conn('vmail').keywords['ssl'] == {'ssl': True}
