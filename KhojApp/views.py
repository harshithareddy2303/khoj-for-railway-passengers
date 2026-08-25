import matplotlib
matplotlib.use('Agg')
from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
import random
from datetime import datetime
from datetime import date
import pymysql
import smtplib
import base64
import numpy as np
import io
import pickle
import matplotlib.pyplot as plt
import cv2
from ultralytics import YOLO
import bcrypt

global user, usertype

CONFIDENCE_THRESHOLD = 0.30
GREEN = (0, 255, 0)

yolo_model = YOLO("model/best.pt")
print("Yolo Model Loaded")

def detectObject(frame):
    global yolo_model
    plan = ""
    labels = ['Backpack', 'Belt-bag', 'Car-key-Chevrolet', 'Car-key-Ford', 'Car-key-Honda', 'Car-key-Hyundai', 'Car-key-Kia', 'Car-key-Lexus',
              'Car-key-Mercedes-Benz', 'Car-key-Mitsubishi', 'Car-key-Nissan', 'Car-key-Toyota', 'Car-key-Volkswagen', 'Car-key-non-specific', 'Card',
              'Cross-bag', 'Electronic-devices-AirPods', 'Electronic-devices-AirPods-case', 'Electronic-devices-charger', 'Electronic-devices-earphones',
              'Electronic-devices-headphones', 'Electronic-devices-laptop', 'Electronic-devices-laptop-charger', 'Electronic-devices-phone',
              'Electronic-devices-phone-charger', 'Electronic-devices-powerbank', 'Electronic-devices-tablet', 'Glasses', 'Handbag', 'Key',
              'Laptop-bag', 'Smart-watch-black', 'Smart-watch-gold', 'Smart-watch-pink', 'Smart-watch-silver', 'Smart-watch-white', 'Sunglasses',
              'Travel-bag', 'Wallet-black', 'Wallet-brown', 'Wallet-grey', 'Wallet-multicolor', 'Wallet-pink', 'Wallet-red', 'Wallet-turquoise',
              'Watch-black', 'Watch-blue', 'Watch-brown', 'Watch-gold', 'Watch-silver', 'Watch-white']
    detections = yolo_model(frame)[0]
    # loop over the detections
    for data in detections.boxes.data.tolist():
        print(data)
        # extract the confidence (i.e., probability) associated with the detection
        confidence = data[4]
        cls_id = data[5]
        # filter out weak detections by ensuring the 
        # confidence is greater than the minimum confidence
        if float(confidence) >= CONFIDENCE_THRESHOLD:
            xmin, ymin, xmax, ymax = int(data[0]), int(data[1]), int(data[2]), int(data[3])
            cv2.rectangle(frame, (xmin, ymin) , (xmax, ymax), GREEN, 2)
            cv2.putText(frame, labels[int(cls_id)], (xmin, ymin+60),  cv2.FONT_HERSHEY_SIMPLEX,0.7, (255, 0, 0), 2)            
            break
    return frame

def ImageCheckAction(request):
    if request.method == 'POST':
        filename = request.FILES['t1'].name
        image = request.FILES['t1'].read() #reading uploaded file from user
        if os.path.exists("KhojApp/static/"+filename):
            os.remove("KhojApp/static/"+filename)
        with open("KhojApp/static/"+filename, "wb") as file:
            file.write(image)
        file.close()
        img = cv2.imread("KhojApp/static/"+filename)
        img = detectObject(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        plt.imshow(img)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        img_b64 = base64.b64encode(buf.getvalue()).decode() 
        context= {'data':"Lost & Found Detected Objects", 'img': img_b64}
        return render(request, 'VolunteerScreen.html', context)

def ImageCheck(request):
    if request.method == 'GET':
        return render(request, 'ImageCheck.html', {})   

def WebcamCheck(request):
    if request.method == 'GET':
        video_cap = cv2.VideoCapture(0)
        while True:
            ret, frame = video_cap.read()
            if ret == True:
                frame = detectObject(frame)
                cv2.imshow("Yolov8 Lost & Found Object Detection Output", frame)
                if cv2.waitKey(5) == ord("q"):
                    break
            else:
                break
        video_cap.release()
        cv2.destroyAllWindows()
        context= {'data':'Object Detection Completed'}
        return render(request, 'VolunteerScreen.html', context)           

def sendEmail(email):
    msg = 'Your lost item found & you can collect from Railway station' 
    em = []
    em.append(email)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as connection:
        email_address = 'kaleem202120@gmail.com'
        email_password = 'xyljzncebdxcubjq'
        connection.login(email_address, email_password)
        connection.sendmail(from_addr="kaleem202120@gmail.com", to_addrs=em, msg="Subject : Alert from Lost & Found railway\n"+msg)   

def getEmail(user):
    companion = ""
    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'khoj',charset='utf8')
    with con:    
        cur = con.cursor()
        cur.execute("select email FROM addpassenger where username='"+user+"'")
        rows = cur.fetchall()
        for row in rows:
            companion = row[0]
            break
    return companion    

