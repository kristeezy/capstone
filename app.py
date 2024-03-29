from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt  
from sqlalchemy.orm import relationship, joinedload
from vonage import Client

password = 'user_password'

app = Flask(__name__, static_folder='static', template_folder='templates')
csrf = CSRFProtect()
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:4648@localhost/users_db'
app.config['SECRET_KEY'] = 'your_secret_key'  
db = SQLAlchemy(app)
migrate = Migrate(app, db)  
bcrypt = Bcrypt(app)  

login_manager = LoginManager(app)
login_manager.login_view = 'login'

VONAGE_API_KEY = 'b4ce559d'
VONAGE_API_SECRET = 'SqPh72XsWUV09jLq'
VONAGE_PHONE_NUMBER = '14142840015'

# Create a Vonage client
vonage_client = Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(15)) 

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        try:
            return bcrypt.check_password_hash(self.password_hash, password)
        except ValueError:
            return False

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # user = db.relationship('User', backref='expenses')
    
    # Establish a one-to-many relationship with participants
    participant = db.relationship('Participant', backref='expense', lazy=True)

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    expense_id = db.Column(db.Integer, db.ForeignKey('expense.id'), nullable=False)

def parse_participant(participant_input):
    participant = []
    for part in participant_input.split(','):
        name, amount = part.strip().split(':')
        participant = Participant(name=name, amount=float(amount))
        participant.append(participant)
    return participant


class PhoneNumberForm(FlaskForm):
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    submit = SubmitField('Save Phone Number')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class YourLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ExpenseForm(FlaskForm):
    description = StringField('Description', render_kw={'placeholder': 'Expense description'}, validators=[DataRequired()])
    amount = StringField('Amount', render_kw={'placeholder': 'Expense amount'}, validators=[DataRequired()])
    participant = StringField('Participant', render_kw={'placeholder': 'Comma-separated usernames'}, validators=[DataRequired()])
    submit = SubmitField('Create Expense')

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    form = YourLoginForm()
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = YourLoginForm()

    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))

        flash('Invalid username or password', 'danger')  # Flash an error message

    return render_template('login.html', form=form)

def create_new_expense(description, amount, user_id, participant):
    # Calculate the total participants' share
    total_participant_share = sum(participant.amount for participant in participant)

    # Convert amount to the appropriate type (e.g., float)
    amount = float(amount)

    # Convert total_participants_share to the same type as amount
    total_participant_share = float(total_participant_share)

    # Create a new Expense instance
    expense = Expense(description=description, amount=amount, user_id=user_id)

    # Add participants to the expense
    for participant in participant:
        expense.participant.append(participant)

    # Add the expense to the session and commit
    db.session.add(expense)
    db.session.commit()

    flash('Expense created successfully!', 'success')

    # Check if the total participants' share exceeds the total bill amount
    if total_participant_share > amount:
        flash('Total participant\' share cannot exceed the total bill amount.', 'danger')
        return





# Updated create_expense route
@app.route('/create_expense', methods=['GET', 'POST'])
@login_required
def create_expense():
    form = ExpenseForm()
    phone_number_form = PhoneNumberForm()

    if form.validate():
        participant_input = form.participant.data
        participant = parse_participant(participant_input)
        
        create_new_expense(form.description.data, form.amount.data, current_user.id, form.participant.data) #01/18 added participants
        return redirect(url_for('create_expense')) # 01/18 Modified from 'expenses'

    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    if phone_number_form.validate():
        # Save the phone number to the current user
        current_user.phone_number = phone_number_form.phone_number.data
        db.session.commit()
        

        # Send SMS to the provided phone number
        send_sms(current_user.phone_number, "This is a test SMS message.")  # Customize the SMS message as needed

        flash('Phone number saved and SMS sent successfully!', 'success')
    return render_template('create_expense.html', form=form, expenses=expenses, phone_number_form=phone_number_form)

@app.route('/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'clear':
            # Logic to clear expenses (delete all expenses for the current user)
            Expense.query.filter_by(user_id=current_user.id).delete()
            db.session.commit()
            flash('Expenses cleared successfully!', 'success')
            return redirect(url_for('expenses'))

        # Include the logic to process the form data and save expenses
        description = request.form.get('description')  
        amount = request.form.get('amount')

        # Extract participants from the form data, assuming they are in a comma-separated string
        participant_str = request.form.get('participant', '')
        participant = [Participant(name=name, amount=0) for name in participant_str.split(',') if name]

        create_new_expense(description, amount, current_user.id, participant)
        
        print(f"POST request received. Description: {description}, Amount: {amount}, Participants: {participant}")

        return redirect(url_for('expenses'))

    # Handle GET request to display expenses with participants
    expenses = db.session.query(Expense).options(joinedload(Expense.participant)).filter_by(user_id=current_user.id).all()
    return render_template('expenses.html', expenses=expenses)



@app.route('/modify_expense/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def modify_expense(expense_id):
    # Fetch the expense from the database
    expense = Expense.query.get_or_404(expense_id)

    # Create an instance of ExpenseForm and populate it with the current expense details
    form = ExpenseForm(request.form, obj=expense)

    # Check if the form is submitted and valid
    if form.validate():
        # Update the expense details with the form data
        form.populate_obj(expense)

        # Calculate the total participants' share
        total_participant_share = sum(participant.amount for participant in expense.participant)

        # Check if the total participants' share exceeds the total bill amount
        if total_participant_share > expense.amount:
            flash('Total participant\' share cannot exceed the total bill amount.', 'danger')
            return redirect(url_for('modify_expense', expense_id=expense_id))

        # Include logic to update participants if needed

        db.session.commit()
        flash('Expense modified successfully!', 'success')
        return redirect(url_for('expenses'))

    # Provide the CSRF token for the modification form
    return render_template('modify_expense.html', expense=expense, form=form)


def send_sms(to, body): #01/19 adding function to allow for sending SMS
    try:
       # sms_body = f"Hello! You owe {expense.amount} for the expense: {expense.description}. Participants: {', '.join(participant.name for participant in expense.participants)}. Thank you!"
        
        response = vonage_client.send_message({
            'from': VONAGE_PHONE_NUMBER,
            'to': to,
            'text': body
        })
        message = response['messages'][0]
        print(f"SMS sent successfully to {to}. Message ID: {message['message-id']}")
    except Exception as e:
        print(f"Failed to send SMS to {to}. Error: {str(e)}")


@app.route('/clear_expenses', methods=['GET', 'POST'])
@login_required
def clear_expenses():
    try:
        Expense.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        flash('All expenses cleared successfully!', 'success')
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        db.session.rollback()
        flash('Failed to clear expenses.', 'danger')

    return redirect(url_for('expenses'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = ExpenseForm()

    if form.validate_on_submit():
        description = form.description.data
        amount = form.amount.data
        users = form.users.data.split(',')

        expense = Expense(description=description, amount=amount, user_id=current_user.id)
        db.session.add(expense)
        db.session.commit()

        flash('Expense created successfully!', 'success')

    expenses = Expense.query.filter_by(user_id=current_user.id).all()

    phone_number_form = PhoneNumberForm()

    if phone_number_form.validate_on_submit():
        current_user.phone_number = phone_number_form.phone_number.data
        db.session.commit()
        flash('Phone number saved successfully!', 'success')

    return render_template('dashboard.html', username=current_user.username, expenses=expenses, form=form, phone_number_form=phone_number_form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('logout/success'))

@app.route('/logout/success')
def logout_success():
    return render_template('logout.html')

if __name__ == '__main__':
    app.run(debug=True)