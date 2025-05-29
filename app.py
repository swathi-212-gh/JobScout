from flask import Flask,request,render_template,redirect,url_for,session,flash,jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from pymongo import MongoClient
from scraping import scrape_jobs
from datetime import  datetime

app=Flask(__name__)
app.secret_key='secret_key'

client=MongoClient('mongodb+srv://jobscraper:jobscraper@cluster0.oek6or7.mongodb.net/')
db=client['job_scraper_db']
collection=db['users']

location_map = {
    "": "All Locations",
    "1": "Infopark Kochi Phase 1",
    "2": "Infopark Kochi Phase 2",
    "4": "Infopark Cherthala",
    "5": "Infopark Thrissur"
}

@app.route('/',methods=['GET','POST'])
def  signup():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')

        if collection.find_one({'username':username}):
            message='User already exists. Please login. '
            return render_template('landing.html',message=message)
            
        
        hashed_password=generate_password_hash(password)
        collection.insert_one({'username':username,'password':hashed_password})
        return redirect('/index')
    return render_template('landing.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password') 

        user=collection.find_one({'username':username})
        if user:
            hash_pass=user.get('password','')      
            if user['password']==hash_pass:
                session['username']=username
                return redirect('/index')
        else:
            message='login unsuccessful.Please create an account'
            return render_template('login.html',message=message)
    return render_template('login.html')           


@app.route('/index',methods=['GET','POST'])
def index():
    if 'username' not in session:
        return redirect('/login')
    jobs=[]
    element=''
    offers=''
    if request.method=='POST':
        keyword=request.form['keyword']
        location_id=request.form['location_id']
        sort_order=request.form.get('sort_order','none')
        company_sort=request.form.get('company_sort','none')

        jobs=scrape_jobs(keyword,location_id)
        offers=len(jobs)
        element=location_map[location_id]
        #hide_expired='hide_expired' in request.form

        if sort_order=='asc':
            jobs.sort(key=lambda x: x['parse_date'])
        elif sort_order=='desc':    
            jobs.sort(key=lambda x: x['parse_date'],reverse=True)



        if company_sort=='asc':
            jobs.sort(key=lambda x: x['company'].lower())
        elif company_sort=='desc':
            jobs.sort(key=lambda x: x['company'].lower(),reverse=True) 

    return render_template('index.html',jobs=jobs,element=element,offers=offers)
"""        if hide_expired:
            jobs=[job for job in jobs if job['parse_date']>=datetime.today()]"""

@app.route('/save',methods=['POST'])
def save_jobs():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'}), 403
    username=session['username']
    job=request.get_json()
    if not job:
        return jsonify({'status': 'error', 'message': 'No data received'}), 400
    collection.update_one(
        {'username':username},
        {'$addToSet':{'saved_jobs':job}}
    )
    return jsonify({'status': 'success', 'message': 'Job saved successfully!'})

@app.route('/saved')
def saved():
    if 'username' not in session:
        return redirect('/login')
    
    user = collection.find_one({'username': session['username']})
    saved_jobs = user.get('saved_jobs', []) if user else []
    return render_template('saved.html', jobs=saved_jobs)


@app.route('/delete', methods=['POST'])
def delete_job():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'User not logged in'}), 401

    username = session['username']
    job = request.get_json()

    if not job:
        return jsonify({'status': 'error', 'message': 'No data received'}), 400

    collection.update_one(
        {'username': username},
        {'$pull': {'saved_jobs': job}}
    )

    return jsonify({'status': 'success', 'message': 'Job deleted successfully!'})


if __name__ =='__main__':
    app.run(debug=True)    