def CheckComplaintAction(request):
    if request.method == 'GET':
        global user
        cid = request.GET.get('rid', False)
        passenger = request.GET.get('t2', False)
        email = getEmail(passenger)
        sendEmail(email)
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'khoj',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "update lostcomplaint set status='Completed' where complaint_id='"+cid+"'"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record Inserted")
        if db_cursor.rowcount == 1:
            status = "<font size=3 color=blue>Email Notification sent about item found to "+passenger+" on email "+email+"</font>"
        context= {'data': status}
        return render(request, 'VolunteerScreen.html', context)     

def CheckComplaint(request):
    if request.method == 'GET':
        global user
        columns = ['Complaint ID','Username','Train No/Name','Compartment No','Seat No','Item Description','Lost Date', 'Status','Image detection','Webcam Detection','Update Status']
        output = "<table border=1 align=center>"
        font = '<font size="" color="black">'
        for i in range(len(columns)):
            output += '<th>'+font+columns[i]+'</th>'
        output += "</tr>"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'khoj',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select * FROM lostcomplaint where status='Under Progress'")
            rows = cur.fetchall()
            for row in rows:
                output+='<tr><td>'+font+str(row[0])+'</td>'
                output+='<td>'+font+str(row[1])+'</td>'
                output+='<td>'+font+str(row[2])+'</td>'
                output+='<td>'+font+str(row[3])+'</td>'
                output+='<td>'+font+str(row[4])+'</td>'
                output+='<td>'+font+str(row[5])+'</td>'
                output+='<td>'+font+str(row[6])+'</td>'
                output+='<td>'+font+str(row[7])+'</td>'
                output+='<td><a href=\'ImageCheck\'><font size=3 color=black>Image Detection</font></a></td>'
                output+='<td><a href=\'WebcamCheck\'><font size=3 color=black>Webcam Detection</font></a></td>'
                output+='<td><a href=\'CheckComplaintAction?rid='+str(row[0])+'&t2='+row[1]+'\'><font size=3 color=black>Click & Update Status</font></a></td></tr>'  
        output += "</table><br/><br/><br/><br/>"
        context= {'data':output}
        return render(request, 'VolunteerScreen.html', context)    

def CheckAssistanceAction(request):
    if request.method == 'POST':
        global user
        passenger = request.POST.get('t1', False)
        treatment = request.POST.get('t2', False)
        status = "<font size=3 color=red>Error in providing medical treatment</font>"
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'khoj',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "update medical set status='"+user+' Volunteer treatment : '+treatment+"' where username='"+passenger+"' and status='Pending'"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record Inserted")
        if db_cursor.rowcount == 1:
            status = "<font size=3 color=blue>Medical assistance & treatment details updated in Database</font>"
        context= {'data': status}
        return render(request, 'VolunteerScreen.html', context)     

def ProvideAssistance(request):
    if request.method == 'GET':
        global user
        passenger = request.GET.get('rid', False)
        output = '<tr><td><font size="3" color="black">Passenger&nbsp;Name</b></td>'
        output += '<td><input type="text" name="t1" size="30" value="'+passenger+'" readonly></td></tr>'        
        context= {'data1':output}
        return render(request, 'ProvideAssistance.html', context)    

