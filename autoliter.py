from app import create_app, db
from flask_migrate import Migrate 

app = create_app("development")
# app = create_app("production")
migrate = Migrate(app, db)


# ip
# 106.14.22.183