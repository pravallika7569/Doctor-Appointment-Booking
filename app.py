import os, datetime, uuid
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_pymongo import PyMongo
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from forms import RegisterForm, LoginForm, ProfileForm, DoctorProfileForm, RateForm, BookForm, ChatForm, ResetRequestForm, ResetForm
from utils import preprocess_symptoms, chat_response, SymptomRecommender
from bson import ObjectId

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY','dev-secret-key')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/doctor_db')

mongo = PyMongo(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Simple User class for Flask-Login using MongoDB docs
class User(UserMixin):
    def __init__(self, user_doc):
        self._doc = user_doc

    @property
    def id(self):
        return str(self._doc['_id'])

    def get(self, key, default=None):
        return self._doc.get(key, default)

@login_manager.user_loader
def load_user(user_id):
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if not user:
        return None
    return User(user)

# Seed sample data manually
def seed():
    if mongo.db.users.count_documents({}) == 0:
        # patient
        patient = {
            'name':'Demo Patient',
            'email':'patient@example.com',
            'password':generate_password_hash('pass'),
            'role':'patient',
            'created_at':datetime.datetime.utcnow()
        }
        pid = mongo.db.users.insert_one(patient).inserted_id

        # doctor user
        doc_user = {
            'name':'Dr Demo',
            'email':'doctor@example.com',
            'password':generate_password_hash('pass'),
            'role':'doctor',
            'created_at':datetime.datetime.utcnow()
        }
        did = mongo.db.users.insert_one(doc_user).inserted_id

        # doctors collection
        docs = [
            {'name':'Dr Asha','specialization':'Cardiologist','bio':'Cardio expert','rating':4.7,'reviews':34,'user_id':did},
            {'name':'Dr Ravi','specialization':'Dermatologist','bio':'Skin specialist','rating':4.5,'reviews':21,'user_id':did},
            {'name':'Dr Meera','specialization':'General Physician','bio':'Primary care','rating':4.6,'reviews':50},
            
                
            
        ]
        mongo.db.doctors.insert_many(docs)

# Routes
@app.route('/')
def index():
    return render_template('index.html')
# register
@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        if mongo.db.users.find_one({'email':email}):
            flash('Email already registered','warning'); return redirect(url_for('login'))
        user = {
            'name':form.name.data,
            'email':email,
            'password':generate_password_hash(form.password.data),
            'role':form.role.data,
            'created_at':datetime.datetime.utcnow()
        }
        res = mongo.db.users.insert_one(user)
        if form.role.data == 'doctor':
            mongo.db.doctors.insert_one({
                'name':form.name.data,
                'specialization':form.specialization.data or 'General Physician',
                'bio':'',
                'rating':4.5,
                'reviews':0,
                'user_id':res.inserted_id
            })
        flash('Registered. Please login.','success'); return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({'email': form.email.data.lower()})
        if user and check_password_hash(user['password'], form.password.data):
            user_obj = User(user)
            login_user(user_obj)
            flash('Logged in','success')
            if user['role']=='doctor':
                return redirect(url_for('doctor_dashboard'))
            return redirect(url_for('dashboard'))
        flash('Invalid credentials','danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user(); flash('Logged out','info'); return redirect(url_for('index'))
    
#dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.get('role') != 'patient':
        return redirect(url_for('index'))
    appts = list(mongo.db.appointments.find({'patient_id': ObjectId(current_user.id)}))
    return render_template('dashboard.html', appointments=appts)

@app.route('/doctor_dashboard')
@login_required
def doctor_dashboard():
    if current_user.get('role') != 'doctor':
        return redirect(url_for('index'))
    doc = mongo.db.doctors.find_one({'user_id': ObjectId(current_user.id)})
    appts = list(mongo.db.appointments.find({'doctor_id': doc['_id']})) if doc else []
    return render_template('doctor_dashboard.html', doctor=doc, appointments=appts)

# profile
@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user._doc)
    if form.validate_on_submit():
        mongo.db.users.update_one({'_id': ObjectId(current_user.id)}, {'$set':{'name':form.name.data}})
        flash('Profile updated','success'); return redirect(url_for('profile'))
    doctor = mongo.db.doctors.find_one({'user_id': ObjectId(current_user.id)}) if current_user.get('role')=='doctor' else None
    dform = DoctorProfileForm(obj=doctor) if doctor else None
    return render_template('profile.html', form=form, doctor=doctor, dform=dform)

@app.route('/profile_doctor', methods=['POST'])
@login_required
def profile_doctor():
    if current_user.get('role')!='doctor': return redirect(url_for('index'))
    form = DoctorProfileForm()
    if form.validate_on_submit():
        mongo.db.doctors.update_one({'user_id': ObjectId(current_user.id)}, {'$set':{'specialization':form.specialization.data,'bio':form.bio.data}})
        flash('Doctor profile updated','success')
    return redirect(url_for('profile'))

@app.route('/doctors')
def doctors_list():
    docs = list(mongo.db.doctors.find().sort('rating', -1))
    return render_template('doctors.html', doctors=docs)

@app.route('/doctor/<doc_id>')
def doctor_detail(doc_id):
    doc = mongo.db.doctors.find_one({'_id': ObjectId(doc_id)})
    return render_template('doctor_detail.html', doctor=doc)

# book doctors
@app.route('/book/<doc_id>', methods=['GET','POST'])
@login_required
def book(doc_id):
    form = BookForm()
    doc = mongo.db.doctors.find_one({'_id': ObjectId(doc_id)})
    if form.validate_on_submit():
        ap = {
            'patient_id': ObjectId(current_user.id),
            'doctor_id': doc['_id'],
            'symptoms':form.symptoms.data,
            'status':'booked',
            'created_at':datetime.datetime.utcnow()
        }
        mongo.db.appointments.insert_one(ap)
        flash('Appointment booked','success'); return redirect(url_for('dashboard'))
    return render_template('book.html', doctor=doc, form=form)

# rating
@app.route('/rate/<doc_id>', methods=['POST'])
@login_required
def rate(doc_id):
    form = RateForm()
    if form.validate_on_submit():
        score = form.score.data
        doc = mongo.db.doctors.find_one({'_id': ObjectId(doc_id)})
        if doc:
            total = doc.get('rating',0) * doc.get('reviews',0)
            reviews = doc.get('reviews',0) + 1
            rating = (total + score) / reviews if reviews>0 else score
            mongo.db.doctors.update_one({'_id': ObjectId(doc_id)}, {'$set':{'rating': rating, 'reviews': reviews}})
            flash('Thanks for rating','success')
    return redirect(url_for('doctor_detail', doc_id=doc_id))
# chatting form
@app.route('/chat')
@login_required
def chat():
    form = ChatForm()
    return render_template('chat.html', form=form)

#recommending nlp
@app.route('/chat_api', methods=['POST'])
@login_required
def chat_api():
    data = request.get_json() or {}
    symptoms = data.get('symptoms','')
    age = data.get('age',''); gender = data.get('gender','')
    extra = {'age': age, 'gender': gender}
    resp = chat_response(symptoms, extra_features=extra)
    chat_doc = {
        'user_id': ObjectId(current_user.id),
        'message': symptoms,
        'reply': resp.get('reply',''),
        'recommendations': resp.get('recommendations',[]),
        'suggested_doctors': [],
        'created_at': datetime.datetime.utcnow()
    }
    suggested = []
    for r in resp.get('recommendations',[]):
        d = mongo.db.doctors.find_one({'specialization': {'$regex': r, '$options':'i'}})
        if d:
            suggested.append({'id': str(d['_id']), 'name': d['name'], 'specialization': d['specialization'], 'rating': d.get('rating',0)})
    chat_doc['suggested_doctors'] = suggested
    mongo.db.chats.insert_one(chat_doc)
    resp['suggested_doctors'] = suggested
    return jsonify(resp)

@app.route('/analytics')
@login_required
def analytics():
    total_users = mongo.db.users.count_documents({})
    total_doctors = mongo.db.doctors.count_documents({})
    total_appointments = mongo.db.appointments.count_documents({})
    top_docs = list(mongo.db.doctors.find().sort('rating', -1).limit(5))
    return render_template('analytics.html', total_users=total_users, total_doctors=total_doctors, total_appointments=total_appointments, top_docs=top_docs)

# password reset
@app.route('/reset_request', methods=['GET','POST'])
def reset_request():
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({'email': form.email.data.lower()})
        if user:
            token = s.dumps(user['email'], salt='pw-reset-salt')
            reset_link = url_for('reset_with_token', token=token, _external=True)
            print('Password reset link (demo):', reset_link)
            flash('Password reset link printed to server console (demo).','info')
        else:
            flash('Email not found','warning')
        return redirect(url_for('login'))
    return render_template('reset_request.html', form=form)

@app.route('/reset/<token>', methods=['GET','POST'])
def reset_with_token(token):
    form = ResetForm()
    try:
        email = s.loads(token, salt='pw-reset-salt', max_age=3600)
    except Exception:
        flash('Invalid or expired token','danger'); return redirect(url_for('reset_request'))
    if form.validate_on_submit():
        mongo.db.users.update_one({'email': email}, {'$set':{'password': generate_password_hash(form.password.data)}})
        flash('Password updated','success'); return redirect(url_for('login'))
    return render_template('reset_with_token.html', form=form)

if __name__ == '__main__':
    seed()  # Call seed manually at startup
    app.run(debug=True)
