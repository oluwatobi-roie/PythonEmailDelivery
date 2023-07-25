from datetime import datetime, timedelta
import mysql.connector
import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from credential import *  # Use this when you are importing credential from another py file

# Declare universal variables here

# mailServer = Credential_roieServer
# From = Credential_roieEmail
# Pass = Credential_roiePassword

mailServer = Credential_gmail_Server
From = Credential_Gmail
Pass = Credential_Gmail_password

Port = Credential_Port
Bcc = Credential_Bcc


def logContent(myMessage):
    date = datetime.now()
    day = date.day
    month = date.month
    year = date.year
    filename = (str(month) + str(day) + str(year) + 'email-log.log')
    f = open(filename, "a")
    f.write(str(date.time())[:8] + ": " + myMessage + '\n')
    f.close()


def CreatesqliteDB():
    ContactMonitor = sqlite3.connect('recentContact.db')
    try:
        ContactMonitor.execute("CREATE TABLE recent("
                               "userID INTEGER PRIMARY KEY NOT NULL,"
                               "timeAdded TIMESTAMP NOT NULL);")
        ContactMonitor.commit()
        logContent("SQL lite Database Created")
        logContent("recent Table Created")
    except Exception as e:
        logContent(str(e))


#     we are trying to insert each user with the time an email was last sent to db
def insertRecent(uid):
    now = datetime.now()
    C_monitor = sqlite3.connect('recentContact.db')
    logContent("Trying to insert value...")
    insert_command = ("INSERT INTO recent(userID, timeAdded) VALUES({},'{}');".format(uid, now))
    try:
        C_monitor.execute(insert_command)
        C_monitor.commit()
        logContent("successfully inserted into sqliteDB")
    except sqlite3.IntegrityError:
        logContent('Item already exist in sqlite')


# delete old records of users that has been sent messages within the last 7 days
def DeleteOldrecords():
    C_monitor = sqlite3.connect('recentContact.db')
    now = datetime.now()
    count = 0

    logContent("Checking for older Records...")
    list = C_monitor.execute("SELECT * FROM recent WHERE timeAdded <'{}';".format(now - timedelta(days=7)))
    for i in list:
        logContent(str(i))
        count += 1
    if count > 0:
        try:
            C_monitor.execute("DELETE FROM recent WHERE timeAdded<'{}';".format(now - timedelta(days=7)))
            C_monitor.commit()
            logContent("old items successfully purged\n")
        except Exception as e:
            logContent('Something went wrong(delete Execute): ' + str(e))
    else:
        logContent("No older records to Delete")


# check to know if a user has recently been sent message within the last 7 days
def isrecent(i, Date):
    C_monitor = sqlite3.connect('recentContact.db')
    recentList = C_monitor.execute("SELECT * FROM recent")
    available = 0
    for j in recentList:
        if i == j[0]:
            available += 1
    if isUrgent(Date):
        return False
    elif available > 0:
        return True
    else:
        return False


def isUrgent(date):
    today = datetime.now()
    daysLeft = (date - today).days
    if daysLeft <= 3:
        return True
    else:
        return False


# Get a list of devices attached to a user and export as html
def userDeviceList(nList, uList):
    Devicetable = '<table><tr>' \
                  '<th> Device Name </th>' \
                  '<th> Last Update </th>' \
                  '</tr>'

    for i in range(len(nList)):
        Devicetable += '<tr> <td>{}</td>' \
                       '<td>{}</td> </tr>'.format(nList[i], uList[i])

    Devicetable += '</table>'

    return Devicetable


# still have to work on the subject of the email to show urgency
def sendEmail(Email, Name, Date, NameList, UpdateList, Uid):
    logContent("Trying to send an Email " + str(Date))
    To = Email
    msg = MIMEMultipart()  # this internal function is used to create header and subject for the email
    msg['Subject'] = 'GPS Tracking Data Expiring in {} Day'.format((Date - datetime.now()).days)
    msg['From'] = From
    msg['To'] = To

    Message = "<strong>Dear {}</strong>" \
              "<br>" \
              "<p>I hope this email finds you in good health and high spirits. </p>" \
              "{}<br><br>" \
              "<br> <strong>Kind Regards</strong><p>name</p><p>phone</p>".format(Name, userDeviceList(NameList, UpdateList))

    msg.attach(MIMEText(Message, 'html'))

    try:
        logContent("Initializing Server...")
        Server = smtplib.SMTP(mailServer, Port)
        Server.set_debuglevel(1)
        Server.ehlo()
        Server.starttls()
        Server.login(From, Pass)
        Server.sendmail(From, To, msg.as_string())
        logmessage = ("Email successfully sent to {}\n".format(Name))
        logContent(logmessage)
        Server.quit()
        insertRecent(Uid)
        return 1
    except Exception as e:
        logContent("Server could not be started and emailed failed to send because " + str(e) + "\n")
        return 0


