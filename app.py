from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/findresbyname')
def findresbyname():
    return render_template('find-res-by-name.html')


@app.route('/agerange')
def agerange():
    return render_template('age-range.html')


@app.route('/findpassbydate')
def findpassbydate():
    return render_template('find-pass-by-date.html')


@app.route('/findresbytrainname')
def findresbytrainname():
    return render_template('find-res-by-train.html')


@app.route('/newreservation', methods=['POST', 'GET'])
def newreservation():
    conn = sqlite3.connect('rrs.db')
    cur = conn.cursor()
    query = "Select userId from passenger;"
    cur.execute(query)
    rows = cur.fetchall()
    query1 = "Select train_number,train_name from train;"
    cur.execute(query1)
    rows1 = cur.fetchall()
    conn.close()
    return render_template('new-reservation.html', rows=rows, rows1=rows1)


@app.route('/cancelreservation', methods=['POST', 'GET'])
def cancelreservation():
    conn = sqlite3.connect('rrs.db')
    cur = conn.cursor()
    query = "Select userId from passenger;"
    cur.execute(query)
    rows = cur.fetchall()
    query1 = "Select train_number,train_name from train;"
    cur.execute(query1)
    rows1 = cur.fetchall()
    conn.close()
    return render_template('cancel-reservation.html', rows=rows, rows1=rows1)


@app.route('/findresbynameform', methods=['POST', 'GET'])
def findresbynameform():
    conn = sqlite3.connect('rrs.db')
    cur = conn.cursor()
    fname = request.form['fname']
    lname = request.form['lname']
    query = "SELECT  b.train_number,b.ticket_type,t.train_name from booked b JOIN  passenger p on b.passenger_ssn = p.ssn and UPPER(p.last_name) = '" + \
        lname.upper().strip()+"' and UPPER(p.first_name) = '"+fname.upper().strip() + \
            "' JOIN train t on b.train_number = t.train_number"
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return render_template('res-by-name-list.html', rows=rows)


@app.route('/findpassbydateform', methods=['POST', 'GET'])
def findpassbydateform():
    conn = sqlite3.connect('rrs.db')
    cur = conn.cursor()
    date = request.form['date']
    # query = "SELECT p.* from train_status ts  join train t on ts.train_name = t.train_name join booked b on b.train_number = t.train_number join passenger p on b.passenger_ssn = p.ssn where ts.train_date = '"+date+"'"
    query = "SELECT p.* from train_status ts,train t,booked b,passenger p where ts.train_date= '"+date + \
        "' and  trim(ts.train_name) = trim(t.train_name) and t.train_number = b.train_number and b.passenger_ssn = p.ssn and b.status='Confirmed';"
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return render_template('passenger-list.html', rows=rows)


@app.route('/train-passenger', methods=['POST', 'GET'])
def trainpassenger():
    conn = sqlite3.connect('rrs.db')
    cur = conn.cursor()
    query = "SELECT t.train_name, count(b.train_number) as count from train t left JOIN booked b on t.train_number = b.train_number GROUP by train_name HAVING count(b.train_number) >=0;"
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return render_template('train-passenger-list.html', rows=rows)


@app.route('/agerangeform', methods=['POST', 'GET'])
def agerangeform():
    conn = sqlite3.connect('rrs.db')
    cur = conn.cursor()
    minage = request.form['minage']
    maxage = request.form['maxage']
    query = "SELECT t.train_number,t.train_name,t.source,t.destination, p.first_name || ' ' || p.last_name as name, p.address || ', ' || p.city || ', ' ||p.county as address, b.ticket_type,b.status FROM passenger p join booked b on b.passenger_ssn = p.ssn join train t on t.train_number = b.train_number WHERE  Cast ((JulianDay('now','localtime') - JulianDay(p.dob))/365 As Integer) BETWEEN " + \
        minage+" AND "+maxage+";"
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return render_template('age-range-list.html', rows=rows)


@app.route('/findresbytrainnameform', methods=['POST', 'GET'])
def findresbytrainnameform():
    conn = sqlite3.connect('rrs.db')
    cur = conn.cursor()
    trainname = request.form['trainname']
    query = "select p.first_name,p.last_name from train t join booked b on t.train_number = b.train_number join passenger p on b.passenger_ssn = p.ssn where trim(UPPER(t.train_name)) = '"+trainname.upper(
    ).strip()+"' and b.status='Confirmed';"
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return render_template('find-res-by-train-list.html', rows=rows)


