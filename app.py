from flask import Flask, render_template, request, url_for, make_response, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "my-secret-key"
db = SQLAlchemy(app)



class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(75), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)



with app.app_context():
    db.create_all()


CATEGORIES = ['Food', 'Transportation', 'Rent', 'Utilities/Bills', 'Entertainment', 'Health']

@app.route("/")
def index():

    expenses = Expense.query.order_by(Expense.date.desc(), Expense.id.desc()).all()
    total = round(sum(e.amount for e in expenses), 2)
    return render_template(
        "index.html", 
        expenses=expenses,
        categories=CATEGORIES,
        total=total
    )



@app.route("/add", methods=['POST'])
def add():
    description = (request.form.get("description") or "" ).strip()
    amount_str = (request.form.get("amount") or "" ).strip()
    date_str = (request.form.get("date") or "" ).strip()
    category = (request.form.get("category") or "" ).strip()

    if not description or not amount_str or not category:
        flash("Please fill the description, amount, and category.", "error")
        redirect(url_for("index"))

    try: 
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError

    except ValueError:
        flash("Amount must be greater than 0.", "error")
        return redirect(url_for("index"))
    

    #For date_str
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()

    except ValueError:
        d = date.today

    e = Expense(description=description, amount=amount, date=d, category=category)
    db.session.add(e)
    db.session.commit()
    flash("Expense added.", "success")
    return redirect(url_for("index"))

@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete(expense_id):
    e = Expense.query.get_or_404(expense_id)
    db.session.delete(e)
    db.session.commit()
    flash("Expense deleted.", "success")
    return redirect(url_for("index"))




if (__name__) == "__main__":
    app.run(debug=True)