from flask import Flask, request, render_template, Response
app = Flask(__name__)


phone_1_action = 'music'
phone_2_action = 'light'


# import bluetooth
# nearby_devices = bluetooth.discover_devices(lookup_names=True)
# print("Found {} devices.".format(len(nearby_devices)))
#
# for addr, name in nearby_devices:
#     print("  {} - {}".format(addr, name))

@app.route('/')
def index():



    return render_template('settings.j2',
                           phone_1_action=phone_1_action,
                           phone_2_action=phone_2_action)


@app.route('/settings', methods=['POST'])
def settings():
    print(request.form)
    print('Settings Saved for Phone 1 Action', request.form['phone_1_action'])
    print('Settings Saved for Phone 2 Action', request.form['phone_2_action'])
    phone_1_action = request.form['phone_1_action']
    phone_2_action = request.form['phone_2_action']

    return render_template('settings.j2',
                           phone_1_action=phone_1_action,
                           phone_2_action=phone_2_action)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
