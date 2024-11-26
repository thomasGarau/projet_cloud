from .. import db
from datetime import datetime

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    extension = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_opened = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    original_size = db.Column(db.Integer, nullable=False, default=0)
    compressed_size = db.Column(db.Integer, nullable=True)
    azure_blob_path = db.Column(db.String(512), nullable=True)
    
    user = db.relationship('User', backref=db.backref('files', lazy=True))