def CheckAssistance(request):
    if request.method == 'GET':
        global user
        columns = ['Passenger Name','Train Name/No','Compartment No','Seat No','Symptoms','Report Date','Provide Treatment']
        output = "<table border=1 align=center>"
        font = '<font size="" color="black">'
        for i in range(len(columns)):
            output += '<th>'+font+columns[i]+'</th>'
        output += "</tr>"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'khoj',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select * FROM medical where status='Pending'")
            rows = cur.fetchall()
            for row in rows:
                output+='<tr><td>'+font+str(row[0])+'</td>'
                output+='<td>'+font+str(row[1])+'</td>'
                output+='<td>'+font+str(row[2])+'</td>'
                output+='<td>'+font+str(row[3])+'</td>'
                output+='<td>'+font+str(row[4])+'</td>'
                output+='<td>'+font+str(row[5])+'</td>'
                output+='<td><a href=\'ProvideAssistance?rid='+str(row[0])+'\'><font size=3 color=black>Click for Assistance</font></a></td></tr>'                
        output += "</table><br/><br/><br/><br/>"
        context= {'data':output}
        return render(request, 'VolunteerScreen.html', context)

def ViewVolunteer(request):
    if request.method == 'GET':
        columns = ['Username','Password','Phone No','Email ID','Address','User Type']
        output = "<table border=1 align=center>"
        font = '<font size="" color="black">'
        for i in range(len(columns)):
            output += '<th>'+font+columns[i]+'</th>'
        output += "</tr>"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'khoj',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select * FROM users where usertype='Volunteer'")
            rows = cur.fetchall()
            for row in rows:
                output+='<tr><td>'+font+str(row[0])+'</td>'
                output+='<td>'+font+str(row[1])+'</td>'
                output+='<td>'+font+str(row[2])+'</td>'
                output+='<td>'+font+str(row[3])+'</td>'
                output+='<td>'+font+str(row[4])+'</td>'
                output+='<td>'+font+str(row[5])+'</td></tr>'                
        output += "</table><br/><br/><br/><br/>"
        context= {'data':output}
        return render(request, 'AdminScreen.html', context)

def ViewComplaints(request):
    if request.method == 'GET':
        columns = ['Complaint ID','Username','Train No/Name','Compartment No','Seat No','Item Description','Lost Date', 'Status']
        output = "<table border=1 align=center>"
        font = '<font size="" color="black">'
        for i in range(len(columns)):
            output += '<th>'+font+columns[i]+'</th>'
        output += "</tr>"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'khoj',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select * FROM lostcomplaint")
            rows = cur.fetchall()
            for row in rows:
                output+='<tr><td>'+font+str(row[0])+'</td>'
                output+='<td>'+font+str(row[1])+'</td>'
                output+='<td>'+font+str(row[2])+'</td>'
                output+='<td>'+font+str(row[3])+'</td>'
                output+='<td>'+font+str(row[4])+'</td>'
                output+='<td>'+font+str(row[5])+'</td>'
                output+='<td>'+font+str(row[6])+'</td>'
                output+='<td>'+font+str(row[7])+'</td></tr>'    
        output += "</table><br/><br/><br/><br/>"
        context= {'data':output}
        return render(request, 'AdminScreen.html', context)

def CheckStatus(request):
    if request.method == 'GET':
        global user
        columns = ['Complaint ID','Username','Train No/Name','Compartment No','Seat No','Item Description','Lost Date', 'Status']
        output = "<table border=1 align=center>"
        font = '<font size="" color="black">'
        for i in range(len(columns)):
            output += '<th>'+font+columns[i]+'</th>'
        output += "</tr>"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'khoj',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select * FROM lostcomplaint where username='"+user+"'")
            rows = cur.fetchall()
            for row in rows:
                output+='<tr><td>'+font+str(row[0])+'</td>'
                output+='<td>'+font+str(row[1])+'</td>'
                output+='<td>'+font+str(row[2])+'</td>'
                output+='<td>'+font+str(row[3])+'</td>'
                output+='<td>'+font+str(row[4])+'</td>'
                output+='<td>'+font+str(row[5])+'</td>'
                output+='<td>'+font+str(row[6])+'</td>'
                output+='<td>'+font+str(row[7])+'</td></tr>'    
        output += "</table><br/><br/><br/><br/>"
        context= {'data':output}
        return render(request, 'UserScreen.html', context)    

