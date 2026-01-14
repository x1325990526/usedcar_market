from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_
from app import db
from app.models import User, Car, Favorite, Message
from app.forms import RegisterForm, LoginForm, CarCreateForm, MessageForm, CarEditForm
from app.utils import save_upload

def register_routes(app):
    @app.get("/")
    def index():
        return render_template("index.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("car_list"))
        form = RegisterForm()
        if form.validate_on_submit():
            if User.query.filter_by(email=form.email.data).first():
                flash("邮箱已注册","danger")
                return redirect(url_for("register"))
            if User.query.filter_by(username=form.username.data).first():
                flash("用户名已存在","danger")
                return redirect(url_for("register"))

            u = User(email=form.email.data, username=form.username.data)
            u.set_password(form.password.data)
            db.session.add(u)
            db.session.commit()
            flash("注册成功，请登录")
            return redirect(url_for("login"))
        return render_template("auth_register.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("car_list"))
        form = LoginForm()
        if form.validate_on_submit():
            u = User.query.filter_by(email=form.email.data).first()
            if not u or not u.check_password(form.password.data):
                flash("邮箱或密码错误", "danger")
                return redirect(url_for("login"))
            login_user(u)
            return redirect(url_for("car_list"))
        return render_template("auth_login.html", form=form)

    @app.get("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("index"))

    @app.get("/cars")
    def car_list():
        q = request.args.get("q", "").strip()
        brand = request.args.get("brand", "").strip()
        city = request.args.get("city", "").strip()
        min_price = request.args.get("min_price", "").strip()
        max_price = request.args.get("max_price", "").strip()

        query = Car.query.filter_by(is_active=True)

        if q:
            like = f"%{q}%"
            query = query.filter(or_(Car.title.ilike(like), Car.model.ilike(like), Car.brand.ilike(like)))
        if brand:
            query = query.filter(Car.brand == brand)
        if city:
            query = query.filter(Car.city == city)
        if min_price.isdigit():
            query = query.filter(Car.price >= int(min_price))
        if max_price.isdigit():
            query = query.filter(Car.price <= int(max_price))

        cars = query.order_by(Car.created_at.desc()).all()
        return render_template("car_list.html", cars=cars)

    @app.route("/cars/create", methods=["GET", "POST"])
    @login_required
    def car_create():
        form = CarCreateForm()
        if form.validate_on_submit():
            filename = save_upload(
                form.image.data,
                upload_folder=app.config["UPLOAD_FOLDER"],
                allowed_ext=app.config["ALLOWED_EXTENSIONS"],
            )

            car = Car(
                title=form.title.data,
                brand=form.brand.data,
                model=form.model.data,
                year=form.year.data,
                mileage_km=form.mileage_km.data,
                price=form.price.data,
                city=form.city.data,
                description=form.description.data,
                image_filename=filename,
                seller_id=current_user.id,
            )
            db.session.add(car)
            db.session.commit()
            flash("发布成功")
            return redirect(url_for("car_detail", car_id=car.id))
        return render_template("car_create.html", form=form)

    @app.route("/cars/<int:car_id>", methods=["GET", "POST"])
    def car_detail(car_id: int):
        car = Car.query.get_or_404(car_id)
        if not car.is_active and (not current_user.is_authenticated or not current_user.is_admin):
            abort(404)

        form = MessageForm()
        if form.validate_on_submit():
            if not current_user.is_authenticated:
                flash("请先登录再留言", "danger")
                return redirect(url_for("login"))
            msg = Message(car_id=car.id, user_id=current_user.id, content=form.content.data)
            db.session.add(msg)
            db.session.commit()
            flash("已发送")
            return redirect(url_for("car_detail", car_id=car.id))

        is_fav = False
        if current_user.is_authenticated:
            is_fav = Favorite.query.filter_by(user_id=current_user.id, car_id=car.id).first() is not None

        messages = Message.query.filter_by(car_id=car.id).order_by(Message.created_at.desc()).all()
        return render_template("car_detail.html", car=car, form=form, is_fav=is_fav, messages=messages)

    @app.post("/cars/<int:car_id>/favorite")
    @login_required
    def car_favorite(car_id: int):
        car = Car.query.get_or_404(car_id)
        fav = Favorite.query.filter_by(user_id=current_user.id, car_id=car.id).first()
        if fav:
            db.session.delete(fav)
            db.session.commit()
            flash("已取消收藏")
        else:
            db.session.add(Favorite(user_id=current_user.id, car_id=car.id))
            db.session.commit()
            flash("已收藏")
        return redirect(url_for("car_detail", car_id=car.id))

    @app.get("/profile")
    @login_required
    def profile():
        my_cars = Car.query.filter_by(seller_id=current_user.id, is_active=True).order_by(Car.created_at.desc()).all()
        favs = Favorite.query.filter_by(user_id=current_user.id).all()
        fav_cars = [f.car for f in favs]
        return render_template("profile.html", my_cars=my_cars, fav_cars=fav_cars)

    @app.post("/admin/cars/<int:car_id>/deactivate")
    @login_required
    def admin_deactivate_car(car_id: int):
        if not current_user.is_admin:
            abort(403)
        car = Car.query.get_or_404(car_id)
        car.is_active = False
        db.session.commit()
        flash("已下架")
        return redirect(url_for("car_detail", car_id=car.id))

    
    @app.route("/cars/<int:car_id>/edit", methods=["GET", "POST"])
    @login_required
    def car_edit(car_id: int):
        car = Car.query.get_or_404(car_id)

        # 只有车主或管理员能编辑
        if car.seller_id != current_user.id and not current_user.is_admin:
            abort(403)

        form = CarEditForm(obj=car)  # GET 时自动把 car 数据回填到表单

        if form.validate_on_submit():
            # 更新字段
            car.title = form.title.data
            car.brand = form.brand.data
            car.model = form.model.data
            car.year = form.year.data
            car.mileage_km = form.mileage_km.data
            car.price = form.price.data
            car.city = form.city.data
            car.description = form.description.data

            # 可选：更新图片（没选则保留原图）
            filename = save_upload(
                form.image.data,
                upload_folder=app.config["UPLOAD_FOLDER"],
                allowed_ext=app.config["ALLOWED_EXTENSIONS"],
            )
            if filename:
                car.image_filename = filename

            db.session.commit()
            flash("修改已保存", "success")
            return redirect(url_for("car_detail", car_id=car.id))

        return render_template("car_edit.html", form=form, car=car)
    
    @app.post("/cars/<int:car_id>/withdraw")
    @login_required
    def car_withdraw(car_id: int):
        car = Car.query.get_or_404(car_id)

        # 只有车主或管理员能撤回
        if car.seller_id != current_user.id and not current_user.is_admin:
            abort(403)

        car.is_active = False
        db.session.commit()
        flash("车辆已下架", "warning")
        return redirect(url_for("profile"))  # 或者回到详情页