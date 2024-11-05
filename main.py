import requests
import json
from flask import Flask
from flask import render_template
from flask import request as freq
from datetime import datetime

app = Flask(__name__)


def get_curr():
    url = "https://api.nbrb.by/exrates/rates?periodicity=0"
    response = requests.get(url=url)
    if response.status_code != 404:
        return response.text


def write_to_file(file_name="currencies.json") -> None:
    with open(file=file_name, encoding="UTF-8", mode="w") as file:
        file.write(get_curr())
    print("Файл успешно записан")


def check_date():
    with open(file="currencies.json", encoding='UTF-8', mode='r') as file:
        data = json.loads(file.read())
        for i in data:
            if i["Date"][:10] == str(datetime.now())[:10]:
                pass
            else:
                write_to_file()


class GetData:
    @staticmethod
    def get_names():
        data_list = {"names": [], "currency": [], "cur_scale": []}
        with open(file="currencies.json", encoding="UTF-8", mode='r') as file:
            data = json.loads(file.read())
            for i in range(len(data)):
                data_list["names"].append(data[i]["Cur_Name"])
                data_list["currency"].append(data[i]["Cur_OfficialRate"])
                data_list["cur_scale"].append(data[i]["Cur_Scale"])
        return data_list


@app.route('/', methods=["GET", "POST"])
def index():
    if freq.method == 'GET':
        context = {"names": GetData.get_names()["names"]}
        return render_template(template_name_or_list="index.html", context=context)


@app.route("/form_processing", methods=["POST"])
def form_processing():
    try:
        if freq.method == "POST":
            ind_curr = GetData.get_names()["names"].index(freq.form.get("names"))
            context = {"names": freq.form.get("names"), "price": freq.form.get("price"),
                       "convert_price": GetData.get_names()["currency"][ind_curr] * float(freq.form.get("price")) /
                                        GetData.get_names()["cur_scale"][ind_curr]}
            return render_template(template_name_or_list="form_processing.html", context=context)
    except ValueError:
        context = {
            "error": "Такой валюты не существует, пожалуйста, вернитесь на главную страницу и выберите корректную валюту"}
        return render_template(template_name_or_list="errors.html", context=context)


if __name__ == "__main__":
    check_date()
    app.run(host='localhost', port=5000, debug=True)
