'''
This script sets up the database...and that's all
'''
from flask import Flask,request,jsonify
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #consumes lot of memory: set to false

db=SQLAlchemy(app,engine_options={
	# 'pool': QueuePool(creator),
    'pool_size': 10,
    'pool_recycle': 120,
    'pool_pre_ping': True
    })

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

#An enrolment relation table
# enrolment = db.Table('enrolment', 
# 			db.Column('id', db.Integer, primary_key=True),
# 			db.Column('personnel_id', db.Integer, db.ForeignKey('user.id')),
# 			db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
# 			db.Column('detail_id', db.Integer, db.ForeignKey('detail.id')),
# 			db.Column('announcement_id', db.Integer, db.ForeignKey('announcement.id')),
# 			db.Column('date', db.DateTime, default=datetime.utcnow)
# 		)

#Model VIN Table
class data(db.Model):
	# id = db.Column(db.Integer, primary_key=True)
	lot_no = db.Column(db.String(6), primary_key=True)
	job_no = db.Column(db.String(10), nullable=True)
	skid_no = db.Column(db.String(7), nullable=True)
	ed_no = db.Column(db.String(6), nullable=True)
	vin_no = db.Column(db.String(17), nullable=False)
	katashiki = db.Column(db.String(14), nullable=True)
	colour = db.Column(db.String(25), nullable=True)
	m3 = db.Column(db.Integer, nullable=True)
	weight = db.Column(db.Integer, nullable=True)
	engine_no = db.Column(db.Integer, nullable=True)
	engine_cap = db.Column(db.Integer, nullable=True)
	container_no = db.Column(db.String(11), nullable=False)

	#template relationships
	# projects = db.relationship('Project', secondary=enrolment, backref=db.backref('personnel', lazy='dynamic'))
	# task_details =  db.relationship('Detail', secondary=enrolment, backref=db.backref('personnel', lazy='dynamic'))
	# announcements = db.relationship('Announcement', secondary=enrolment, backref=db.backref('personnel', lazy='dynamic'))

	# date_created =  db.Column(db.DateTime, default=datetime.utcnow)	

	def __repr__(self): 
		return '<Vin %r, %s>' % (self.lot_no, self.vin_no)	

#Model Project Table
# class Project(db.Model):
# 	id = db.Column(db.Integer, primary_key=True)
	# name = db.Column(db.String(200), nullable=False)
	# consultant = db.Column(db.String(100), nullable=False)
	# consultant_id = db.Column(db.Integer, nullable=False)
	# manager = db.Column(db.String(100), nullable=False)
	# manager_id = db.Column(db.Integer, nullable=False)
	# team = db.Column(db.String(200), nullable=True)
	# customer = db.Column(db.String(200), nullable=False)
	# start_date = db.Column(db.String(10), nullable=False)
	# end_date = db.Column(db.String(10), nullable=False)
	# number = db.Column(db.Integer, nullable=True)
	# progress_percentage = db.Column(db.String(8), nullable=True)
	# revised_end_date = db.Column(db.String(10), nullable=True)
	# status = db.Column(db.String(100), nullable=True)
	# actual_end_date = db.Column(db.String(10), nullable=True)

	# tasks=db.relationship('Task', backref='project', lazy=True)
	# registers=db.relationship('Register', backref='project', lazy=True)

	# def __repr__(self): 
	# 	return '<Project %r>' % self.id

#Model Task Table
# class Task(db.Model):
# 	id = db.Column(db.Integer, primary_key=True)
# 	title = db.Column(db.String(100), nullable=False)
# 	description = db.Column(db.String(500), nullable=False)
# 	date_created = db.Column(db.DateTime, default=datetime.utcnow)

# 	creator = db.Column(db.Integer, nullable=False)
# 	project_id=db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
# 	details = db.relationship('Detail', backref='task', lazy=True)

	# target=db.Column(db.String(5), nullable=False)
	# achieved=db.Column(db.String(5), nullable=True)
	# comment=db.Column(db.String(2000),nullable=True)
	# date =  db.Column(db.DateTime)
	# child_task=db.relationship('Reassigned_Task', backref='parent_task', uselist=False)


	# def __repr__(self): 
	# 	return '<Task %r>' % self.title

#Model Task Detailes Table
# class Detail(db.Model):
# 	id = db.Column(db.Integer, primary_key=True)
# 	task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
# 	date_updated = db.Column(db.DateTime, default=datetime.utcnow)
# 	target_date = db.Column(db.DateTime, nullable=True)
# 	entry_type = db.Column(db.Integer, nullable=False)
# 	achieved = db.Column(db.String(5), nullable=True)
# 	target = db.Column(db.String(5), nullable=True)
# 	comment = db.Column(db.String(2000), nullable=True)

# 	def __repr__(self): 
# 		return '<Detail %r>' % self.id

# #Model Register Table
# class Register(db.Model):
# 	id = db.Column(db.Integer, primary_key=True)
# 	date =  db.Column(db.DateTime)
# 	is_present = db.Column(db.Boolean)
# 	time_in = db.Column(db.String(10))
# 	time_out = db.Column(db.String(10))
# 	lunch = db.Column(db.Boolean)
# 	t_and_t= db.Column(db.Float)
# 	personnel_id = db.Column(db.Integer)
# 	personnel_name=db.Column(db.String(100))
	
# 	project_id=db.Column(db.Integer, db.ForeignKey('project.id'),nullable=False)

# 	def __repr__(self): 
# 		return '<Register %r>' % self.id

# class Announcement(db.Model):
# 	id = db.Column(db.Integer, primary_key=True)
# 	date =  db.Column(db.DateTime, default=datetime.utcnow)
# 	sender = db.Column(db.String(100), nullable=False)
# 	title = db.Column(db.String(100), nullable=False)
# 	description = db.Column(db.String(1000), nullable=False)
# 	def __repr__(self): 
# 		return '<Announcement %r>' % self.id

# #Model Reassigned_Task Table
# class Reassigned_Task(db.Model):
# 	id = db.Column(db.Integer, primary_key=True)
# 	parent_id=db.Column(db.Integer, db.ForeignKey('task.id'), unique=True)

# 	def __repr__(self): 
# 		return '<Reassigned_Task %r>' % self.parent_id

if __name__ == '__main__':
    manager.run()