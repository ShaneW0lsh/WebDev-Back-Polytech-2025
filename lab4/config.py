import os

class Config:
    SECRET_KEY = '8806d05fdb32c6b25bbe417def4258c5e9b4dc4d865aa57a66105ce119d3da2e'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///lab4.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False 