def getPhone(user):
    companion = ""
    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'khoj',charset='utf8')
    with con:    
        cur = con.cursor()
        cur.execute("select contact_no FROM addpassenger where username='"+user+"'")
        rows = cur.fetchall()
        for row in rows:
            companion = row[0]
            break
    return companion

def getCompanion(train, compartment, seat, output, dd):
    global user
    font = '<font size="" color="black">'
    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'khoj',charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("select * FROM addpassenger where username!='"+user+"' and travel_date='"+dd+"' and train_no='"+train+"' and compartment_no='"+compartment+"'")
        rows = cur.fetchall()
        for row in rows:
            username = row[1]
            contact = getPhone(username)
            output+='<tr><td>'+font+str(username)+'</td>'
            output+='<td>'+font+str(row[4])+'</td>'
            output+='<td>'+font+str(contact)+'</td>'
    return output   

def Safety(request):
    if request.method == 'GET':
        global user
        dd = str(date.today())
        columns = ['Companion Name', 'Seat No', 'Phone No']
        output = "<table border=1 align=center>"
        font = '<font size="" color="black">'
        for i in range(len(columns)):
            output += '<th>'+font+columns[i]+'</th>'
        output += "</tr>"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'khoj',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select * FROM addpassenger where username='"+user+"' and travel_date='"+dd+"'")
            rows = cur.fetchall()
            for row in rows:
                train = row[2]
                compartment = row[3]
                seat = row[4]
                output = getCompanion(train, compartment, seat, output, dd)                
        output += "</table><br/><br/><br/><br/>"
        context= {'data':output}
        return render(request, 'UserScreen.html', context)    

def MedicalAssistance(request):
    if request.method == 'GET':
        return render(request, 'MedicalAssistance.html', {})    

def MedicalAssistanceAction(request):
    if request.method == 'POST':
        global user
        train = request.POST.get('t1', False)
        compartment = request.POST.get('t2', False)
        seat = request.POST.get('t3', False)
        symptoms = request.POST.get('t4', False)
        dd = str(datetime.now())
        dd = dd.split(".")
        dd = dd[0]
        status = "<font size=3 color=red>Error in taking medical assitance request</font>"
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'khoj',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO medical VALUES('"+str(user)+"','"+train+"','"+compartment+"','"+seat+"','"+symptoms+"','"+dd+"','Pending')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record Inserted")
        if db_cursor.rowcount == 1:
            status = "<font size=3 color=blue>Your Request for Health Assistance Accepted<br/>Please wait! Soon our Volunteer will approached you</font>"
        context= {'data': status}
        return render(request, 'UserScreen.html', context)    

def LostFound(request):
    if request.method == 'GET':
        return render(request, 'LostFound.html', {})    

def LostFoundAction(request):
    if request.method == 'POST':
        global user
        train = request.POST.get('t1', False)
        compartment = request.POST.get('t2', False)
        seat = request.POST.get('t3', False)
        desc = request.POST.get('t4', False)
        cid = "none"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'khoj',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select max(complaint_id) FROM lostcomplaint")
            rows = cur.fetchall()
            for row in rows:
                cid = row[0]
                break
        if cid is not None:
            cid += 1
        else:
            cid = 1
        dd = str(datetime.now())
        dd = dd.split(".")
        dd = dd[0]
        status = "<font size=3 color=red>Error in taking complaint</font>"
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'khoj',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO lostcomplaint VALUES('"+str(cid)+"','"+user+"','"+train+"','"+compartment+"','"+seat+"','"+desc+"','"+dd+"','Under Progress')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record Inserted")
        if db_cursor.rowcount == 1:
            status = "<font size=3 color=blue>Your Complaint Accepted<br/>Your complaint Id = "+str(cid)+"</font>"
        context= {'data': status}
        return render(request, 'UserScreen.html', context)

def AddPassenger(request):
    if request.method == 'GET':
        return render(request, 'AddPassenger.html', {})    

