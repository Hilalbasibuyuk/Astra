from questdb.ingress import Sender, TimestampNanos

from apps.config import settings


def create_ilp_sender() -> Sender:
    return Sender(
        "tcp",
        settings.questdb_host,
        settings.questdb_ilp_port,
    )