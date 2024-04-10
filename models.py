from flask import Flask, render_template, request, redirect, url_for
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from database import Base, db_session
from slugify import slugify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, delete

class User(Base, UserMixin):

    __tablename__ = 'portal_user'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(256), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=False)

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        if not self.id:
            db_session.add(self)
        db_session.commit()

    @staticmethod
    def get_by_id(id):
        return User.query.get(id)

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

class Post(Base, UserMixin):

    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('portal_user.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(256), nullable=False)
    title_slug = Column(String(256), unique=True, nullable=False)
    content = Column(Text)
    def __repr__(self):
        return f'<Post {self.title}>'
    def save(self):
        if not self.id:
            db_session.add(self)
        if not self.title_slug:
            self.title_slug = slugify(self.title)
        saved = False
        count = 0
        while not saved:
            try:
                db_session.commit()
                saved = True
            except IntegrityError:
                count += 1
                self.title_slug = f'{slugify(self.title)}-{count}'
    def public_url(self):
        return url_for('show_post', slug=self.title_slug)
    @staticmethod
    def get_by_slug(slug):
        return Post.query.filter_by(title_slug=slug).first()
    @staticmethod
    def get_all():
        return Post.query.all()



class Radio(Base, UserMixin):

    __tablename__ = 'radios'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    unique_name = Column(String(80), nullable=False)
    username = Column(String(256), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    #bitrate = Column(String(20), nullable=False, default = '192000')
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f'<Radio {self.name}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        if not self.id:
            db_session.add(self)
        db_session.commit()

    @staticmethod
    def get_by_id(id):
        return Radio.query.get(id)
   
    @staticmethod
    def get_by_name(name):
        return Radio.query.filter_by(name=name).first()

    @staticmethod
    def remove_by_unique_name(unique_name):
        #print(dir(db_session))
        #radio_a_borrar= Radio.query.filter_by(unique_name=unique_name).first()
        #print("/n"+"**********"+"/n")
        #print(radio_a_borrar)
        db_session.delete(Radio.query.filter_by(unique_name=unique_name).first())
        db_session.commit()
        return unique_name

    @staticmethod
    def get_all():
        print(Radio.query.all())
        return Radio.query.all()

    def public_url(self):
        print(url_for('show_radio', name=self.name))
        return url_for('show_radio', name=self.name)
