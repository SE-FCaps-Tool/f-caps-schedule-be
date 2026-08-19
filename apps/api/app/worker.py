"""Small local worker process for PostgreSQL outbox delivery."""

import time

from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_engine
from app.services.notification_dispatcher import (
    process_availability_reminders,
    process_outbox,
    process_remediation_reminders,
    process_round_auto_close,
)


def run() -> None:
    engine = get_engine(get_settings().database_url)
    while True:
        with Session(engine) as db:
            process_round_auto_close(db)
            process_remediation_reminders(db)
            process_availability_reminders(db)
            process_outbox(db)
        time.sleep(2)


if __name__ == "__main__":
    run()