@app.route('/newreservationform', methods=['POST', 'GET'])
def newreservationform():
    conn = sqlite3.connect('rrs.db')
    cur = conn.cursor()
    userId = request.form['userId']
    train = request.form['train']
    type = request.form['type']
    query = "select * from train where train_number = "+train+";"
    cur.execute(query)
    rows = cur.fetchall()
    train_name = rows[0][1].strip()
    q1 = "select * from train_status where trim(train_name) = '"+train_name+"'"
    cur.execute(q1)
    rows1 = cur.fetchall()
    train_date = rows1[0][0]
    gen_ava_seats = rows1[0][3]
    general_seats_waitlist = rows1[0][7]
    q2 = "select ssn from passenger where userId = "+userId+""
    cur.execute(q2)
    rows2 = cur.fetchall()
    passenger_ssn = rows2[0][0]

    if type == 'Premium':
        pre_ava_seats = rows1[0][2]
        premium_seats_waitlist = rows1[0][6]
        if(pre_ava_seats > 0):
            q3 = "Update train_status set premium_seats_available = premium_seats_available-1,premium_seats_occupied = premium_seats_occupied+1 where trim(train_name) = '" + \
                train_name+"'"
            cur.execute(q3)
            conn.commit()
            q4 = "Insert into booked (passenger_ssn,Train_Number,ticket_type,doj,status) values ("+passenger_ssn + \
                ","+train+",'Premium','"+train_date+"','Confirmed')"
            cur.execute(q4)
            conn.commit()
            infoText = "Reservation Confirmed for Premium Class in Train " + \
                train_name+" on "+train_date+" for userId "+userId
        else:
            if premium_seats_waitlist < 2:
                q5 = "Update train_status set premium_seats_waitlist = premium_seats_waitlist +1 where trim(train_name) = '" + \
                    train_name+"'"
                cur.execute(q5)
                conn.commit()
                q6 = "Insert into booked (passenger_ssn,Train_Number,ticket_type,doj,status) values ("+passenger_ssn + \
                    ","+train+",'Premium','"+train_date+"','Waitlist')"
                cur.execute(q6)
                conn.commit()
                infoText = "User "+userId+" is placed on waitlist for Premium Class in Train " + \
                    train_name+" on "+train_date+"."
            elif premium_seats_waitlist >= 2:
                infoText = "Premium Class in Train "+train_name+" is full on "+train_date+"."
    elif type == 'General':
        if(gen_ava_seats > 0):
            q7 = "Update train_status set general_seats_available = general_seats_available-1 , general_seats_occupied = general_seats_occupied+1 where trim(train_name) = '" + \
                train_name+"'"
            cur.execute(q7)
            conn.commit()
            q8 = "Insert into booked (passenger_ssn,Train_Number,ticket_type,doj,status) values ("+passenger_ssn + \
                ","+train+",'General','"+train_date+"','Confirmed')"
            cur.execute(q8)
            conn.commit()
            infoText = "Reservation Confirmed for General Class in Train " + \
                train_name+" on "+train_date+" for user "+userId+"."
        else:
            if general_seats_waitlist < 2:
                q9 = "Update train_status set general_seats_waitlist = general_seats_waitlist +1 where trim(train_name) = '" + \
                    train_name+"'"
                cur.execute(q9)
                conn.commit()
                q10 = "Insert into booked (passenger_ssn,Train_Number,ticket_type,doj,status) values ("+passenger_ssn + \
                    ","+train+",'General','"+train_date+"','Waitlist')"
                cur.execute(q10)
                conn.commit()
                infoText = "User "+userId+" is placed on waitlist for General Class in Train " + \
                    train_name+" on "+train_date+"."
            elif general_seats_waitlist >= 2:
                infoText = "General Class in Train "+train_name+" is full on "+train_date+"."
    query2 = "Select userId from passenger;"
    cur.execute(query2)
    rows = cur.fetchall()
    query3 = "Select train_number,train_name from train;"
    cur.execute(query3)
    rows1 = cur.fetchall()
    conn.close()
    return render_template('new-reservation.html', infoText=infoText, rows=rows, rows1=rows1)


