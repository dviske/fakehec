from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Collector(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    token: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=False)
    messages: so.WriteOnlyMapped['Message'] = so.relationship(back_populates='collector', passive_deletes=True)

    def __repr__(self):
        return '<Collector {}>'.format(self.name)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return Collector.query.get(int(id))

class Message(db.Model):
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    received_at: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, server_default=sa.func.now())
    received_from: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)
    content: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    collector_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('collector.id'), nullable=False)
    collector: so.Mapped[Collector] = so.relationship(back_populates='messages', passive_deletes=True)

    def __repr__(self):
        return '<Message {}>'.format(self.id)
    
    def remove_old_messages(days=7):
        from datetime import datetime, timedelta
        threshold_date = datetime.now() - timedelta(days=days)
        old_messages = Message.query.filter(Message.received_at < threshold_date).all()
        for message in old_messages:
            db.session.delete(message)
        db.session.commit()