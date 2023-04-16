from flask import Flask, render_template, request, redirect, flash, session
import pickle
from flask_mysqldb import MySQL
import MySQLdb.cursors
import mysql.connector
# from flask_bcrypt import Bcrypt
# import mysql.connector
app = Flask(__name__)
# bcrypt = Bcrypt(app)
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "intellimed"

db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="intellimed"
)
mycursor = db.cursor()


db = MySQL(app)


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/user/signup", methods=['GET', 'POST'])
def contact():
    if(request.method == 'POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('number')
        address = request.form.get('address')
        password = request.form.get('password')
        cur = db.connection.cursor()
        # hash_password=bcrypt.generate_password_hash(password,10)
        # cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM user WHERE username = % s AND password = % s', (username, password))
        # user = cursor.fetchone()
        # if user:
        #     # session['loggedin'] = True
        #     # session['sno'] = user['sno']
        #     # session['name'] = user['name']
        #     # session['email'] = user['email']
        # return redirect('/signup')
        cur.execute("INSERT IGNORE INTO user (name,phoneno, email,username,password,address) VALUES (%s,%s,%s,%s,%s,%s)",
                    (name, phone, email, username, password, address))

        db.connection.commit()
        cur.close()
        return redirect('/user/')
    return render_template('user/SignUp.html')

# @app.route('/user/', methods=['GET', 'POST'])
# def login():
#     # Output message if something goes wrong...
#     # Check if "username" and "password" POST requests exist (user submitted form)
#     if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
#         # Create variables for easy access
#         username = request.form.get('username')
#         password = request.form.get('password')
#         # Check if account exists using MySQL
#         cursor = db.connection.cursor()
#         hash_password=bcrypt.generate_password_hash(password,10)
#         cursor.execute('SELECT * FROM user WHERE username = %s AND password = %s', (username, hash_password))
#         # Fetch one record and return result
#         account = cursor.fetchone()
#         cursor.close()
#         print(password)
#         print(account['password'])
#         # If account exists in accounts table in out database
#         if account and hash_password==account['password']:
#             # Create session data, we can access this data in other routes
#             # session['loggedin'] = True
#             # session['id'] = account['id']
#             # session['username'] = account['username']
#             # Redirect to home page
#             print('wrong password')
#             return redirect('/')
#         else:
#             # Account doesnt exist or username/password incorrect
#             return render_template('user/user_signin.html')
#     # Show the login form with message (if any)s
#     return render_template('user/user_signin.html')

# from flask import Flask, render_template, request, redirect, url_for, session
# from flask_mysqldb import MySQL
# import MySQLdb.cursors
# import re


# app = Flask(__name__)


# app.secret_key = 'xyzsdfg'

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'intellimed'

# mysql = MySQL(app)

@app.route('/user/', methods=['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM user WHERE username = % s AND password = % s', (username, password))
        x = cursor.fetchone()
        if x:
            # session['loggedin'] = True
            # session['sno'] = user['sno']
            # session['name'] = user['name']
            # session['email'] = user['email']
            mesage = 'Logged in successfully !'
            return redirect('/home')
        else:
            mesage = 'Please enter correct email / password !'
    return render_template('user/user_signin.html', mesage=mesage)

# # @app.route('/logout')
# # def logout():
# #     session.pop('loggedin', None)
# #     session.pop('userid', None)
# #     session.pop('email', None)
# #     return redirect(url_for('login'))
# import re
# @app.route('/user/signup', methods =['GET', 'POST'])
# def register():
#     mesage = ''
#     if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form and 'username' in request.form and 'address' in request.form and 'phone' in request.form:
#         # userName = request.form['name']
#         # password = request.form['password']
#         # email = request.form['email']
#         name = request.form.get('name')
#         username = request.form.get('username')
#         email = request.form.get('email')
#         phone = request.form.get('number')
#         address = request.form.get('address')
#         password=request.form.get('password')
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
#         account = cursor.fetchone()
#         if account:
#             mesage = 'Account already exists !'
#         elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
#             mesage = 'Invalid email address !'
#         elif not username or not password or not email:
#             mesage = 'Please fill out the form !'
#         else:
#             cursor.execute("INSERT INTO user (name,phoneno, email,username,password,address) VALUES (%s,%s,%s,%s,%s,%s)",(name,phone,email,username,password,address))
#             # cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s)', (username, email, password, ))
#             mysql.connection.commit()
#             mesage = 'You have successfully registered !'
#     elif request.method == 'POST':
#         mesage = 'Please fill out the form !'
#     return render_template('user/SignUp.html', mesage = mesage)

#end is here


@app.route('/')
def home():
    return render_template('landing1.html')


@app.route('/nextsteps')
def Next_steps():
    return render_template('landing.html')


@app.route('/AboutUs')
def about2():
    return render_template('AboutUs.html')


@app.route('/contact')
def contact2():
    return render_template('contact.html')

# @app.route('/admin/')
# def AdminIndex():
#     return render_template('admin/a_signin.html')


@app.route('/admin/', methods=['POST', 'GET'])
def adminsignin():
    if request.method == "POST":
        password = request.form.get('password')
        print(password)
        if(password == "password"):
            return redirect('/calculate')
        else:
            return redirect('/admin/')
    else:
        return render_template("admin/a_signin.html")


@app.route('/user/signup')
def Usersignup():
    return render_template('user/SignUp.html')


@app.route('/user/')
def Usersignin():
    return render_template('user/user_signin.html')


# paba code continues from here StoD

model = pickle.load(open('modelStoD.pkl', 'rb'))
model2 = pickle.load(open('modelDtoM.pkl', 'rb'))


# make this slug correct
@app.route('/home')
def user_home():
    return render_template("home.html")


# make this slug correct
@app.route('/predict', methods=['POST', 'GET'])
def predict():
    freq = {}
    freq['itching'] = 0
    freq['continuous_sneezing'] = 0
    freq['shivering'] = 0
    freq['joint_pain'] = 0
    freq['stomach_pain'] = 0
    freq['acidity'] = 0
    freq['vomiting'] = 0
    freq['spotting_urination'] = 0
    freq['fatigue'] = 0
    freq['weight_gain'] = 0
    freq['anxiety'] = 0
    freq['cold_hands_and_feets'] = 0
    freq['mood_swings'] = 0
    freq['weight_loss'] = 0
    freq['restlessness'] = 0
    freq['irregular_sugar_level'] = 0
    freq['cough'] = 0
    freq['high_fever'] = 0
    freq['breathlessness'] = 0
    freq['sweating'] = 0
    freq['dehydration'] = 0
    freq['indigestion'] = 0
    freq['headache'] = 0
    freq['back_pain'] = 0
    freq['constipation'] = 0
    freq['abdominal_pain'] = 0
    freq['diarrhoea'] = 0
    freq['mild_fever'] = 0
    freq['yellow_urine'] = 0
    freq['redness_of_eyes'] = 0
    freq['chest_pain'] = 0
    freq['fast_heart_rate'] = 0
    freq['cramps'] = 0
    freq['obesity'] = 0
    freq['muscle_weakness'] = 0
    freq['stiff_neck'] = 0
    freq['depression'] = 0
    freq['muscle_pain'] = 0
    freq['abnormal_menstruation'] = 0
    freq['lack_of_concentration'] = 0

    dis = {}
    # dis['Acne']=0
    dis['AIDS'] = 0
    dis['Alcoholic hepatitis'] = 0
    dis['Allergy'] = 0
    dis['Arthritis'] = 0
    dis['Bronchial Asthma'] = 0
    dis['Cervical spondylosis'] = 0
    dis['Chicken pox'] = 0
    dis['Chronic cholestasis'] = 0
    dis['Common Cold'] = 0
    dis['Dengue'] = 0
    dis['Diabetes'] = 0
    dis['Drug Reaction'] = 0
    dis['Fungal infection'] = 0
    dis['Fungal infection'] = 0
    dis['Gastroenteritis'] = 0
    dis['GERD'] = 0
    dis['Heart attack'] = 0
    dis['hepatitis A'] = 0
    dis['hepatitis B'] = 0
    dis['hepatitis C'] = 0
    dis['Hepatitis D'] = 0
    dis['Hepatitis E'] = 0
    dis['Hypertension'] = 0
    dis['Hyperthyroidism'] = 0
    dis['Hypoglycemia'] = 0
    dis['Hypothyroidisms'] = 0
    dis['Impetigo'	] = 0
    dis['Jaundice'] = 0
    dis['Malaria'] = 0
    dis['Migraine'] = 0
    dis['Osteoarthristis'] = 0
    dis['Paralysis'] = 0
    dis['Paroymsal Positional Vertigo'] = 0
    dis['Peptic ulcer diseae'] = 0
    dis['Piles'] = 0
    dis['Pneumonia'] = 0
    dis['Psoriasis'] = 0
    dis['Tuberculosis'] = 0
    dis['Typhoid'] = 0
    dis['Urinary tract infection'] = 0
    dis['Varicose veins'] = 0

    thisdict2 = {
        0: "",
        1: "M01AB",
        2: "M01AE",
        3: "N02BA",
        4: "N02BE/B",
        5: "N05B",
        6: "N05C",
        7: "R03",
        8: "R06",
        9: ""
    }

    temp = []
    if request.method == "POST":
        print(request.form)
        countOne = 0
        for x in request.form:
            if(request.form[x] == '0'):
                freq[x] = 1
                countOne = countOne+1
        for x in freq:
            temp.append(freq[x])
        print(temp)
        if countOne == 0:
            return render_template('home.html',
                                   pred="You are healthy",
                                   pred2="You dont need any medicine")

        ip = []
        ip.append(temp)
        print(ip)
        value = model.predict(ip)
        print(value[0])
        ip2 = []
        temp2 = []
        if value[0] in dis:
            dis[value[0]] = 1
        count = 0
        for x in dis:
            count = count+1
            temp2.append(dis[x])

        ip2.append(temp2)

        print(temp2)
        print(count)
        value2 = model2.predict(ip2)
        print(value2)
    # return render_template('home.html',pred=value[0],pred2=thisdict2[int(value2[0])])
    # return render_template('home.html',
    #                        pred=f" The predicted disease is {value[0]}")
    return render_template('home.html',
                           pred=f" The predicted disease is {value[0]}",
                           pred2=f"Go to group {thisdict2[round(value2[0])]}")
    # return render_template('home.html')
    # return redirect('/new')


@app.route('/buy')
def buy():
    return render_template("buy.html")

from pickle import load
import math
from tensorflow.python.keras.models import load_model
# selected_value='a'
@app.route('/calculate',methods=['POST','GET'])
def calculate():
    if request.method=="POST":
        mycursor = db.cursor()

        selected_value = request.form['custom-select']
        print(selected_value)
        mycursor.execute(f"SELECT * FROM {selected_value} ORDER BY sno DESC LIMIT 3")

        result = mycursor.fetchall()
       
        # print(result[2][1])
        # print(result[1][1])
        # print(result[0][1])
        scaler = load(open(f'{selected_value}.pkl', 'rb'))
        model = load_model(f'{selected_value}.h5')
        val=model.predict([[[result[2][1]],[result[1][1]],[result[0][1]]]])
        # val=1
        ret=math.ceil(scaler.inverse_transform(val)[0][0])
        if(ret>result[2][1]+result[0][1]+result[1][1]):
            ret=round((result[2][1]+result[0][1]+result[1][1])/3)
        return render_template("calculate.html",pred=f"Expected stock for next month for {selected_value} is {ret}",pred1=f"{selected_value}",pred2=f"Current stock is {result[0][1]}")
    return render_template("calculate.html")

# import _mysql as mc
# db = mc.connect (host = "localhost", user = "root", passwd = "password1234")
@app.route('/add',methods=['POST','GET'])
def add():
    if request.method=="POST":
        selected_value = request.form.get('dbname')
        val = request.form.get('val')
        print(selected_value)
        print(val)

        
        cur=db.connection.cursor()
        # mycursor
        mycursor.execute(f"INSERT INTO m01ab (val) VALUES (%d)",(val))

        # cur.execute("INSERT IGNORE INTO user (name,phoneno, email,username,password,address) VALUES (%s,%s,%s,%s,%s,%s)",
        #             (name, phone, email, username, password, address))
        
        # cur.execute("INSERT IGNORE INTO m01ab (val) VALUES (%s)",(val))

        # mycursor.execute("INSERT INTO m01ab (val) VALUES (%d)",(val))
        mycursor.commit()


        db.connection.commit()
        # cur.close()
    return render_template("home.html")

if __name__ == '__main__':
    app.run(debug=True)
