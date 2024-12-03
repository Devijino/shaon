from flask import Flask, render_template_string
import requests
from datetime import datetime, timedelta
import pytz
from hdate import HDate

app = Flask(__name__)

@app.route("/")
def home():
    # קואורדינטות עבור פתח תקווה
    latitude = 32.08
    longitude = 34.87
    local_timezone = pytz.timezone("Asia/Jerusalem")
    now = datetime.now(local_timezone)
    date = now.strftime("%Y-%m-%d")

    # התחברות ל-API של Sunrise-Sunset
    url = "https://api.sunrise-sunset.org/json"
    params = {
        "lat": latitude,
        "lng": longitude,
        "date": date,
        "formatted": 0
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "OK":
            # זמני זריחה ושקיעה ב-UTC
            sunrise_utc = data["results"]["sunrise"]
            sunset_utc = data["results"]["sunset"]

            # המרת זמן UTC לזמן מקומי
            utc_time_sunrise = datetime.strptime(sunrise_utc, "%Y-%m-%dT%H:%M:%S+00:00")
            utc_time_sunset = datetime.strptime(sunset_utc, "%Y-%m-%dT%H:%M:%S+00:00")
            local_sunrise = utc_time_sunrise.astimezone(local_timezone)
            local_sunset = utc_time_sunset.astimezone(local_timezone)

            # תאריך עברי
            hebrew_date = str(HDate(now, hebrew=True))

            # שליחת הנתונים ל-HTML
            return render_template_string("""
                <!DOCTYPE html>
                <html lang="he">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>שעונים אלגנטיים</title>
                    <link href="https://fonts.googleapis.com/css2?family=Alef:wght@400;700&family=Roboto:wght@400;700&display=swap" rel="stylesheet">
                    <style>
                        body { 
                            font-family: 'Roboto', sans-serif; 
                            direction: rtl; 
                            text-align: center; 
                            background-color: #f5f5f5; 
                            margin: 0; 
                            padding: 0; 
                        }
                        h1 {
                            margin: 30px 0;
                            color: #2e7d32;
                            font-family: 'Alef', sans-serif;
                        }
                        .info {
                            margin: 10px 0 30px 0;
                            font-size: 1.2em;
                            color: #004d40;
                        }
                        .clocks {
                            display: flex;
                            justify-content: center;
                            gap: 40px;
                            flex-wrap: wrap;
                        }
                        .clock-container {
                            width: 300px;
                            height: 300px;
                            border: 8px solid #00796b;
                            border-radius: 50%;
                            background-color: #ffffff;
                            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2);
                            position: relative;
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                            align-items: center;
                            padding: 20px;
                            transition: background-color 0.5s, border-color 0.5s;
                        }
                        .clock-container.daylight {
                            background-color: #ffeb3b; /* צהוב לאור יום */
                            border-color: #fdd835;
                            color: #000000;
                        }
                        .clock-container.night {
                            background-color: #283593; /* כחול כהה ללילה */
                            border-color: #1a237e;
                            color: #ffffff;
                        }
                        .time-display {
                            font-size: 3em;
                            font-weight: bold;
                        }
                        .date-display {
                            position: absolute;
                            top: 20px;
                            font-size: 1em;
                            color: inherit;
                        }
                        .remaining {
                            margin-top: 15px;
                            font-size: 1em;
                            color: #ff5722;
                        }
                        .progress-container {
                            width: 80%;
                            height: 10px;
                            background-color: #ddd;
                            border-radius: 5px;
                            margin-top: 15px;
                            overflow: hidden;
                        }
                        .progress-bar {
                            height: 100%;
                            width: 0%;
                            background-color: #ff5722;
                            transition: width 1s linear;
                        }
                        .remaining-seconds {
                            margin-top: 10px;
                            font-size: 0.9em;
                            color: #555555;
                        }
                    </style>
                </head>
                <body>
                    <h1>תאריך עברי: {{ hebrew_date }}</h1>
                    <div class="info">
                        <p><strong>זריחה:</strong> {{ sunrise }}</p>
                        <p><strong>שקיעה:</strong> {{ sunset }}</p>
                    </div>
                    <div class="clocks">
                        <!-- שעון רגיל -->
                        <div id="regularClock" class="clock-container">
                            <div class="date-display">תאריך: טוען...</div>
                            <div class="time-display">טוען...</div>
                        </div>
                        <!-- שעון זמני -->
                        <div id="hebrewClock" class="clock-container">
                            <div class="date-display">תאריך: {{ hebrew_date }}</div>
                            <div class="time-display">טוען...</div>
                            <div class="remaining" id="remaining">טוען...</div>
                            <div class="progress-container">
                                <div class="progress-bar" id="progressBar"></div>
                            </div>
                            <div class="remaining-seconds" id="remainingSeconds">טוען...</div>
                        </div>
                    </div>
                    <script>
                        const sunrise = new Date("{{ sunrise }}");
                        const sunset = new Date("{{ sunset }}");
                        const nextSunrise = new Date(sunrise.getTime() + 24 * 60 * 60 * 1000); // זריחה של היום הבא

                        // פונקציה לחישוב הזמן הזמני
                        function calculateTemporaryTime(now, start, end) {
                            const duration = end - start; // אורך התקופה במילישניות
                            const elapsed = now - start;
                            const percentage = Math.max(0, Math.min((elapsed / duration) * 100, 100));
                            const remainingSeconds = Math.max(0, Math.floor((duration - elapsed) / 1000));
                            const temporaryHours = Math.floor(elapsed / (duration / 12));
                            const temporaryMinutes = Math.floor((elapsed % (duration / 12)) / (duration / 12 / 60));
                            return { temporaryHours, temporaryMinutes, percentage, remainingSeconds };
                        }

                        function updateClocks() {
                            const now = new Date();

                            // עדכון שעון רגיל
                            const regularClock = document.getElementById('regularClock');
                            regularClock.querySelector('.time-display').innerText = now.toLocaleTimeString('he-IL', { hour: '2-digit', minute: '2-digit' });
                            regularClock.querySelector('.date-display').innerText = `תאריך: ${now.toLocaleDateString('he-IL')}`;

                            let temporaryHours, temporaryMinutes, label, percentage, remainingSeconds;
                            const hebrewClock = document.getElementById('hebrewClock');

                            if (now >= sunrise && now < sunset) {
                                // שעות אור
                                const tempTime = calculateTemporaryTime(now, sunrise, sunset);
                                temporaryHours = tempTime.temporaryHours;
                                temporaryMinutes = tempTime.temporaryMinutes;
                                percentage = tempTime.percentage;
                                remainingSeconds = tempTime.remainingSeconds;
                                label = `שעות אור נותרו עד לשעות חושך (${percentage.toFixed(2)}%)`;
                                hebrewClock.classList.remove('night');
                                hebrewClock.classList.add('daylight');
                            } else {
                                // שעות חושך
                                const tempTime = calculateTemporaryTime(now, sunset, nextSunrise);
                                temporaryHours = tempTime.temporaryHours;
                                temporaryMinutes = tempTime.temporaryMinutes;
                                percentage = tempTime.percentage;
                                remainingSeconds = tempTime.remainingSeconds;
                                label = `שעות חושך נותרו עד לשעות אור (${percentage.toFixed(2)}%)`;
                                hebrewClock.classList.remove('daylight');
                                hebrewClock.classList.add('night');
                            }

                            // עדכון שעון זמני
                            hebrewClock.querySelector('.time-display').innerText = `${temporaryHours.toString().padStart(2, '0')}:${temporaryMinutes.toString().padStart(2, '0')}`;
                            hebrewClock.querySelector('.remaining').innerText = label;
                            hebrewClock.querySelector('.remaining-seconds').innerText = `שניות נותרות: ${remainingSeconds}`;

                            // עדכון פס האחוזים
                            const progressBar = document.getElementById('progressBar');
                            progressBar.style.width = `${percentage}%`;
                        }

                        // עדכון שעונים כל שנייה
                        setInterval(updateClocks, 1000);
                        updateClocks();
                    </script>
                </body>
                </html>
            """, sunrise=local_sunrise.strftime("%Y-%m-%dT%H:%M:%S"),
               sunset=local_sunset.strftime("%Y-%m-%dT%H:%M:%S"),
               hebrew_date=hebrew_date)
        else:
            return "<h1>אירעה שגיאה בקבלת הנתונים מה-API</h1>"
    except requests.RequestException as e:
        return f"<h1>אירעה שגיאה: {e}</h1>"

if __name__ == "__main__":
    app.run(debug=True)
