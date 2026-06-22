from app import app, db, Donation

def create_database():
    print('Creating database...')
    print('Database URI:', app.config['SQLALCHEMY_DATABASE_URI'])
    with app.app_context():
        print('In app context')
        db.create_all()
        print('db.create_all() called')
    print('Database created successfully: donations.db')


if __name__ == '__main__':
    create_database()
