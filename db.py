import csv
import sqlite3

con = sqlite3.connect("rrs.db")
cur = con.cursor()
cur.execute(
    "CREATE TABLE train (train_number int auto_increment, train_name text unique not null, prem_fair double not null, gen_fair double not null, source text not null, destination text not null, avaiable_on text not null, primary key(train_number));")

with open('Train.csv', 'r') as train:
    dr = csv.DictReader(train)
    to_db = [(i['Train Number'], i[' Train Name'], i['Premium Fair'], i[' General Fair'], i[' Source Station'],
              i[' Destination Station'], i[' Available on']) for i in dr]

cur.executemany(
    "INSERT INTO train (train_number, train_name,prem_fair,gen_fair,source,destination,avaiable_on) VALUES (?, ?,?, ?,?, ?,?);", to_db)


cur.execute("Create table train_status (train_date date not null, train_name text not null,premium_seats_available int default 10, general_seats_available int default 10, premium_seats_occupied int default 0, general_seats_occupied int default 0, premium_seats_waitlist int default 0, general_seats_waitlist int default 0 ,primary key (train_date, train_name), FOREIGN KEY (train_name) REFERENCES train(train_name));")

with open('Train_status.csv', 'r') as train_status:
    dr1 = csv.DictReader(train_status)
    to_db1 = [(i['TrainDate'], i['TrainName'], i['PremiumSeatsAvailable'], i['GenSeatsAvailable'], i['PremiumSeatsOccupied'],
              i['GenSeatsOccupied'], i['PremiumSeatsWaitlist'], i['GenSeatsWaitlist']) for i in dr1]

cur.executemany(
    "INSERT INTO train_status (train_date,train_name,premium_seats_available,general_seats_available,premium_seats_occupied,general_seats_occupied,premium_seats_waitlist,general_seats_waitlist) VALUES (?, ?,?, ?,?, ?,?,?);", to_db1)


cur.execute("Create table booked (id integer ,passenger_ssn char(9) not null, Train_Number int not null, ticket_type text not null,doj date not null, status text not null,foreign key (train_number) references train(train_number), primary key(id)) ")

with open('booked.csv', 'r') as booked:
    dr2 = csv.DictReader(booked)
    to_db2 = [(j['passenger_ssn'], j['Train_Number'], j['Ticket_Type'], j['doj'], j['status'], j['id'])
              for j in dr2]

cur.executemany(
    "Insert into booked (passenger_ssn,train_number,ticket_type,doj,status,id) values (?,?,?,?,?,?);", to_db2)


cur.execute("Create table passenger (first_name text not null, last_name text not null, ssn char(9) not null,dob date not null,address text not null, city text not null,county text not null,userId int  auto_increment unique,phone varchar(12) not null,primary key (ssn), foreign key (ssn) references booked(passenger_ssn))")

with open('Passenger.csv', 'r') as passenger:
    dr3 = csv.DictReader(passenger)
    to_db3 = [(i['first_name'], i['last_name'], i['address'],
               i['city'], i['county'], i['phone'], i['SSN'], i['DOB'], i['userId']) for i in dr3]

cur.executemany(
    "Insert into passenger (first_name,last_name,address,city,county,phone,ssn,dob,userId) values (?,?,?,?,?,?,?,?,?);", to_db3)


con.commit()
con.close()
