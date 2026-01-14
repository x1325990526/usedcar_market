from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, Length, NumberRange


class RegisterForm(FlaskForm):
    email = StringField("邮箱", validators=[DataRequired(), Email(), Length(max=120)])
    username = StringField("用户名", validators=[DataRequired(), Length(min=2, max=40)])
    password = PasswordField("密码", validators=[DataRequired(), Length(min=6, max=64)])
    submit = SubmitField("注册")


class LoginForm(FlaskForm):
    email = StringField("邮箱", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("密码", validators=[DataRequired(), Length(min=6, max=64)])
    submit = SubmitField("登录")


class CarCreateForm(FlaskForm):
    title = StringField("标题", validators=[DataRequired(), Length(max=120)])
    brand = StringField("品牌", validators=[DataRequired(), Length(max=40)])
    model = StringField("车型", validators=[DataRequired(), Length(max=60)])
    year = IntegerField("年份", validators=[DataRequired(), NumberRange(min=1980, max=2100)])
    mileage_km = IntegerField("里程(km)", validators=[DataRequired(), NumberRange(min=0, max=2000000)])
    price = IntegerField("价格(元)", validators=[DataRequired(), NumberRange(min=1, max=200000000)])
    city = StringField("城市", validators=[DataRequired(), Length(max=40)])
    description = TextAreaField("描述", validators=[Length(max=5000)])
    image = FileField("车辆图片")
    submit = SubmitField("发布")


class MessageForm(FlaskForm):
    content = StringField("留言", validators=[DataRequired(), Length(min=2, max=500)])
    submit = SubmitField("发送")

class CarEditForm(FlaskForm):
    title = StringField("标题", validators=[DataRequired(), Length(max=120)])
    brand = StringField("品牌", validators=[DataRequired(), Length(max=40)])
    model = StringField("车型", validators=[DataRequired(), Length(max=60)])
    year = IntegerField("年份", validators=[DataRequired(), NumberRange(min=1980, max=2100)])
    mileage_km = IntegerField("里程(km)", validators=[DataRequired(), NumberRange(min=0, max=2000000)])
    price = IntegerField("价格(元)", validators=[DataRequired(), NumberRange(min=1, max=200000000)])
    city = StringField("城市", validators=[DataRequired(), Length(max=40)])
    description = TextAreaField("描述", validators=[Length(max=5000)])
    image = FileField("车辆图片（不选则保留原图）")
    submit = SubmitField("保存修改")
