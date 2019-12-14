from flask import Blueprint, Flask, render_template, jsonify, request

myservice = Blueprint('myservice', __name__, template_folder='templates')

"""
    simple endpoints to show the external definition of a custom service
"""

@myservice.route("/annotatequestion", methods=['POST'])
def qanaryService():
    """the POST endpoint required for a Qanary service"""
    
    triplestore_endpoint = request.json["values"]["urn:qanary#endpoint"]
    triplestore_ingraph  = request.json["values"]["urn:qanary#inGraph"]
    triplestore_outgraph = request.json["values"]["urn:qanary#outGraph"]
    print(triplestore_ingraph)
    print("endpoint: %s, ingraph: %s, outGraph: %s" % (triplestore_endpoint, triplestore_ingraph, triplestore_outgraph))

	# add your functionality here    

    return jsonify(request.get_json())

@myservice.route("/", methods=['GET'])
def index():
    """an examplary GET endpoint returning "hello world2 (String)"""
    print(request.host_url)
    return "Hello, World!"


@myservice.route("/", methods=['POST'])
def indexJson():
    """a POST endpoint returning a hello world JSON"""
    data = {'Hello': 'World'}
    return jsonify(data)
