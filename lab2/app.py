from flask import Flask, render_template, request, make_response, redirect, url_for
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/url_params')
def url_params():
    return render_template('url_params.html', params=request.args)

@app.route('/headers')
def headers():
    return render_template('headers.html', headers=dict(request.headers))

@app.route('/cookies')
def cookies():
    response = make_response(render_template('cookies.html', cookies=request.cookies))
    
    if 'some_cookie' not in request.cookies:
        response.set_cookie('some_cookie', '12345')
    else:
        response.delete_cookie('some_cookie')
    
    return response

@app.route('/form_params', methods=['GET', 'POST'])
def form_params():
    if request.method == 'POST':
        return render_template('form_params.html', form_data=request.form)
    return render_template('form_params.html')

@app.route('/phone', methods=['GET', 'POST'])
def phone():
    error_message = None
    formatted_phone = None

    if request.method == 'POST':
        phone_input = request.form.get('phone', '')

        if not phone_input:
            error_message = 'Ошибка: неверное количество цифр.'
        elif not re.match(r'^[\d\s()\-\.+]+$', phone_input):
            error_message = 'Ошибка: номер телефона содержит недопустимые символы.'
        else:
            digits_only = re.sub(r'[^\d]', '', phone_input)

            if len(digits_only) == 11:
                if digits_only[0] in ['7', '8']:
                    digits_only = digits_only[1:]
                    formatted_phone = f"8-{digits_only[:3]}-{digits_only[3:6]}-{digits_only[6:8]}-{digits_only[8:]}"
                else:
                    error_message = 'Ошибка: неверное количество цифр.'
            elif len(digits_only) == 10:
                formatted_phone = f"8-{digits_only[:3]}-{digits_only[3:6]}-{digits_only[6:8]}-{digits_only[8:]}"
            else:
                error_message = 'Ошибка: неверное количество цифр.'

    return render_template('phone.html', error=error_message, formatted_number=formatted_phone)
