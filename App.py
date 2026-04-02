import json
import os
import math
import random
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "rounds.json")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Aviator Bot IA</title>
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Aviator Bot">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#000000">
    <link rel="apple-touch-icon" href="/icon.png">
    <link rel="manifest" href="/manifest.json">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #000;
            color: #fff;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            min-height: 100vh;
            padding: 16px;
        }
        .header {
            text-align: center;
            padding: 20px 0 16px;
            border-bottom: 1px solid #1a1a1a;
            margin-bottom: 20px;
        }
        .header h1 {
            font-size: 22px;
            font-weight: 700;
            color: #ff4d4d;
            letter-spacing: 1px;
        }
        .header p {
            font-size: 12px;
            color: #666;
            margin-top: 4px;
        }
        .section {
            background: #0d0d0d;
            border: 1px solid #1f1f1f;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
        }
        .section-title {
            font-size: 13px;
            font-weight: 600;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 12px;
        }
        .input-row {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .coeff-input {
            flex: 1;
            background: #111;
            border: 1px solid #2a2a2a;
            border-radius: 8px;
            color: #fff;
            font-size: 18px;
            padding: 12px 14px;
            outline: none;
            -webkit-appearance: none;
            appearance: none;
        }
        .coeff-input:focus {
            border-color: #ff4d4d;
        }
        .coeff-input::placeholder {
            color: #444;
            font-size: 14px;
        }
        .btn {
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            padding: 12px 16px;
            transition: opacity 0.2s;
            -webkit-tap-highlight-color: transparent;
        }
        .btn:active { opacity: 0.75; }
        .btn-add {
            background: #1a3a1a;
            color: #4cff4c;
            border: 1px solid #2a5a2a;
            white-space: nowrap;
        }
        .btn-predict {
            background: #ff4d4d;
            color: #fff;
            width: 100%;
            font-size: 16px;
            padding: 15px;
            border-radius: 10px;
            margin-top: 4px;
        }
        .btn-clear {
            background: #1a1a2e;
            color: #6666ff;
            border: 1px solid #2a2a5a;
            font-size: 12px;
            padding: 8px 14px;
            float: right;
        }

        /* Result */
        .result-box {
            background: #0d0d0d;
            border: 1px solid #2a2a2a;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            display: none;
        }
        .result-box.visible { display: block; }
        .signal-line {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 12px;
            background: #0a1a0a;
            border: 1px solid #1a3a1a;
            border-radius: 8px;
            margin-bottom: 12px;
        }
        .signal-label { font-size: 12px; color: #888; }
        .signal-value { font-size: 24px; font-weight: 800; color: #4cff4c; }
        .timing-box {
            padding: 10px 12px;
            border-radius: 8px;
            margin-bottom: 10px;
            text-align: center;
        }
        .timing-play { background: #0a1f0a; border: 1px solid #1a4a1a; }
        .timing-wait { background: #1f1a0a; border: 1px solid #4a3a0a; }
        .timing-after { background: #0a0a1f; border: 1px solid #1a1a4a; }
        .timing-label { font-size: 11px; color: #888; margin-bottom: 4px; }
        .timing-play .timing-value { font-size: 18px; font-weight: 800; color: #4cff4c; }
        .timing-wait .timing-value { font-size: 18px; font-weight: 800; color: #ffaa00; }
        .timing-after .timing-value { font-size: 16px; font-weight: 700; color: #6688ff; }
        .metric-row {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        .metric {
            flex: 1;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
        }
        .metric-reliability {
            background: #0a0a1f;
            border: 1px solid #1a1a4a;
        }
        .metric-insurance {
            background: #1a0a0a;
            border: 1px solid #4a1a1a;
        }
        .metric-label { font-size: 10px; color: #888; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
        .metric-value { font-size: 16px; font-weight: 700; }
        .metric-reliability .metric-value { color: #6688ff; }
        .metric-insurance .metric-value { color: #ff8866; }
        .metric-sub { font-size: 10px; color: #555; margin-top: 2px; }

        /* Historique */
        .rounds-list {
            max-height: 200px;
            overflow-y: auto;
        }
        .round-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 10px;
            border-radius: 6px;
            margin-bottom: 4px;
            font-size: 14px;
        }
        .round-high { background: #0a1a0a; color: #4cff4c; }
        .round-low { background: #1a0a0a; color: #ff6666; }
        .round-mid { background: #0a0a1a; color: #8888ff; }
        .round-num { color: #555; font-size: 11px; }
        .round-coeff { font-weight: 700; }
        .round-tag {
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 4px;
            background: rgba(255,255,255,0.05);
        }
        .empty-msg { text-align: center; color: #444; font-size: 13px; padding: 20px; }
        .count-info { color: #555; font-size: 12px; }

        /* Notification */
        .notif {
            position: fixed;
            top: 16px;
            left: 50%;
            transform: translateX(-50%);
            background: #1a3a1a;
            border: 1px solid #2a5a2a;
            color: #4cff4c;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 13px;
            display: none;
            z-index: 100;
        }
        .notif.error { background: #3a1a1a; border-color: #5a2a2a; color: #ff6666; }
        .loading { opacity: 0.6; pointer-events: none; }
    </style>
</head>
<body>

<div class="header">
    <h1>✈ AVIATOR BOT IA</h1>
    <p>Analyse probabiliste & Machine Learning</p>
</div>

<div id="notif" class="notif"></div>

<!-- Saisie du coefficient -->
<div class="section">
    <div class="section-title">Saisir un coefficient</div>
    <div class="input-row">
        <input type="text" id="coeffInput" class="coeff-input" placeholder="ex: 2.43" inputmode="decimal" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false">
        <button class="btn btn-add" onclick="addRound()">AJOUTER</button>
    </div>
</div>

<!-- Bouton prédiction -->
<div class="section">
    <button class="btn btn-predict" onclick="getPrediction()">🔮 OBTENIR LA PRÉDICTION</button>
</div>

<!-- Résultat -->
<div id="resultBox" class="result-box">
    <div class="signal-line">
        <div>
            <div class="signal-label">SIGNAL DÉTECTÉ</div>
        </div>
        <div class="signal-value" id="signalValue">--</div>
    </div>

    <div class="timing-box" id="timingBox">
        <div class="timing-label">TIMING</div>
        <div class="timing-value" id="timingValue">--</div>
    </div>

    <div class="metric-row">
        <div class="metric metric-reliability">
            <div class="metric-label">FIABILITÉ</div>
            <div class="metric-value" id="reliabilityValue">--%</div>
        </div>
        <div class="metric metric-insurance">
            <div class="metric-label">ASSURANCE</div>
            <div class="metric-value" id="insuranceValue">--x</div>
            <div class="metric-sub" id="insurancePct">--</div>
        </div>
    </div>
</div>

<!-- Historique -->
<div class="section">
    <div class="section-title">
        Historique
        <button class="btn btn-clear" onclick="clearRounds()">Effacer</button>
        <span class="count-info" id="countInfo"></span>
    </div>
    <div class="rounds-list" id="roundsList">
        <div class="empty-msg">Aucun round enregistré</div>
    </div>
</div>

<script>
function showNotif(msg, isError=false) {
    const n = document.getElementById('notif');
    n.textContent = msg;
    n.className = 'notif' + (isError ? ' error' : '');
    n.style.display = 'block';
    setTimeout(() => n.style.display = 'none', 2500);
}

function extractAllCoeffs(raw) {
    if (!raw) return [];
    const s = raw.replace(/,/g, '.');
    const matches = s.match(/\d+(?:\.\d+)?/g);
    if (!matches) return [];
    return matches.map(m => parseFloat(m)).filter(v => !isNaN(v) && v >= 1.00);
}

async function addRound() {
    const input = document.getElementById('coeffInput');
    const coeffs = extractAllCoeffs(input.value);
    if (coeffs.length === 0) {
        showNotif('Entrez au moins un coefficient ≥ 1.00 (ex: 2.43)', true);
        return;
    }
    try {
        const res = await fetch('/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({coefficients: coeffs})
        });
        const data = await res.json();
        if (data.success) {
            input.value = '';
            if (data.added === 0) {
                showNotif('Aucun nouveau round (déjà enregistrés)', false);
            } else if (data.added === 1) {
                showNotif('1 round ajouté. Total : ' + data.total);
            } else {
                showNotif(data.added + ' rounds ajoutés. Total : ' + data.total);
            }
            loadRounds();
        } else {
            showNotif(data.error || 'Erreur', true);
        }
    } catch(e) {
        showNotif('Erreur de connexion', true);
    }
}

async function getPrediction() {
    const btn = document.querySelector('.btn-predict');
    btn.classList.add('loading');
    btn.textContent = '⏳ Analyse en cours...';
    try {
        const res = await fetch('/predict');
        const data = await res.json();
        btn.classList.remove('loading');
        btn.textContent = '🔮 OBTENIR LA PRÉDICTION';

        if (!data.success) {
            showNotif(data.error || 'Erreur de prédiction', true);
            return;
        }

        document.getElementById('resultBox').classList.add('visible');
        document.getElementById('signalValue').textContent = data.predicted_value;

        const timingBox = document.getElementById('timingBox');
        const timingValue = document.getElementById('timingValue');
        timingValue.textContent = data.timing.label;
        timingBox.className = 'timing-box timing-' + data.timing.type;

        document.getElementById('reliabilityValue').textContent = data.reliability + '%';
        document.getElementById('insuranceValue').textContent = data.insurance.value + 'x';
        document.getElementById('insurancePct').textContent = 'Fiabilité : ' + data.insurance.reliability + '%';
    } catch(e) {
        btn.classList.remove('loading');
        btn.textContent = '🔮 OBTENIR LA PRÉDICTION';
        showNotif('Erreur de connexion', true);
    }
}

async function loadRounds() {
    try {
        const res = await fetch('/rounds');
        const data = await res.json();
        const list = document.getElementById('roundsList');
        const countInfo = document.getElementById('countInfo');

        if (!data.rounds || data.rounds.length === 0) {
            list.innerHTML = '<div class="empty-msg">Aucun round enregistré</div>';
            countInfo.textContent = '';
            return;
        }

        countInfo.textContent = '(' + data.rounds.length + ' rounds)';
        const items = [...data.rounds].reverse().map((r, i) => {
            const idx = data.rounds.length - i;
            let cls = 'round-mid';
            let tag = 'MOYEN';
            if (r < 2.0) { cls = 'round-low'; tag = 'BAS'; }
            else if (r >= 5.0) { cls = 'round-high'; tag = 'HAUT'; }
            else if (r >= 2.0 && r < 5.0) { cls = 'round-mid'; tag = r >= 3 ? 'BON' : 'OK'; }
            return '<div class="round-item ' + cls + '"><span class="round-num">#' + idx + '</span><span class="round-coeff">' + r.toFixed(2) + 'x</span><span class="round-tag">' + tag + '</span></div>';
        });
        list.innerHTML = items.join('');
    } catch(e) {}
}

async function clearRounds() {
    if (!confirm('Effacer tous les rounds ?')) return;
    try {
        await fetch('/clear', { method: 'POST' });
        showNotif('Historique effacé');
        document.getElementById('resultBox').classList.remove('visible');
        loadRounds();
    } catch(e) {
        showNotif('Erreur', true);
    }
}

document.getElementById('coeffInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') addRound();
});

loadRounds();

if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js', {scope: '/'})
        .catch(function(e) { console.log('SW:', e); });
}
</script>
</body>
</html>"""


def load_rounds():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def save_rounds(rounds):
    with open(DATA_FILE, "w") as f:
        json.dump(rounds, f)


def predict_with_ml(rounds):
    n = len(rounds)

    if n < 3:
        return None

    try:
        import numpy as np
        from sklearn.linear_model import LinearRegression
        from sklearn.ensemble import RandomForestRegressor

        X = np.array(range(n)).reshape(-1, 1)
        y = np.array(rounds)

        lr = LinearRegression()
        lr.fit(X, y)
        lr_pred = float(lr.predict([[n]])[0])

        if n >= 5:
            rf = RandomForestRegressor(n_estimators=50, random_state=42)
            rf.fit(X, y)
            rf_pred = float(rf.predict([[n]])[0])
            combined = lr_pred * 0.4 + rf_pred * 0.6
        else:
            combined = lr_pred

        combined = max(1.01, round(combined, 2))
        return combined

    except Exception:
        return None


def compute_prediction(rounds):
    n = len(rounds)
    if n == 0:
        return None

    last_10 = rounds[-10:] if n >= 10 else rounds

    avg = sum(last_10) / len(last_10)
    low_count = sum(1 for x in last_10 if x < 2.0)
    high_count = sum(1 for x in last_10 if x >= 5.0)

    ml_pred = predict_with_ml(rounds)

    if ml_pred is not None:
        base_pred = ml_pred
    else:
        base_pred = avg

    low_streak = 0
    for v in reversed(last_10):
        if v < 2.0:
            low_streak += 1
        else:
            break

    if low_streak >= 3:
        boost = 1.0 + (low_streak * 0.25)
        base_pred = max(base_pred, avg * boost)

    base_pred = round(max(1.01, base_pred), 2)

    low_ratio = low_count / len(last_10)
    high_ratio = high_count / len(last_10)
    consistency_bonus = 0

    if low_streak >= 3:
        reliability = min(92, 55 + low_streak * 10 + consistency_bonus)
    elif high_ratio > 0.3:
        reliability = min(88, 50 + int(high_ratio * 60))
    else:
        reliability = min(85, 45 + n * 2 + consistency_bonus)

    reliability = max(35, reliability)

    if low_streak >= 3:
        timing_type = "play"
        timing_label = "JOUER MAINTENANT"
    elif low_count == 0 and high_count >= 3:
        timing_type = "wait"
        timing_label = "ATTENDRE"
    elif low_streak == 0 and low_ratio > 0.4:
        rounds_wait = max(1, 3 - low_streak)
        timing_type = "after"
        timing_label = f"JOUER APRÈS {rounds_wait} ROUND(S)"
    else:
        timing_type = "play"
        timing_label = "JOUER MAINTENANT"

    insurance_value = round(max(1.10, min(base_pred * 0.65, base_pred - 0.5)), 2)
    insurance_reliability = min(97, reliability + 10)

    return {
        "predicted_value": f"{base_pred:.2f}x",
        "timing": {"type": timing_type, "label": timing_label},
        "reliability": reliability,
        "insurance": {"value": insurance_value, "reliability": insurance_reliability},
        "rounds_analyzed": len(last_10),
        "low_streak": low_streak,
    }


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/manifest.json")
def manifest():
    m = {
        "name": "Aviator Bot IA",
        "short_name": "Aviator Bot",
        "description": "Prédictions Aviator avec IA",
        "start_url": "/",
        "display": "standalone",
        "orientation": "portrait",
        "background_color": "#000000",
        "theme_color": "#ff4d4d",
        "icons": [
            {
                "src": "/icon.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable",
            },
            {
                "src": "/icon.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable",
            },
        ],
    }
    return jsonify(m)


@app.route("/icon.png")
def icon():
    import numpy as np
    import struct
    import zlib

    size = 192
    img = np.zeros((size, size, 3), dtype=np.uint8)
    cx, cy = size // 2, size // 2

    yy, xx = np.ogrid[:size, :size]
    dist2 = (xx - cx) ** 2 + (yy - cy) ** 2

    circle = dist2 <= (size // 2 - 4) ** 2
    img[circle] = [200, 30, 30]

    body = (np.abs(yy - cy) <= 9) & (xx >= cx - 48) & (xx <= cx + 58)
    img[body] = [255, 255, 255]

    wings = (np.abs(yy - cy) <= 26) & (np.abs(xx - cx) <= 18) & circle
    img[wings] = [255, 255, 255]

    tail = (np.abs(yy - cy) <= 16) & (xx >= cx + 35) & (xx <= cx + 58) & circle
    img[tail] = [255, 255, 255]

    rows = [b"\x00" + row.tobytes() for row in img]
    raw = b"".join(rows)
    compressed = zlib.compress(raw, 6)

    def chunk(name, data):
        c = name + data
        return (
            struct.pack(">I", len(data))
            + c
            + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        )

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", compressed)
    png += chunk(b"IEND", b"")

    from flask import Response

    return Response(
        png, mimetype="image/png", headers={"Cache-Control": "public, max-age=86400"}
    )


@app.route("/sw.js")
def service_worker():
    sw = """const CACHE = 'aviator-v2';
const SHELL = ['/', '/rounds'];

self.addEventListener('install', e => {
    e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)));
    self.skipWaiting();
});

self.addEventListener('activate', e => {
    e.waitUntil(caches.keys().then(keys =>
        Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ));
    self.clients.claim();
});

self.addEventListener('fetch', e => {
    const url = new URL(e.request.url);
    const bypass = ['/add', '/predict', '/clear', '/rounds'];
    if (e.request.method !== 'GET') return;
    if (bypass.some(p => url.pathname === p)) return;
    e.respondWith(
        fetch(e.request)
            .then(res => {
                const clone = res.clone();
                caches.open(CACHE).then(c => c.put(e.request, clone));
                return res;
            })
            .catch(() => caches.match(e.request))
    );
});
"""
    from flask import Response

    return Response(
        sw,
        mimetype="application/javascript",
        headers={"Service-Worker-Allowed": "/", "Cache-Control": "no-cache"},
    )


def deduplicate(existing, new_coeffs):
    """
    Détecte intelligemment les nouveaux rounds.
    Cherche le plus long suffixe de 'existing' qui correspond
    au début de 'new_coeffs', puis retourne uniquement la partie nouvelle.
    """
    if not existing or not new_coeffs:
        return new_coeffs

    def coeffs_match(a, b):
        return abs(a - b) < 0.005

    max_overlap = min(len(existing), len(new_coeffs))
    for overlap in range(max_overlap, 0, -1):
        tail = existing[-overlap:]
        head = new_coeffs[:overlap]
        if all(coeffs_match(a, b) for a, b in zip(tail, head)):
            return new_coeffs[overlap:]

    return new_coeffs


@app.route("/add", methods=["POST"])
def add_round():
    try:
        body = request.get_json(force=True)

        # Accepte soit un tableau, soit un seul coefficient (rétrocompatibilité)
        if "coefficients" in body:
            raw_list = body["coefficients"]
            new_coeffs = [round(float(c), 2) for c in raw_list if float(c) >= 1.00]
        elif "coefficient" in body:
            c = float(body["coefficient"])
            if c < 1.00:
                return jsonify(
                    {"success": False, "error": "Coefficient doit être ≥ 1.00"}
                ), 400
            new_coeffs = [round(c, 2)]
        else:
            return jsonify({"success": False, "error": "Données manquantes"}), 400

        if not new_coeffs:
            return jsonify(
                {"success": False, "error": "Aucun coefficient valide (≥ 1.00)"}
            ), 400

        existing = load_rounds()
        to_add = deduplicate(existing, new_coeffs)

        existing.extend(to_add)
        if len(existing) > 1000:
            existing = existing[-1000:]
        save_rounds(existing)

        return jsonify(
            {
                "success": True,
                "added": len(to_add),
                "total": len(existing),
                "skipped": len(new_coeffs) - len(to_add),
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/predict")
def predict():
    try:
        rounds = load_rounds()
        if len(rounds) < 3:
            return jsonify(
                {
                    "success": False,
                    "error": f"Données insuffisantes. Ajoutez au moins 3 rounds (actuellement : {len(rounds)})",
                }
            ), 200

        result = compute_prediction(rounds)
        if result is None:
            return jsonify(
                {"success": False, "error": "Impossible de calculer la prédiction"}
            ), 200

        result["success"] = True
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/rounds")
def get_rounds():
    rounds = load_rounds()
    return jsonify({"rounds": rounds, "total": len(rounds)})


@app.route("/clear", methods=["POST"])
def clear_rounds():
    save_rounds([])
    return jsonify({"success": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port, debug=False)
