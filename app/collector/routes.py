from flask import request, jsonify
from app.collector import bp
import sqlalchemy as sa
from app import db
from app.models import Collector, Message

@bp.route('/services/collector', methods=['POST'], subdomain='<sub>')
def collector(sub):
    user = db.session.scalar(sa.select(Collector).where(Collector.name == sub))
    if user is None:
       return {"text": "Incorrect index", "code": 7}, 400

    if not request.authorization:
        return {"text": "Token is required", "code": 2}, 401
    
    auth = str(request.authorization).lstrip("Splunk ")

    if auth != user.token:
        return {"text": "invalid token", "code": 4}, 401
    
    if request.headers.get('X-Real-IP'):
        addr = request.headers.get('X-Real-IP')
    else:
        addr = request.remote_addr

    msg = Message(
        received_from=addr,
        collector=user
    )
    if request.headers.get('Content-Type') == "application/json":
      if request.data == b'':
        print("Empty request")
        msg.content = None
      else:
        msg.content = request.get_data(as_text=True)
    db.session.add(msg)
    db.session.commit()
    return {"text": "Success", "code": 0}


#@bp.route('/services/collector/event', methods=['POST'])
#def collector_json():
#    print(request.json)
#    return jsonify('{"text": "Success", "code": 0}')