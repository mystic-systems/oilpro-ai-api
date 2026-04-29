from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf
import requests
import numpy as np

app = Flask(__name__)
CORS(app)

# -----------------------
# MARKET DATA
# -----------------------

def get_usd():
    data = yf.download("DX-Y.NYB", period="1d", interval="5m")
    return float(data["Close"].iloc[-1]) if len(data) else 100

def get_oil():
    data = yf.download("CL=F", period="1d", interval="5m")
    return float(data["Close"].iloc[-1]) if len(data) else 70

# -----------------------
# FACTORS
# -----------------------

def score_opec(oil):
    return (oil - 70) / 2

def score_usd(usd):
    return -(usd - 100) / 2

def score_fed():
    return -0.5

def score_demand(oil):
    return (75 - oil) / 3

def score_geo():
    try:
        url = "https://api.gdeltproject.org/api/v2/doc/doc?query=war&mode=ArtList&format=json"
        r = requests.get(url, timeout=3)
        data = r.json()
        return min(len(data.get("articles", [])) / 5, 5)
    except:
        return 1

# -----------------------
# API
# -----------------------

@app.route("/signals")
def signals():

    oil = get_oil()
    usd = get_usd()

    opec = score_opec(oil)
    usd_s = score_usd(usd)
    fed = score_fed()
    demand = score_demand(oil)
    geo = score_geo()

    mix = opec + usd_s + fed + demand + geo

    return jsonify({
        "oil_price": oil,
        "usd_price": usd,

        "opec": round(opec, 2),
        "usd": round(usd_s, 2),
        "fed": round(fed, 2),
        "demand": round(demand, 2),
        "geo": round(geo, 2),

        "mix": round(mix, 2)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)