@app.route('/cancelreservationform', methods=['POST', 'GET'])
def cancelreservationform():
    conn = sqlite3.connect('rrs.db')
    cur = conn.cursor()
    userId = request.form['userId']
    train = request.form['train']
    type = request.form['type']
    query = "select * from train where train_number = "+train+";"
    cur.execute(query)
    rows = cur.fetchall()
    train_name = rows[0][1].strip()
    q1 = "select * from train_status where trim(train_name) = '"+train_name+"'"
    cur.execute(q1)
    rows1 = cur.fetchall()
    train_date = rows1[0][0]
    premium_seats_waitlist = rows1[0][6]
    general_seats_waitlist = rows1[0][7]
    q2 = "select ssn from passenger where userId = "+userId+""
    cur.execute(q2)
    rows2 = cur.fetchall()
    passenger_ssn = rows2[0][0]
    query2 = "Select userId from passenger;"
    cur.execute(query2)
    users = cur.fetchall()
    query3 = "Select train_number,train_name from train;"
    cur.execute(query3)
    trains = cur.fetchall()
    qe1 = "Select * from booked where passenger_ssn = "+passenger_ssn+" and train_number = " + \
        train+" and ticket_type = '"+type+"' and doj = '"+train_date+"' limit 1;"
    cur.execute(qe1)
    rows4 = cur.fetchall()
    if(len(rows4) == 0):
        infoText = "No such reservation exists for userId " + \
            userId+" in Train "+train_name+" on "+train_date+"."
        return render_template('cancel-reservation.html', infoText=infoText, rows=users, rows1=trains)
    elif(len(rows4) > 0):
        ticket_status = rows4[0][5]
        booked_id = str(rows4[0][0])
        delqu = "Delete from booked where id = "+booked_id+";"

        if type == 'Premium':

            if ticket_status == 'Confirmed':
                if premium_seats_waitlist > 0:
                    qu2 = "Update train_status set premium_seats_waitlist =  premium_seats_waitlist-1 where trim(train_name) = '" + \
                        train_name+"'"
                    cur.execute(qu2)
                    conn.commit()
                    qu3 = "Update booked set status = 'Confirmed' where id in (select id from booked where train_number = " + \
                        train+" and ticket_type = '"+type + \
                        "' and status='Waitlist' limit 1);"
                    cur.execute(qu3)
                    conn.commit()
                    cur.execute(delqu)
                    conn.commit()
                    infoText = "Reservation Cancelled for userId " + \
                        userId+" in Train "+train_name+" on "+train_date+"."
                elif premium_seats_waitlist == 0:
                    qu4 = "Update train_status set premium_seats_available = premium_seats_available+1 , premium_seats_occupied = premium_seats_occupied-1 where trim(train_name) = '" + \
                        train_name+"'"
                    cur.execute(qu4)
                    conn.commit()
                    cur.execute(delqu)
                    conn.commit()
                    infoText = "Reservation Cancelled for userId " + \
                        userId+" in Train "+train_name+" on "+train_date+"."
            elif ticket_status == 'Waitlist':
                qu8 = "Update train_status set premium_seats_waitlist =  premium_seats_waitlist-1 where trim(train_name) = '" + \
                    train_name+"'"
                cur.execute(qu8)
                conn.commit()
                cur.execute(delqu)
                conn.commit()
                infoText = "Reservation Cancelled for userId " + \
                    userId+" in Train "+train_name+" on "+train_date+"."

        elif type == 'General':
            if ticket_status == 'Confirmed':
                if general_seats_waitlist > 0:
                    qu5 = "Update train_status set  general_seats_waitlist =  general_seats_waitlist-1 where trim(train_name) = '" + \
                        train_name+"'"
                    cur.execute(qu5)
                    conn.commit()
                    qu6 = "Update booked set status = 'Confirmed' where id in (select id from booked where train_number = " + \
                        train+" and ticket_type = '"+type + \
                        "' and status='Waitlist' limit 1);"
                    cur.execute(qu6)
                    conn.commit()
                    cur.execute(delqu)
                    conn.commit()
                    infoText = "Reservation Cancelled for userId " + \
                        userId+" in Train "+train_name+" on "+train_date+"."
                elif general_seats_waitlist == 0:
                    qu7 = "Update train_status set general_seats_available = general_seats_available+1 , general_seats_occupied = general_seats_occupied-1 where trim(train_name) = '" + \
                        train_name+"'"
                    cur.execute(qu7)
                    conn.commit()
                    cur.execute(delqu)
                    conn.commit()
                    infoText = "Reservation Cancelled for userId " + \
                        userId+" in Train "+train_name+" on "+train_date+"."
            elif ticket_status == 'Waitlist':
                qu9 = "Update train_status set general_seats_waitlist =  general_seats_waitlist-1 where trim(train_name) = '" + \
                    train_name+"'"
                cur.execute(qu9)
                conn.commit()
                cur.execute(delqu)
                conn.commit()
                infoText = "Reservation Cancelled for userId " + \
                    userId+" in Train "+train_name+" on "+train_date+"."
        conn.close()
    return render_template('cancel-reservation.html', infoText=infoText, rows=users, rows1=trains)


if __name__ == '__main__':
    app.run()
