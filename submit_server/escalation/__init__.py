import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import sql
import click
import logging
from logging.handlers import RotatingFileHandler

# create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    #        DATABASE=os.path.join(app.instance_path, 'escalation.sqlite'),
    UPLOAD_FOLDER = os.path.join(app.instance_path,'submissions'),
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(app.instance_path,'escalation.sqlite'),
    #32 MB max upload
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024,
    ADMIN_KEY='secret',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)
    
# ensure the instance folder exists
try:
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)
except OSError:
    pass

db = SQLAlchemy(app)

class Submission(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64))
    expname = db.Column(db.String(64))
    crank = db.Column(db.String(64))
    filename = db.Column(db.String(256))
    notes = db.Column(db.Text)
    created = db.Column(db.DateTime(timezone=True), server_default=sql.func.now())
    def __repr__(self):
        return '<Submission {} {} {} {}>'.format(self.username,self.expname,self.crank,self.filename) 

class Crank(db.Model):
    id       = db.Column(db.Integer,primary_key=True)
    crank    = db.Column(db.String(64))    
    stateset = db.Column(db.String(11))
    filename = db.Column(db.String(256))    
    githash  = db.Column(db.String(7))    #git commit of stateset file
    username = db.Column(db.String(64))
    current  = db.Column(db.Boolean,server_default='FALSE')
    created  = db.Column(db.DateTime(timezone=True), server_default=sql.func.now())

    def  __repr__(self):
        return '<Crank {} {} {} {}>'.format(self.crank,self.stateset,self.githash,self.current)

class Run(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    crank    = db.Column(db.String(64))    
    stateset = db.Column(db.String(11))
    dataset = db.Column(db.String(256))
    name = db.Column(db.String(256))
    _rxn_M_inorganic = db.Column(db.Float)
    _rxn_M_organic = db.Column(db.Float)           

    def __repr__(self):
        return '<Run {} {} {} {}>'.format(self.dataset,self.name,self._rxn_M_inorganic,self._rxn_M_organic)

@app.cli.command()
def init_db():
    """Clear the existing data and create new tables."""
    db.create_all()
    click.echo('Initialized the database.')   

@app.cli.command('demo-data')
def insert_demo_data():
    Run.query.delete()
    Submission.query.delete()
    Crank.query.delete()    
    db.session.add(Crank(crank='0001', stateset='12345678901', filename='file.csv', githash='abc1234', username='snovot', current=False))
    db.session.add(Crank(crank='0002', stateset='aaaa5678901', filename='file.csv', githash='abc1235', username='snovot', current=False))
    db.session.add(Crank(crank='0002', stateset='bbbb5678901', filename='file.csv', githash='abc1236', username='snovot', current=True))
    db.session.add(Submission(username='snovot',expname='name',crank='0001',filename='file.csv',notes='test test test'))
    db.session.add(Submission(username='snovot',expname='name1',crank='0002',filename='file.csv',notes='test test test'))
    db.session.add(Submission(username='snovot',expname='name2',crank='0002',filename='file.csv',notes='test test test'))    
    db.session.add(Run(crank='0002',stateset='bbbb5678901',dataset='12345678901',name='0',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='bbbb5678901',dataset='12345678901',name='1',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='bbbb5678901',dataset='12345678901',name='2',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='bbbb5678901',dataset='12345678901',name='3',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='bbbb5678901',dataset='12345678901',name='4',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='bbbb5678901',dataset='12345678901',name='5',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='bbbb5678901',dataset='12345678901',name='6',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='bbbb5678901',dataset='12345678901',name='7',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='bbbb5678901',dataset='12345678901',name='8',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))
    db.session.add(Run(crank='0002',stateset='bbbb5678901',dataset='12345678901',name='9',_rxn_M_inorganic=0.0,_rxn_M_organic=0.0))    
    db.session.commit()
    click.echo("Added demo data")
    
# a simple page that says hello
@app.route('/hello')
def hello():
    return 'Hello, World!'

from . import submission
from . import view
from . import admin
app.register_blueprint(submission.bp)
app.register_blueprint(view.bp)
app.register_blueprint(admin.bp)            

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/escalation.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('ESCALATion started')    


from .database import *
@app.cli.command()
def test():
    click.echo(get_stateset(1))
    
