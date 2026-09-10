from app import app, db

with app.app_context():
    for table in reversed(db.metadata.sorted_tables):
        print(f'Dropping table {table.name}')
        db.session.execute(table.delete())
        db.session.commit()
