from app import Topic, app, db


with app.app_context():
	topic = db.session.get(Topic, 4)
	if topic is None:
		print('No topic found with ID 4.')
	else:
		print(f'Deleting topic: {topic.title} with ID {topic.id}')
		db.session.delete(topic)
	db.session.commit()