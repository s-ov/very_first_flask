from flask_login import UserMixin
# UserMixin substitutes - is_authenticated(), is_active(), is_anonymous()
from flask import url_for


class UserLogin(UserMixin):
    def from_db(self, user_id, db):
        self.__user = db.get_user(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['id'])

    def get_name(self):
        return self.__user['name'] if self.__user else 'No name'

    def get_email(self):
        return self.__user['email'] if self.__user else 'No email'

    def get_avatar(self, app):
        img = None
        if not self.__user['avatar']:
            try:
                with app.open_resource(app.root_path + url_for('static', filename='images/mezada.jpg'), "rb") as file:
                    img = file.read()
            except FileNotFoundError as e:
                print(f"Default avatar not found: {e}")
        else:
            img = self.__user['avatar']
        return img

    def verify_extension(self, filename):
        extension = filename.rsplit('.', 1)[1]
        if extension == 'jpg' or extension == 'JPG':
            return True
        return False

    # def is_authenticated(self):
    #     return True
    #
    # def is_active(self):
    #     return True
    #
    # def is_anonymous(self):
    #     return False
