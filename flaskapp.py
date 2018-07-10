import boto3
import pymysql
from flask import Flask, render_template, request
from botocore.client import Config


ACCESS_KEY_ID = ''
ACCESS_SECRET_KEY = ''
BUCKET_NAME = ''


hostname = ''
username = ''
password = ''
database = ''
myConnection = pymysql.connect( host=hostname, user=username, passwd=password, db=database, autocommit = True, cursorclass=pymysql.cursors.DictCursor, local_infile=True)

print "Database Connected"

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/decider',methods=['POST'])
def decider():
    user = request.form['firstname']
    name = request.form['view']
    if (name == "view"):
        with myConnection.cursor() as cursor:
            view_sql = "select p.picid, p.title, p.image_url, p.last_modified_time, p.rating from Picture p"
            cursor.execute(view_sql)
            result = cursor.fetchall()
            print(result)
        return render_template('View.html', your_list=result,name_value=user)

    elif(name == "upload"):
        return render_template('upload.html', value=user)
    
    elif(name == "delete"):
        return render_template('Delete.html')

@app.route('/deletion',methods=['POST'])
def deletion_tab():
    title1 = request.form['title']
    with myConnection.cursor() as cursor:
            del_sql = "delete from Picture where title='"+title1+"'"
            print(del_sql)
	    cursor.execute(del_sql)
    return "Successfull"
	
 
@app.route('/view',methods=['POST'])
def view():
    with myConnection.cursor() as cursor:
        view_sql = "select p.picid, p.title, u.user_name, p.image_url, p.rating from Picture p join User u on p.owner_id=u.id"
        cursor.execute(view_sql)
        result = cursor.fetchall()
        print(result)

    return render_template('View.html', your_list=result)

@app.route('/ratingfetch', methods=['POST'])
def ratingfetch():
    #value2=0
    with myConnection.cursor() as cursor:
        for key,value in request.form.items():
            (key2,value2)=(key,value)
			
        current_rating=float(value2)
        sql = "select rating,no_of_ppl from Picture where picid="+key2
        cursor.execute(sql)
        result = cursor.fetchall()
        for row in result:
            print row
            previous_rating=float(row["rating"])
            print previous_rating
            no_ppl=int(row["no_of_ppl"])
            print previous_rating
            if (previous_rating == "null" or previous_rating=="None" or previous_rating == None ):
                previous_rating = 0

            if (no_ppl == "null" or no_ppl == "None" or no_ppl == None):
                no_ppl = 0

        print("testvvv")
        print(current_rating)
        print (no_ppl)
		#print(((previous_rating*no_ppl)+current_rating)/(no_ppl+1))
        weight_rating=float(((previous_rating*no_ppl)+current_rating)/(no_ppl+1))
        no_ppl=str(no_ppl+1)
        print("weight check")
        print(weight_rating)
        weight_r=str(weight_rating)
		#print(weight_r)
        sql1 = "update Picture set rating="+weight_r+",no_of_ppl="+no_ppl+" where picid="+key2
        print(sql1)
        result2 = cursor.execute(sql1)
        myConnection.commit()
        cursor.close()
    return render_template('Rated.html')

@app.route('/upload', methods=['POST'])
def upload():

    s3 = boto3.resource('s3', aws_access_key_id = ACCESS_KEY_ID, aws_secret_access_key= ACCESS_SECRET_KEY)

    f_name = request.form['title']  + ".JPG"
    s3.Bucket('s3').put_object(Key=f_name, Body=request.files['myfile'])
    for object in s3.Bucket('shilpashree-s3').objects.all():
       if (object.key == f_name):
           temp_file = object.key + '\t\t  ' + 'Size:  ' + str(object.size) + 'Last Updated ' + str(object.last_modified)

           #picid = "1"
           title = str(object.key)
           #rating = "2"
           image_url = "https://s3.us-east-2.amazonaws.com/s3/" + f_name
           print image_url
           #no_of_ppl = "5"
           last_modified_time = str(object.last_modified)
           image_size = str(object.size)
           #comments = "image is good!!!"
           #owner_id = "1"
           #insertQuery = "insert into Picture values ('" + picid + "','" + title + "','" + rating + "','" + image_url + "','" + no_of_ppl + "','" + last_modified_time + "','" + image_size + "','" + comments + "','" + owner_id + "')"
           sql ="Insert into Picture (title, image_url, last_modified_time,image_size,no_of_ppl,rating) values (%s, %s, %s, %s, %s, %s)"
           #print insertQuery
           print sql
           cur = myConnection.cursor()
           #cur.execute(insertQuery)
           cur.execute(sql, (title, image_url, last_modified_time, image_size, "0", "0"))
           myConnection.commit()
           cur.close()
           #return insertQuery
           return  render_template('index.html')

if __name__ == '__main__':
    app.run()