def AddPassengerAction(request):
    if request.method == 'POST':
        global user
        passenger = request.POST.get('name', False)
        train = request.POST.get('t1', False)
        compartment = request.POST.get('t2', False)
        seat = request.POST.get('t3', False)
        dd = request.POST.get('t4', False)
        contact = request.POST.get('t5', False)
        email = request.POST.get('t6', False)
        cid = "none"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'khoj',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select max(ticket_id) FROM addpassenger")
            rows = cur.fetchall()
            for row in rows:
                cid = row[0]
                break
        if cid is not None:
            cid += 1
        else:
            cid = 1
        status = "<font size=3 color=red>Error in taking complaint</font>"
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'khoj',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO addpassenger VALUES('"+str(cid)+"','"+passenger+"','"+train+"','"+compartment+"','"+seat+"','"+dd+"','"+contact+"','"+email+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record Inserted")
        if db_cursor.rowcount == 1:
            status = "<font size=3 color=blue>Your ticket confirmed<br/>Your ticket Id = "+str(cid)+"</font>"
        context= {'data': status}
        return render(request, 'AdminScreen.html', context)    

def VolunteerLogin(request):
    if request.method == 'GET':
        return render(request, 'VolunteerLogin.html', {})

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def UserLogin(request):
    if request.method == 'GET':
       return render(request, 'UserLogin.html', {})

def Signup(request):
    if request.method == 'GET':
       return render(request, 'Signup.html', {})

def AdminLogin(request):
    if request.method == 'GET':
        return render(request, 'AdminLogin.html', {})

def AddVolunteer(request):
    if request.method == 'GET':
       return render(request, 'AddVolunteer.html', {})

def encryptPassword(password):
    if os.path.exists("key/key.txt") == False:
        key = bcrypt.gensalt()
        with open("key/key.txt", "wb") as file:
            file.write(key)
        file.close()
    else:
        with open("key/key.txt", "rb") as file:
            key = file.read()
        file.close()
    hashed_password = bcrypt.hashpw(password.encode(), key)
    return hashed_password.decode()        

def AdminLoginAction(request):
    if request.method == 'POST':
        global user, usertype
        page = "AdminLogin.html"
        msg = "<font size=3 color=red>Invalid Login</font>"
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        if "admin" == username and "admin" == password:
            user = username
            page = "AdminScreen.html"
            msg = '<font size=3 color=blue>welcome '+username+"</font>"            		
        context= {'data':msg}
        return render(request, page, context)

def VolunteerLoginAction(request):
    if request.method == 'POST':
        global user, usertype
        page = "VolunteerLogin.html"
        msg = "<font size=3 color=red>Invalid Login</font>"
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        index = 0
        callack = request          
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'khoj',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select username, password FROM users where usertype='Volunteer'")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username and encryptPassword(password) == row[1]:
                    user = username
                    page = "VolunteerScreen.html"
                    msg = '<font size=3 color=blue>welcome '+username+"</font>"
                    break		
        context= {'data':msg}
        return render(request, page, context)    

def UserLoginAction(request):
    if request.method == 'POST':
        global user, usertype
        page = "UserLogin.html"
        msg = "<font size=3 color=red>Invalid Login</font>"
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        index = 0
        callack = request          
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'khoj',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select username, password FROM users where usertype='User'")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username and encryptPassword(password) == row[1]:
                    user = username
                    page = "UserScreen.html"
                    msg = '<font size=3 color=blue>welcome '+username+"</font>"
                    break		
        context= {'data':msg}
        return render(request, page, context)
        
def AddVolunteerAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        status = "none"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'khoj',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select username FROM users")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username:
                    status = "Username already exists"
                    break
        if status == "none":
            db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'khoj',charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO users VALUES('"+username+"','"+encryptPassword(password)+"','"+contact+"','"+email+"','"+address+"','Volunteer')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            print(db_cursor.rowcount, "Record Inserted")
            if db_cursor.rowcount == 1:
                status = "<font size=3 color=blue>New volunteer details added</font>"
        context= {'data': status}
        return render(request, 'AdminScreen.html', context)

def SignupAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        status = "none"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'khoj',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select username FROM users")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username:
                    status = "Username already exists"
                    break
        if status == "none":
            db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'khoj',charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO users VALUES('"+username+"','"+encryptPassword(password)+"','"+contact+"','"+email+"','"+address+"','User')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            print(db_cursor.rowcount, "Record Inserted")
            if db_cursor.rowcount == 1:
                status = "User Signup Task Completed"
        context= {'data': "<font size=3 color=blue>"+status+"</font>"}
        return render(request, 'Signup.html', context)
