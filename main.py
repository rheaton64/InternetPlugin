from flask import Flask, send_file
from flask_restx import Api, Resource, fields
from flask_cors import CORS
import yaml
from flask import make_response

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://chat.openai.com"}})
api = Api(app, version='v1', title='TODO Plugin', description='A plugin that allows the user to create and manage a TODO list using ChatGPT. If you do not know the user\'s username, ask them first before making queries to the plugin. Otherwise, use the username "global".')

# Keep track of todo's. Does not persist if Python session is restarted.
_TODOS = {}

todo_ns = api.namespace('todos', description='TODO operations')

todo = api.model('Todo', {
    'todo': fields.String(required=True, description='The todo to add to the list.'),
})

todo_list = api.model('TodoList', {
    'todos': fields.List(fields.String, description='The list of todos.'),
})

todo_delete = api.model('TodoDelete', {
    'todo_idx': fields.Integer(required=True, description='The index of the todo to delete.'),
})

@todo_ns.route('/<string:username>')
@api.doc(params={'username': 'The name of the user.'})
class TodoResource(Resource):
    @api.doc('get_todos')
    @api.marshal_with(todo_list)
    def get(self, username):
        '''Get the list of todos'''
        return {'todos': _TODOS.get(username, [])}, 200

    @api.doc('add_todo')
    @api.expect(todo, validate=True)
    def post(self, username):
        '''Add a todo to the list'''
        _TODOS.setdefault(username, []).append(api.payload['todo'])
        return 'OK', 200

    @api.doc('delete_todo')
    @api.expect(todo_delete, validate=True)
    def delete(self, username):
        '''Delete a todo from the list'''
        todo_idx = api.payload['todo_idx']
        if 0 <= todo_idx < len(_TODOS[username]):
            _TODOS[username].pop(todo_idx)
        return 'OK', 200

@app.route("/logo.png", methods=['GET'])
def plugin_logo():
    filename = 'logo.png'
    return send_file(filename, mimetype='image/png')

@app.route("/openapi.yaml", methods=['GET'])
def openapi_spec():
    openapi_json = api.__schema__
    openapi_yaml = yaml.dump(openapi_json)
    response = make_response(openapi_yaml)
    response.headers["Content-Type"] = "text/yaml"
    return response

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()
