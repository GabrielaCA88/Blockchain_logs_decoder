from flask import Flask, request, render_template
from decoder import Decoder

import json
app = Flask(__name__)

decoder = Decoder()

@app.route('/', methods=["GET", "POST"])
def getfunction():
    if request.method == "POST":
        data_d = request.form.get("datatext")
        data = decoder.clean_input(data_d)
        topics_d = request.form.get("topicstext").split(",")
        topics = decoder.clean_input(topics_d)
        abi = request.form.get("abitext")
        decoded = decoder.decode_log(data, topics, abi)
        to_json= 'function called: ', decoded[0], 'arguments: ', json.dumps(json.loads(decoded[1]), indent=2)
        return json.dumps(to_json)

    return render_template("form.html")

if __name__ == '__main__':
    app.run()