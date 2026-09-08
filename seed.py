import json
from pathlib import Path

from app import Topic, app, db

DATA_FILE = Path(__file__).with_name("templates_data.json")


def seed_topics():
    topics = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    added = 0

    for topic_data in topics:
        exists = Topic.query.filter_by(
            subject=topic_data["subject"], title=topic_data["title"]
        ).first()
        if exists is None:
            db.session.add(Topic(**topic_data))
            added += 1

    db.session.commit()
    return added


if __name__ == "__main__":
    with app.app_context():
        print(f"Added {seed_topics()} topic(s).")
