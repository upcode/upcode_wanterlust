from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
db = SQLAlchemy(app)

##############################################################################
                ##### MODEL FOR USER TABLE ####
##############################################################################

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(50), nullable=True)
    username = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(128))
    state = db.Column(db.String(64), nullable=True)
    city = db.Column(db.String(64), nullable=True)
    user_image = db.Column(db.Unicode(128))
    about = db.Column(db.String(64), nullable=True)

##############################################################################
                ##### MODEL FOR USER TABLE ####
##############################################################################
class AdventureList(db.Model):
    """adventure list where users can create a bucketlist of places they want to see"""

    __tablename__ = 'adventurelists'

    adventure_list_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.ForeignKey('users.user_id'), nullable=False)
    adventure_item = db.Column(db.String(64))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<AdventureList adventure_list_id=%s user_id=%s adventure_item=%s>" % (self.adventure_list_id, self.user_id, adventure_item)

#############################################################################
                ##### MODEL D3_State_Map  ####
##############################################################################

class State(db.Model):
    """D3_State_Map Table has all the:
    DB output: STATE_ID: 1 STATE_ABBRREVATION: AL STATE_NAME: Alabama
    """

    __tablename__ = "states"
    state_id = db.Column(db.Integer, autoincrement=True, primary_key=True) # d3 console.log id is same as in db
    state_name = db.Column(db.String(64), nullable=True)
    state_abbrevation = db.Column(db.String(2), nullable=True)


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<State state_map_id=%s  state_abbrevation=%s state_name=%s, user_id=%s, visited_at=%s>" % (self.state_map_id, self.state_id, self. state_abbrevation, self.states_name, self.user_id, visited_at)
#############################################################################
                ##### MODEL D3_State_Map  ####
##############################################################################

class User_State(db.Model):
    """Relationship table for users and states: where users states will be recorded"""
    #creating table name

    __tablename__ = "user_states"

    # defining what table will look like in DB

    user_state_id = db.Column(db.Integer, autoincrement=True, nullable=True, primary_key=True)
    user_id = db.Column(db.ForeignKey('users.user_id'), nullable=False)
    state_id = db.Column(db.ForeignKey('states.state_id'))
    visited_at = db.Column(db.DateTime)
    # Define the relationship to user table
    user = db.relationship("User", backref=db.backref("user_states", order_by=user_id))
    state = db.relationship("State", backref=db.backref("user_states", order_by=state_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User_State user_state_id=%s user_id=%s state_id=%s>" % (self.user_state_id, self.user_id, self.state_id)


##############################################################################
                ##### MODEL FOR POSTCARD TABLE ####
##############################################################################



class Postcard(db.Model):
    """user upload their picture to their travel-timeline"""

    __tablename__ = "postcards"

    postcard_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.ForeignKey('users.user_id'))
    image_title = db.Column(db.Unicode(64))
    postcard_image = db.Column(db.Unicode(128))
    description = db.Column(db.Text)
    street_address = db.Column(db.String(64))
    route_address = db.Column(db.String(64))
    city = db.Column(db.String(64))
    postal_code = db.Column(db.String(64))
    state = db.Column(db.String(64))
    country = db.Column(db.String(64))
    message = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Postcard postcard_id=%s user_id=%s created_at=%s>" % (self.postcard_id, self.user_id)

############################################################################
        #### RELATIONSHIP TABLE FOR USER AND STATE ####
        ## records users states they have visited  ###
##############################################################################
#Associative Users and States


class User_Country(db.Model):
    """Relationship table for users and states: where users states will be recorded"""
    #creating table name

    __tablename__ = "user_countries"

    # defining what table will look like in DB

    user_country_id = db.Column(db.Integer, autoincrement=True, nullable=True, primary_key=True)
    user_id = db.Column(db.ForeignKey('users.user_id'), nullable=False)
    country_id = db.Column(db.ForeignKey('countries.country_id'))
    visited_at = db.Column(db.DateTime)
    # Define the relationship to user table
    user = db.relationship("User", backref=db.backref("user_countries", order_by=user_id))
    country = db.relationship("Country", backref=db.backref("user_countries", order_by=country_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User_Country user_country_id=%s user_id=%s country_id=%s>" % (self.user_country_id, self.user_id, self.country_id)



class Country(db.Model):
    """D3_State_Map Table has all the:
    DB output: STATE_ID: 1 STATE_ABBRREVATION: AL STATE_NAME: Alabama
    """

    __tablename__ = "countries"
    country_id = db.Column(db.Integer, primary_key=True) # d3 console.log id is same as in db
    country_name = db.Column(db.String(64), nullable=True)


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Country country_id=%s country_name=%s, user_id=%s, visited_at=%s>" % (self.country_id, self.country_id, self.country_name, self.user_id, visited_at)



##############################################################################
                        ##### HELPER FUNCTIONS ####
##############################################################################


def connect_to_db(app):
    """Connect the database to our Flask App"""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    # Prepare SQLAlchemy for connection
    db.app = app
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Makes the connection
    db.init_app(app)

##############################################################################

if __name__ == "__main__":
# As a convenience, if we run this module interactively, it will leave
# you in a state of being able to work with the database directly.

    from routes import app
    connect_to_db(app)
    print "#### ** Conected to the Database ** ##"
