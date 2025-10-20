from flask import Flask, render_template, jsonify, request
import statistics

app = Flask(__name__)

# Home page (optional)
@app.route('/')
def index():
    return render_template('registration.html')  # Directly serve the trigger page

# Trigger page route (same as above, just in case you want separate URL)
@app.route('/registration')
def trigger():
    return render_template('registration.html')


from flask import Flask, render_template, request, jsonify
import statistics

app = Flask(__name__)

@app.route('/')
def register():
    return render_template('registration.html')

@app.route('/verify_behavior', methods=['POST'])
def verify_behavior():
    data = request.get_json()

    if not data or 'behavior' not in data:
        return jsonify({'verified': False, 'reason': 'no data received'}), 400

    behavior = data['behavior']

    # --- Mouse variability score ---
    mouse = behavior.get('mouse', [])
    speeds = [m['speed'] for m in mouse if m['speed'] is not None]
    if speeds:
        std_speed = statistics.stdev(speeds) if len(speeds) > 1 else 0
        mouse_score = min(std_speed * 10, 1.0)  # scale
    else:
        mouse_score = 0.5
        std_speed = None

    # --- Typing variability score ---
    typing = behavior.get('typing', [])
    intervals = [t['interval'] for t in typing if t['interval'] is not None]
    if intervals:
        std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0
        typing_score = min(std_interval / 200, 1.0)  # scale
    else:
        typing_score = 0.5
        std_interval = None

    # --- Idle time score ---
    idle_times = behavior.get('idleTimes', [])
    long_pauses = [i['duration'] for i in idle_times if i['type'] == 'long']
    idle_score = 1.0 if long_pauses else 0.5

    # --- Weighted human score ---
    human_score = 0.5 * mouse_score + 0.4 * typing_score + 0.1 * idle_score
    verified = human_score >= 0.6

    # --- Debug info for frontend ---
    debug_data = {
        'mouse_count': len(mouse),
        'mouse_std_speed': round(std_speed, 3) if std_speed is not None else None,
        'mouse_score': round(mouse_score,2),
        'typing_count': len(typing),
        'typing_std_interval': round(std_interval, 2) if std_interval is not None else None,
        'typing_score': round(typing_score,2),
        'idle_times_count': len(idle_times),
        'long_idle_count': len(long_pauses),
        'idle_score': round(idle_score,2)
    }

    print("\n--- Behavior Data ---")
    print(debug_data)
    print("--------------------\n")

    return jsonify({
        'verified': verified,
        'score': round(human_score, 2),
        'debug_data': debug_data
    })

if __name__ == '__main__':
    app.run(debug=True)


@app.route("/behavior", methods=["POST"])
def behavior():
    data = request.get_json()
    print("Received behavior data:", data)  # Debugging output
    total_entries = sum(len(v) for v in data.values())
    return jsonify({"status": "ok", "entries": total_entries})














if __name__ == '__main__':
    app.run(debug=True)
