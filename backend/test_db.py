from app.database import Base, engine
from app import models

try:
    Base.metadata.create_all(bind=engine)

    print("CampusIQ database tables created successfully!")

    for table in Base.metadata.sorted_tables:
        print(f"Table created: {table.name}")

except Exception as error:
    print("Table creation failed!")
    print(error)