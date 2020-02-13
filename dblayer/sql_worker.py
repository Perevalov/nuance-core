import random
import uuid
from datetime import datetime
import pytz
import sqlite3
from resources.constants import QUESTION_TYPE
from config import DB_PATH


class SQLWorker:
    def __init__(self):
        pass
        #self.connection = sqlite3.connect(DB_PATH)

    def create_dialogue(self, dialogue_id):
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            dt = datetime.now()
            #timezone = pytz.timezone(time_zone)
            # dt = timezone.localize(dt)
            dt_string = dt.strftime("%Y-%m-%d %H:%M:%S")

            sql = "INSERT INTO dialogue (id, date_started) " \
                  "VALUES (?,?)"
            cursor.execute(sql, (dialogue_id, dt_string,))

            connection.commit()
            cursor.close()
            return dialogue_id

    def create_message(self, dialogue_id, message_text, message_type, annotation, uri=None):
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            dt = datetime.now()
            # timezone = pytz.timezone(time_zone)
            # dt = timezone.localize(dt)
            dt_string = dt.strftime("%Y-%m-%d %H:%M:%S")

            # insert message
            message_id = uuid.uuid4().__str__()
            sql = "INSERT INTO message (id, text, type_id, annotation, date, dialogue_id, uri) " \
                  "VALUES (?,?,?,?,?,?,?)"
            cursor.execute(sql, (message_id, message_text, message_type, annotation, dt_string, dialogue_id, str(uri)))

            connection.commit()
            cursor.close()
            return message_id

    def update_answer_for_question(self, answer_id, message_id):
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()

            sql = "UPDATE message SET answer_id=? WHERE id=?"
            cursor.execute(sql, (answer_id, message_id,))

            connection.commit()
            cursor.close()
            return message_id

    def get_last_question(self, dialogue_id):
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()

            sql = "SELECT text, annotation, answer_id, date " \
                  "FROM message " \
                  "WHERE dialogue_id=? AND type_id=? " \
                  "ORDER BY date DESC " \
                  "LIMIT 1 OFFSET 1"
            cursor.execute(sql, (dialogue_id, QUESTION_TYPE,))

            result = cursor.fetchall()

            if result:
                cursor.close()
                return {"text": result[0][0], "annotation": result[0][1], "answer_id": result[0][2]}
            cursor.close()
            return None

    def get_message(self, message_id):
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()

            sql = "SELECT text, type_id, annotation, answer_id, date, dialogue_id " \
                  "FROM message " \
                  "WHERE id=? "
            cursor.execute(sql, (message_id,))

            result = cursor.fetchall()

            if result:
                cursor.close()
                return {"text": result[0][0], "type_id": result[0][1], "annotation": result[0][2]}
            cursor.close()
            return None

    def is_dialogue_exists(self, dialogue_id):
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()

            sql = "SELECT * " \
                  "FROM dialogue " \
                  "WHERE id=? "
            cursor.execute(sql, (dialogue_id,))

            result = cursor.fetchall()

            if result:
                cursor.close()
                return True
            cursor.close()
            return False
