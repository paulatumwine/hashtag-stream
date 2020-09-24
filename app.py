from flask import Flask,jsonify,request
from flask import render_template
import ast
import happybase

app = Flask(__name__)
labels = []
values = []


@app.route("/")
def get_chart_page():
	global labels,values
	labels = []
	values = []
	return render_template('chart.html', values=values, labels=labels)


@app.route('/refreshData')
def refresh_graph_data():
	global labels, values
	connection = happybase.Connection(host = 'localhost')
	table = connection.table('hashtags')
	labels = []
	values = []
	for key, data in table.rows([str(i) for i in range(0, 9)]):
		# print(key, data)
		labels.append(data['hashtag:name'])
		values.append(data['hashtag:count'])
	print("DEBUG: labels: {}, data: {}".format(str(labels), str(values)))
	return jsonify(sLabel=labels, sData=values)


@app.route('/updateData', methods=['POST'])
def update_data():
	global labels, values
	if not request.form or 'data' not in request.form:
		return "error",400
	labels = ast.literal_eval(request.form['label'])
	values = ast.literal_eval(request.form['data'])
	print("labels received: " + str(labels))
	print("data received: " + str(values))
	return "success",201


if __name__ == "__main__":
	app.run(host='localhost', port=5001)