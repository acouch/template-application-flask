import logging  # noqa: B1

from sqlalchemy import text

import api.adapters.db as db
from api.adapters.db.client import get_connection_parameters, make_connection_uri, verify_ssl
from api.adapters.db.config import DbConfig, get_db_config


class DummyConnectionInfo:
    def __init__(self, ssl_in_use, attributes):
        self.ssl_in_use = ssl_in_use
        self.attributes = attributes
        self.ssl_attribute_names = tuple(attributes.keys())

    def ssl_attribute(self, name):
        return self.attributes[name]


def test_verify_ssl(caplog):
    caplog.set_level(logging.INFO)  # noqa: B1

    conn_info = DummyConnectionInfo(True, {"protocol": "ABCv3", "key_bits": "64", "cipher": "XYZ"})
    verify_ssl(conn_info)

    assert caplog.messages == [
        "database connection is using SSL: protocol ABCv3, key_bits 64, cipher XYZ"
    ]
    assert caplog.records[0].levelname == "INFO"


def test_verify_ssl_not_in_use(caplog):
    caplog.set_level(logging.INFO)  # noqa: B1

    conn_info = DummyConnectionInfo(False, {})
    verify_ssl(conn_info)

    assert caplog.messages == ["database connection is not using SSL"]
    assert caplog.records[0].levelname == "WARNING"


def test_make_connection_uri():
    assert (
        make_connection_uri(
            DbConfig(
                host="localhost",
                name="dbname",
                username="foo",
                password="bar",
                db_schema="public",
                port="5432",
            )
        )
        == "postgresql://foo:bar@localhost:5432/dbname?options=-csearch_path=public"
    )

    assert (
        make_connection_uri(
            DbConfig(
                host="localhost",
                name="dbname",
                username="foo",
                password=None,
                db_schema="public",
                port="5432",
            )
        )
        == "postgresql://foo@localhost:5432/dbname?options=-csearch_path=public"
    )


def test_get_connection_parameters(monkeypatch):
    db_config = get_db_config()
    conn_params = get_connection_parameters(db_config)

    assert conn_params == dict(
        host=db_config.host,
        dbname=db_config.name,
        user=db_config.username,
        password=db_config.password,
        port=db_config.port,
        options=f"-c search_path={db_config.db_schema}",
        connect_timeout=3,
    )


def test_db_connection():
    db_client = db.init(check_db_connection=False)
    with db_client.get_connection() as conn:
        assert conn.scalar(text("SELECT 1")) == 1


def test_check_db_connection(caplog):
    db.init(check_db_connection=True)
    assert "database connection is not using SSL" in caplog.messages


def test_get_session():
    db_client = db.init(check_db_connection=False)
    with db_client.get_session() as session:
        with session.begin():
            assert session.scalar(text("SELECT 1")) == 1