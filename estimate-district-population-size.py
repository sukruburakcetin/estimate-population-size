"""
Author: @ Sukru Burak Cetin
Created Date: 08/06/2022
A simple linear Regression model to predict a district
population.
"""
import json
import warnings
import pandas as pd
from flask import Flask, flash, render_template, request
from sklearn.linear_model import LinearRegression

warnings.filterwarnings("ignore")

app = Flask(__name__)
app.secret_key = "imm-district-population-estimation-sukruburakcetin"


upper_map = {
    ord(u'ı'): u'I',
    ord(u'i'): u'İ'
}

lower_map = {
    ord(u'I'): u'ı',
    ord(u'İ'): u'i'
}

def country_list_gen(df):
    df.rename(columns={'Country Name': 'country_name'}, inplace=True)
    df['country_name'] = df['country_name'].apply(lambda row: row.translate(lower_map).lower())
    lists = df['country_name'].unique().tolist()
    with open('country_list.json', 'w', encoding='utf-8') as f:
        json.dump(lists, f, ensure_ascii=False, indent=4)
    return lists, df


def selecting_country(df, country):
    """
    this function will 
    """
    df = df.loc[df['country_name'] == country]
    df.drop(['country_name', 'Country Code', 'Indicator Name', 'Indicator Code'], axis=1, inplace=True)
    df = df.T
    df.dropna(inplace=True)
    df = df.reset_index()
    return df


def prediction_model(df):
    x = df.iloc[:, 0].values.reshape(-1, 1)
    y = df.iloc[:, 1].values.reshape(-1, 1)
    model = LinearRegression().fit(x, y)
    return model


def prediction(model, year):
    return int(model.coef_[0][0] * year + model.intercept_[0])


def main():
    country = input("Please input the district name: ").lower()
    year = int(input("Please input the year to predict: "))
    df = pd.read_excel('pop2.xlsx')
    lists, df = country_list_gen(df)
    if country in lists:
        df = selecting_country(df, country)
        model = prediction_model(df)
        result = prediction(model, year)
        print(f"\n Result: {country.upper()} population in {year} will be {result:,d}")
    else:
        print('kindly check available country name and thier spelling from country_list.json')


@app.route("/adreskisi", methods=['POST', 'GET'])
def greeter():
    if request.method == "POST":
        selected_district = request.form['districts'].translate(lower_map).lower()
        try:
            selected_year = int(request.form['year_input'])
            df = pd.read_excel('pop.xlsx')
            lists, df = country_list_gen(df)
            if selected_district in lists:
                df = selecting_country(df, selected_district)
                model = prediction_model(df)
                result = prediction(model, selected_year)
                # print(f"\n Result: {selected_district.upper()} population in {selected_year} will be {result:,d}")
            else:
                print('kindly check available country name and thier spelling from country_list.json')
            flash(f"{selected_year} yılı için {selected_district.translate(upper_map).upper()} nüfusunun {result} olacağı öngörülmektedir. ")
        except:
            flash(f"Lütfen yıl giriniz!")
        return render_template("index.html")
    else:
        return render_template("index.html")


app.config['JSON_AS_ASCII'] = False
app.run(host="0.0.0.0")

# if __name__ == "__main__":
#     main()