# sends Urgent Email to customer regardeless if they have recently been contacted
def sendUrgentEmail(Email, Name, Date, NameList, UpdateList, Uid):
    logContent("Trying to send an Urgent Email " + str(Date))
    To = Email
    days = (Date - datetime.now()).days
    msg = MIMEMultipart()  # this internal function is used to create header and subject for the email
    if days < 2:
        msg['Subject'] = 'Urgent  GPS Data Expiring Today!!!'
    elif days < 3:
        msg['Subject'] = 'Urgent  GPS Data Expiring Soon'
    else:
        msg['Subject'] = 'Urgent 3Days Validity Remaining on your GPS'
    msg['From'] = From
    msg['To'] = To

    Message = "<strong>Dear {}</strong>" \
              "<br>" \
              "<p>I hope this email finds you in good health and high spirits. " \
              "{}<br><br>" \
              "<br> <strong>Kind Regards</strong><p>Company Name</p><p>+Phone</p>".format(Name, userDeviceList(NameList, UpdateList))

    msg.attach(MIMEText(Message, 'html'))

    try:
        logContent("Initializing Server...")
        Server = smtplib.SMTP(mailServer, Port)
        Server.set_debuglevel(1)
        Server.ehlo()
        Server.starttls()
        Server.login(From, Pass)
        Server.sendmail(From, To, msg.as_string())
        logmessage = ("Urgent Email successfully sent to {}\n".format(Name))
        logContent(logmessage)
        Server.quit()
        insertRecent(Uid)
        return 1
    except Exception as e:
        logContent("Server could not be started and emailed failed to send because " + str(e) + "\n")
        return 0


def main():
    logContent("Starting...")
    CreatesqliteDB()
    DeleteOldrecords()
    logContent("trying to Connect to Roie SQL DB...")
    mydb = mysql.connector.connect(
        host=Credential_IP,
        user=Credential_TraccarUser,
        password=Credential_TraccarPass,
        database=Credential_TraccarDB
    )
    total_email_sent = 0
    try:
        if mydb:
            logContent("Successfully connected to Roie DB")
            # customer details extraction
            CustomerCursor = mydb.cursor()
            CustomerCursor.execute("SELECT * FROM tc_users WHERE expirationtime >'{}' and expirationtime <'{}'".
                                   format(datetime.now(), datetime.now() + timedelta(days=10)))

            # this code below helps us target accounts that expired 20days ago.
            # CustomerCursor.execute("SELECT * FROM tc_users WHERE expirationtime >='{}' and expirationtime <'{}'".
            #                        format(datetime.now() - timedelta(days=20), datetime.now()))

            ExpiredCustomer = CustomerCursor.fetchall()

            # device Details Extraction
            DeviceCursor = mydb.cursor()
            DeviceCursor.execute("SELECT * FROM tc_devices")
            AllDevice = DeviceCursor.fetchall()

            logContent("**** Extracting User Data ****")
            for user in ExpiredCustomer:
                Uid = user[0]
                Phone = user[19]
                Email = user[2]
                Name = user[1]
                Date = user[15]

                # check if user has been recently contacted
                if isrecent(Uid, Date):
                    logContent("User has recently been contacted")
                else:
                    # user devices Details Extraction
                    userDeviceCursor = mydb.cursor()
                    userDeviceCursor.execute("SELECT * FROM tc_user_device WHERE userid={}".format(Uid))
                    userDevice = userDeviceCursor.fetchall()
                    nameList = []
                    updateList = []
                    for device in userDevice:
                        deviceid = device[1]
                        for allDevice in AllDevice:
                            if deviceid == allDevice[0]:
                                deviceName = allDevice[1]
                                devicelastUpdate = allDevice[3]
                                nameList.append(deviceName)
                                if devicelastUpdate == '':
                                    updateList.append('N/A')
                                else:
                                    updateList.append(devicelastUpdate)
                    if isUrgent(Date):
                        total_email_sent += sendUrgentEmail(Email, Name, Date, nameList, updateList, Uid)
                    else:
                        total_email_sent += sendEmail(Email, Name, Date, nameList, updateList, Uid)
                    logmessage = ("Name= {}\nPhone= {}\nEmail= {}\nExpiringDate= {}".
                                  format(Name, Phone, Email, Date))
                    logContent(logmessage)
        else:
            logContent("something went wrong at try connection")
    except Exception as e:
        logContent("Cant Connect to Database " + str(e))
    finally:
        mydb.close()
        logContent("Total Email sent=: " + str(total_email_sent))
        logContent("All connections closed.\n\n\n\n")


if __name__ == '__main__':
    main()
