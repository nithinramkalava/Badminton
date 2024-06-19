from models import  Venue,Member
from datetime import time
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_admin.form.upload import FileUploadField
from werkzeug.utils import secure_filename
from flask import request, redirect, url_for,flash
from werkzeug.security import generate_password_hash
from wtforms import StringField
from flask_login import current_user,logout_user
from flask_admin.form import SecureForm

from wtforms.validators import DataRequired
from flask_admin import AdminIndexView
import os

# All the views of Admin page
allowed_image_extensions = ["jpg","avif", "jpeg", "png", "gif", "bmp", "webp", "svg", "tiff", "ico", "psd", "hdr", "exr"]


class AdminIndexView2(AdminIndexView):
    def is_accessible(self):
        # to take care of AnonymousUser
        if current_user:  
            return current_user.is_admin if hasattr(current_user, 'is_admin') else False
        return False


    def inaccessible_callback(self, name, **kwargs): # LOGIC ON UNAUTHORIZED ACCESs
        flash("Trespassers will be prosecuted :)","error")
        return redirect(url_for('userlogin', next=request.url))
    

class AdminModelView(ModelView): #extension of Modelview
    def is_accessible(self):
        # to take care of AnonymousUser
        if current_user:  
            return current_user.is_admin if hasattr(current_user, 'is_admin') else False
        return False


    def inaccessible_callback(self, name, **kwargs): # LOGIC ON UNAUTHORIZED ACCESs
        flash("Trespassers will be prosecuted :)","error")
        return redirect(url_for('userlogin', next=request.url))


class UserView(AdminModelView):
    form_base_class = SecureForm # for csrf protection forms
    column_searchable_list = ["Name", "Username","is_admin"] # for searching
    column_filters = ["Name", "Username","is_admin"]# for filters
    form_excluded_columns = ["HashedPassword","bookings"]#excluded attributes in forms
    form_extra_fields = {
        'Password': StringField('Password', validators=[DataRequired()])
    }

    def on_model_change(self, form, model, is_created):
        if is_created or 'Password' in form.data:
            model.HashedPassword = generate_password_hash(form.Password.data) # for hashing


class VenueView(AdminModelView):
    model = Venue()
    form_base_class = SecureForm
    column_searchable_list = ["VenueName"]
    column_filters = ["VenueName"]
    form_excluded_columns = ["VenueImageURL","bookings"]
    form_extra_fields = {
        'image': FileUploadField('Image', base_path="static/venues", allowed_extensions=allowed_image_extensions)
    }
    
    def generate_filename(self, model, form): #for unique file name
        venue_name = model.VenueName
        filename = secure_filename(form.image.data.filename)
        unique_filename = f"{venue_name}_{filename}"
        return unique_filename


    def on_model_change(self, form, model, is_created):
        if model.VenueImageURL and not is_created:
            original_image_path = os.path.join(os.getcwd(), "static/venues", os.path.basename(model.VenueImageURL))
            if os.path.exists(original_image_path): # to remove image with original name
                os.remove(original_image_path)

        if 'image' in form.data:
            new_filename = self.generate_filename(model, form)
            form.image.data.seek(0) # to prevent corruption
            form.image.data.save(os.path.join(os.getcwd(), "static/venues", new_filename))
            model.VenueImageURL = f"/static/venues/{new_filename}"
            filepath = os.path.join(os.getcwd(), "static/venues", form.image.data.filename)
            if os.path.exists(filepath):
                os.remove(filepath)

    def on_model_delete(self, model):
        super().on_model_delete(model)
        if model.VenueImageURL:
            image_path = os.path.join(os.getcwd(), "static/venues", os.path.basename(model.VenueImageURL))
            if os.path.exists(image_path):
                os.remove(image_path)



class SportView(AdminModelView):
    form_base_class = SecureForm
    column_searchable_list = ["SportName"]
    column_filters = ["SportName"]
    form_excluded_columns = ["SportImageURL","venues","bookings"]

    form_extra_fields = {
        'image': FileUploadField('Image', base_path="static/sports", allowed_extensions=allowed_image_extensions)
    }

    def generate_filename(self, model, form):
        name = model.SportName
        filename = secure_filename(form.image.data.filename)
        unique_filename = f"{name}_{filename}"
        return unique_filename


    def on_model_change(self, form, model, is_created):
        if model.SportImageURL and not is_created:
            original_image_path = os.path.join(os.getcwd(), "static/sports", os.path.basename(model.SportImageURL))
            if os.path.exists(original_image_path):
                os.remove(original_image_path)

        if 'image' in form.data:
            new_filename = self.generate_filename(model, form)
            form.image.data.seek(0) # to prevent image correuption
            form.image.data.save(os.path.join(os.getcwd(), "static/sports", new_filename))
            model.SportImageURL = f"/static/sports/{new_filename}"
            filepath = os.path.join(os.getcwd(), "static/sports", form.image.data.filename)
            if os.path.exists(filepath):
                os.remove(filepath)

    def on_model_delete(self, model):
        super().on_model_delete(model)
        if model.SportImageURL:
            image_path = os.path.join(os.getcwd(), "static/sports", os.path.basename(model.SportImageURL))
            if os.path.exists(image_path):
                os.remove(image_path)


class LogView(AdminModelView):
    form_base_class = SecureForm
    can_create = False # cannot create a new log
    can_delete = True
    can_edit = False # cannot edit any log
    can_view_details = True
    form_excluded_columns=["User","Venue","Sport"]
    column_list = ['BookingID', 'UserID', 'VenueID', 'SportID', 'Slot', 'Duration', 'Date']
    column_searchable_list = ["UserID", "VenueID","SportID","Date"]
    column_filters = ["UserID", "VenueID","SportID","Date"]


class MemberView(AdminModelView):
    model = Member()
    form_base_class = SecureForm
    column_searchable_list = ["Name","Instno", "Batch"]
    column_filters = ["Name","Instno", "Batch"]
    form_excluded_columns = ["MemImageURL"]
    form_extra_fields = {
        'image': FileUploadField('Image', base_path="static/members", allowed_extensions=allowed_image_extensions)
    }

    def generate_filename(self, model, form):
        name = model.Name
        filename = secure_filename(form.image.data.filename)
        unique_filename = f"{name}_{filename}"
        return unique_filename


    def on_model_change(self, form, model, is_created):
        if model.MemImageURL and not is_created:
            original_image_path = os.path.join(os.getcwd(), "static/members", os.path.basename(model.MemImageURL))
            if os.path.exists(original_image_path):
                os.remove(original_image_path)

        if 'image' in form.data:
            new_filename = self.generate_filename(model, form)
            form.image.data.seek(0)
            form.image.data.save(os.path.join(os.getcwd(), "static/members", new_filename))
            model.MemImageURL = f"/static/members/{new_filename}"
            filepath = os.path.join(os.getcwd(), "static/members", form.image.data.filename)
            if os.path.exists(filepath):
                os.remove(filepath)

    def on_model_delete(self, model):
        super().on_model_delete(model)
        if model.MemImageURL:
            image_path = os.path.join(os.getcwd(), "static/members", os.path.basename(model.MemImageURL))
            if os.path.exists(image_path):
                os.remove(image_path)

