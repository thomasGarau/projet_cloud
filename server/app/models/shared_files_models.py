from .. import db

class SharedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
    owner_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    shared_with_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    file = db.relationship('File', backref=db.backref('shared_files', lazy=True))
    owner_user = db.relationship('User', foreign_keys=[owner_user_id], backref=db.backref('owned_files', lazy=True))
    shared_with_user = db.relationship('User', foreign_keys=[shared_with_user_id], backref=db.backref('shared_with_me_files', lazy=True))
