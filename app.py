import os
import psycopg2
from dotenv import load_dotenv
from flask import request, Flask


load_dotenv()
DROP_SESSIONS = ("DROP TABLE IF EXISTS sessions")
DROP_WORKOUTS = ("DROP TABLE IF EXISTS workouts")

CREATE_SESSIONS_TABLE = ("CREATE TABLE IF NOT EXISTS sessions (id SERIAL PRIMARY KEY, user_id INT, date DATE,date_time TIME, type VARCHAR(255), duration TIME, calories_burned INT, notes VARCHAR(255));")
CREATE_WORKOUTS_TABLE = ("CREATE TABLE IF NOT EXISTS workouts (id SERIAL PRIMARY KEY, session_id INT, excersise_type VARCHAR(255), sets INT, reps INT, weight INT);")
INSERT_SESSION = ("INSERT INTO sessions (user_id, date,date_time , type, duration, calories_burned, notes) VALUES (%s,%s, %s, %s, %s, %s, %s) RETURNING id;")
INSERT_WORKOUT = ("INSERT INTO workouts (session_id, excersise_type, sets, reps, weight) VALUES (%s, %s, %s,%s, %s);")
SELECT_SESSIONS = ("SELECT * FROM sessions WHERE user_id = (%s);")
SELECT_WORKOUTS = ("SELECT * FROM workouts WHERE session_id = (%s);")


app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

with connection:
        with connection.cursor() as cursor:
            #cursor.execute(DROP_SESSIONS, DROP_WORKOUTS)
            cursor.execute(CREATE_SESSIONS_TABLE)
            cursor.execute(CREATE_WORKOUTS_TABLE)

@app.get('/session/<string:user_id>')
def get_session(user_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_SESSIONS, (user_id, ))
            sessions = cursor.fetchall()
            
            ls = []
            for session in sessions:
                id, user_id, date, date_time, type, duration, calories_burned, notes = session
                ls.append({
                    'id': id,
                    'date': str(date),
                    'date_time': str(date_time),
                    'user_id': user_id,
                    'type': type,
                    'duration': str(duration),
                    'calories_burned': calories_burned,
                    'notes': notes

                })
                cursor.execute(SELECT_WORKOUTS, (id, ))
                workouts = cursor.fetchall()
                excercises = []
                for workout in workouts:
                    id, session_id, excersise_type, sets, reps, weight = workout
                    excercises.append({
                        'id': id,
                        'session_id': session_id,
                        'excersise_type': excersise_type,
                        'sets': sets,
                        'reps': reps,
                        'weight': weight
                    })
                ls[-1]['workouts'] = excercises
            
            
            print(workouts)
            return ls

@app.post('/session')
def create_session():
    data = request.get_json()

    session = (data['user_id'], data['date'],data['date_time'], data['type'], data['duration'], data['calories_burned'], data['notes'])
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_SESSION, session)
            session_id = cursor.fetchone()[0]
    
    print(session)


    for workout in data['workouts']:
        workout = (session_id, workout['type'], workout['sets'], workout['reps'], workout['weight'])
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(INSERT_WORKOUT, workout)
        print(workout)

    return "Success"

if __name__ == '__main__':
    app.run(debug=True)


