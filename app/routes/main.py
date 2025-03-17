from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.models.record import Record
from app.forms import SignUpForm, AddRecordForm
from app import db
from werkzeug.security import generate_password_hash

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
def home():
    records = Record.query.all()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('You Have Been Logged In!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('There Was An Error Logging In, Please Try Again...', 'error')
            return redirect(url_for('main.home'))
    return render_template('home.html', records=records)


@bp.route('/logout')
@login_required
def logout():  # This function name should match what's used in url_for()
    logout_user()
    flash('You Have Been Logged Out Successfully', 'success')
    return redirect(url_for('main.home'))

@bp.route('/register', methods=['GET', 'POST'])
def register_user():
    form = SignUpForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data
            )
            user.set_password(form.password1.data)
            db.session.add(user)
            db.session.commit()

            login_user(user)
            flash('You Have Successfully Registered! Welcome!', 'success')
            return redirect(url_for('main.home'))
    return render_template('register.html', form=form)

@bp.route('/record/<int:pk>')
@login_required
def customer_record(pk):
    customer_record = Record.query.get_or_404(pk)
    return render_template('record.html', customer_record=customer_record)

@bp.route('/delete_record/<int:pk>')
@login_required
def delete_record(pk):
    delete_it = Record.query.get_or_404(pk)
    db.session.delete(delete_it)
    db.session.commit()
    flash('Record Deleted Successfully...', 'success')
    return redirect(url_for('main.home'))

@bp.route('/add_record', methods=['GET', 'POST'])
@login_required
def add_record():
    form = AddRecordForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            record = Record(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                address=form.address.data,
                city=form.city.data,
                state=form.state.data,
                zipcode=form.zipcode.data,
                user_id=current_user.id
            )
            db.session.add(record)
            db.session.commit()
            flash('Record Added...', 'success')
            return redirect(url_for('main.home'))
    return render_template('add_record.html', form=form)

@bp.route('/update_record/<int:pk>', methods=['GET', 'POST'])
@login_required
def update_record(pk):
    try:
        current_record = Record.query.get_or_404(pk)
        
        # Check if the current user owns this record
        if current_record.user_id != current_user.id:
            flash('You are not authorized to update this record.', 'error')
            return redirect(url_for('main.home'))
        
        form = AddRecordForm(obj=current_record)
        
        if request.method == 'POST':
            if form.validate_on_submit():
                try:
                    # Update record fields
                    current_record.first_name = form.first_name.data
                    current_record.last_name = form.last_name.data
                    current_record.email = form.email.data
                    current_record.phone = form.phone.data
                    current_record.address = form.address.data
                    current_record.city = form.city.data
                    current_record.state = form.state.data
                    current_record.zipcode = form.zipcode.data
                    
                    # The updated_at timestamp will be automatically updated thanks to onupdate
                    
                    db.session.commit()
                    flash('Record Has Been Updated Successfully!', 'success')
                    return redirect(url_for('main.home'))
                
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error updating record: {str(e)}', 'error')
                    return redirect(url_for('main.update_record', pk=pk))
            else:
                flash('Please check the form for errors.', 'error')
        
        return render_template('update_record.html', 
                            form=form,
                            record=current_record,
                            title='Update Record')
    
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('main.home'))