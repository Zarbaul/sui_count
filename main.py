from flask import Flask, jsonify, request, render_template
import time
import threading

app = Flask(__name__)

#global vars for time tracking
start_time = None
counter_45 = 0
running = False
elapsed_time = 0
days = 0
years = 0
time_log = None
lock = threading.Lock()


def update_stopwatch():
    global start_time, running, elapsed_time, days, years

    while running:
        with lock:
            if start_time:
                elapsed_time = time.time() - start_time
                hours, remainder = divmod(elapsed_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                hundredths = int((seconds % 1) * 100)
                seconds = int(seconds)
                if hours <= 24:
                    days = int(hours // 24)
                    hours %= 24
                    if days >= 365:
                        years = days // 365
                        days %= 365
        time.sleep(0.01) #updates every 10 milliseconds


def update_45_counter():
    global counter_45
    while running:
        time.sleep(45)
        with lock:
            counter_45 += 1


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start():
    global start_time, running, counter_45, time_log
    with lock:
        if not running:
            running = True
            start_time = time.time()
            time_log = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
            threading.Thread(target=update_stopwatch).start()
            threading.Thread(target=update_45_counter).start()
        return jsonify({"message": "Timer started", "time_log": time_log})


@app.route("/status")
def status():
    with lock:
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        hundredths = int((seconds % 1 ) * 100)
        seconds = int(seconds)
        time_display = f"{int(hours):02}:{int(minutes):02}:{seconds:02}.{hundredths:02}:"
        return jsonify({
            "time": time_display,
            "days": days,
            "years": years,
            "counter_45": counter_45,
            "time_log": time_log
        })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

