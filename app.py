from flask import Flask, render_template
import pymysql

app = Flask(__name__)

DB_HOST = "4.217.192.250"
DB_USER = "socuser"
DB_PASS = "socpassword"
DB_NAME = "socweb"

@app.route('/')
def home():

    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )

        cursor = conn.cursor()
        cursor.execute("SELECT NOW()")
        result = cursor.fetchone()

        conn.close()

        return render_template(
            "index.html",
            db_status="connected",
            time=result[0]
        )

    except Exception as e:

        return render_template(
            "index.html",
            db_status="failed",
            error=str(e)
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
