from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from sqlalchemy import create_engine, text
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from datetime import datetime, timedelta
import random

def login_required(
    f,
):  # redirects to login if not logged in, idk what it does otherwise
    # Decorate routes to require login.

    # http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def admin_page(
    f,
):  # redirects to login if not logged in, idk what it does otherwise
    # Decorate routes to require login.

    # http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session["account_type"] != "Admin":
            return apology("This is admin page, u no have access", 400)
        return f(*args, **kwargs)

    return decorated_function

def vendor_page(
    f,
):  # redirects to login if not logged in, idk what it does otherwise
    # Decorate routes to require login.

    # http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session["account_type"] != "Vendor":
            return apology("This is user page, u no have access", 400)
        return f(*args, **kwargs)

    return decorated_function

def customer_page(
    f,
):  # redirects to login if not logged in, idk what it does otherwise
    # Decorate routes to require login.

    # http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session["account_type"] != "Customer":
            return apology("This is user page, u no have access", 400)
        return f(*args, **kwargs)

    return decorated_function


#configure application
app = Flask(__name__)

#configure session to use file system
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# connection string is in the format mysql://user:password@server/database
conn_str = "mysql://root:Just5fun!@localhost/customers_2"
engine = create_engine(conn_str) # echo=True tells you if connection is successful or not
db = engine.connect()


@app.route("/")
def main_page():
    warning = ""
    items = db.execute(text("select * from items")).all()
    if (len(items) > 6):
        random_numbers = random.sample(range(len(items)), 6)
    elif (len(items) > 0):
        random_numbers = random.sample(range(len(items)), len(items))
    else:
        warning = "Uh oh! Something went wrong so no items are available."
    random_items = []
    random_images = []

    if (len(items) > 0):

        for i in random_numbers:
            random_items.append(items[i])

        for i in random_items:
            params = {"id":i[0]}
            if len(db.execute(text("select * from images where item_id = :id"), params).all()) > 0:
                random_images.append([db.execute(text("select * from images where item_id = :id"), params).all()[0][1], i[0]])
            else:
                warning = "Uh oh! Something went wrong so no items are available."
        
    return render_template("index.html", random_images=random_images, warning=warning)


@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    if request.method == "POST":
        #store all data
        username = request.form.get("username")
        email = request.form.get("email")
        name = request.form.get("name")
        password = request.form.get("password")
        check_password = request.form.get("confirmation")
        account_type = request.form.get("account_type")

        #make sure all info exists
        if not username or not password or not check_password or not name or not email or not account_type:
            return apology("Missing information", 400)

        #check if username already exists
        params = {"email":email, "username":username}
        users = db.execute(text("select * from users where email = :email"), params).all()
        if len(users) > 0:
            return apology("email already in use", 400)
        
        #check confirmation password
        if password != check_password:
            return apology("passwords don't match", 400)
        
        users = db.execute(text("select * from users where username = :username"), params).all()
        for user in users:
            if user[2] == username and check_password_hash(user[4], password):
                return apology("account already in use")
        

        #generate hash and store in database
        hashed = generate_password_hash(password + "SOIEFHBsefuionvhiouW")
        params = {"username":username, "username":username, "name":name, "email":email, "hashed":hashed, "account":account_type}

        
        db.execute(text("insert into users (email, username, proper_name, pass, user_type) values (:email, :username, :name, :hashed, :account)"), params)
        db.commit()
        
        return render_template("login.html")
    
    else:
        return render_template("register.html")
    

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        #store login info
        email = request.form.get("email")
        password = request.form.get("password")
        password = password + "SOIEFHBsefuionvhiouW"
        
        #check all info exists
        if not email or not password:
            return apology("missing information", 400)
        
        #call username and check password
        params = {"email":email, "password":password}
        users = db.execute(text("select * from users where email = :email"), params).all()

        user_password = db.execute(text("select pass from users where email = :email"), params).all()

        # Check if the password matches their hashed version in the database
        if len(users) != 1 or not check_password_hash(user_password[0][0], password):
            users = db.execute(text("select * from users where username = :email"), params).all()
            for user in users:
                if check_password_hash(user[4], password) and user[2] == email:
                    session["account_num"] = user[0]
                    session["user_id"] = user[1]
                    session["username"] = user[2]
                    session["loggedIn"] = True
                    session["account_type"] = user[5]
                    return redirect("/")
            return apology("Wrong username and or password", 400)

        
        else:
            # Sign the user in as their current username and make the session "loggedIn"
            session["account_num"] = users[0][0]
            session["user_id"] = users[0][1]
            session["username"] = users[0][2]
            session["loggedIn"] = True
            session["account_type"] = users[0][5]

            return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/")

#account routes
@app.route("/my_account", methods=["Get", "POST"])
@login_required
def my_account():
    user_id = session["account_num"]
    params = {"user_id":user_id}
    info = db.execute(text("select * from users where user_id = :user_id"), params).all()
    address = db.execute(text("select * from addresses where user_id = :user_id and default_address = 'Yes'"), params).all()
    return render_template("account.html", info=info[0], address=address)

@app.route("/my_account/view", methods=["Get", "POST"])
@login_required
@customer_page
def view_addresses():
    params = {"user_id": session["account_num"]}
    addresses = db.execute(text("select * from addresses where user_id = :user_id and is_active = 'Yes' order by default_address desc"), params).all()
    return render_template("view_addresses.html", addresses=addresses)

@app.route("/my_account/add", methods=["Get", "POST"])
@login_required
@customer_page
def add_address():


    if request.method == "POST":
        reciever = request.form.get("reciever")
        contact = request.form.get("contact_number")
        address1 = request.form.get("address_1")
        address2 = request.form.get("address_2")
        city = request.form.get("city")
        zip = request.form.get("zip")
        state = request.form.get("state")
        is_default = False
        
        if not reciever or not contact or not address1 or not address2 or not city or not zip or not state:
            return apology("Missing info")

        if request.form.get("default_address"):
            is_default = True

        params={"user_id":session["account_num"], "reciever":reciever, "contact":contact, "address1":address1, "address2":address2, "city":city, "zip":zip, "state":state}

        if is_default or len(db.execute(text("select * from addresses where user_id = :user_id and default_address = 'Yes'"), params).all()) == 0:
            db.execute(text("update addresses set default_address = 'No' where user_id = :user_id"), params)
            db.commit()
            db.execute(text("insert into addresses (user_id, default_address, reciever, contact_number, address_line_1, address_line_2, city, state, zip, is_active) values (:user_id, 'Yes', :reciever, :contact, :address1, :address2, :city, :state, :zip, 'Yes')"), params)
            db.commit()
        else:
            db.execute(text("insert into addresses (user_id, default_address, reciever, contact_number, address_line_1, address_line_2, city, state, zip, is_active) values (:user_id, 'No', :reciever, :contact, :address1, :address2, :city, :state, :zip, 'Yes')"), params)
            db.commit()

    
        return render_template("add_address.html")
    else:
        return render_template("add_address.html")
    
@app.route("/my_account/delete", methods=["Get", "POST"])
@login_required
@customer_page
def delete_address():
    if request.method == "POST":
        id = request.form.get("address_id")
        params = {"address_id":id}
        db.execute(text("update addresses set is_active = 'No' where address_id = :address_id"), params)
        db.commit()

        params = {"user_id": session["account_num"]}
        addresses = db.execute(text("select * from addresses where user_id = :user_id and is_active = 'Yes'"), params).all()
        return render_template("delete_addresses.html", addresses=addresses)
    else:
        params = {"user_id": session["account_num"]}
        addresses = db.execute(text("select * from addresses where user_id = :user_id and is_active = 'Yes'"), params).all()
        return render_template("delete_addresses.html", addresses=addresses)

@app.route("/my_account/edit", methods=["Get", "POST"])
@login_required
@customer_page
def edit_address():
    if request.method == "POST":
        address_id = request.form.get("address_id")
        reciever = request.form.get("reciever")
        contact = request.form.get("contact_number")
        address1 = request.form.get("address_1")
        address2 = request.form.get("address_2")
        city = request.form.get("city")
        zip = request.form.get("zip")
        state = request.form.get("state")
        is_default = request.form.get("default_address")
        if is_default == "on":
            is_default == True
        else:
            is_default == False

        params={"user_id":session["account_num"], "address_id":address_id, "reciever":reciever, "contact":contact, "address1":address1, "address2":address2, "city":city, "zip":zip, "state":state}

        if is_default:
            db.execute(text("update addresses set default_address = 'No' where user_id = :user_id"), params)
            db.commit()
            db.execute(text("update addresses set default_address = 'Yes', reciever = :reciever, contact_number = :contact, address_line_1 = :address1, address_line_2 = :address2, city = :city, state = :state, zip = :zip where address_id = :address_id"), params)
            db.commit()
        else:
            db.execute(text("update addresses set default_address = 'No', reciever = :reciever, contact_number = :contact, address_line_1 = :address1, address_line_2 = :address2, city = :city, state = :state, zip = :zip where address_id = :address_id"), params)
            db.commit()

        addresses = db.execute(text("select * from addresses where user_id = :user_id and default_address = 'No' and is_active = 'Yes'"), params).all()
        return render_template("edit_address.html", addresses=addresses)

    else:
        params = {"user_id":session["account_num"]}
        addresses = db.execute(text("select * from addresses where user_id = :user_id and default_address = 'No' and is_active = 'Yes'"), params).all()
        return render_template("edit_address.html", addresses=addresses)

@app.route("/my_account/edit_default", methods=["Get", "POST"])
@login_required
@customer_page
def edit_default_address():
    if request.method == "POST":
        address_id = request.form.get("address_id")
        reciever = request.form.get("reciever")
        contact = request.form.get("contact_number")
        address1 = request.form.get("address_1")
        address2 = request.form.get("address_2")
        city = request.form.get("city")
        zip = request.form.get("zip")
        state = request.form.get("state")


        params={"user_id":session["account_num"], "address_id":address_id, "reciever":reciever, "contact":contact, "address1":address1, "address2":address2, "city":city, "zip":zip, "state":state}
            
        db.execute(text("update addresses set default_address = 'Yes', reciever = :reciever, contact_number = :contact, address_line_1 = :address1, address_line_2 = :address2, city = :city, state = :state, zip = :zip where address_id = :address_id"), params)
        db.commit()

        addresses = db.execute(text("select * from addresses where user_id = :user_id and default_address = 'Yes' and is_active = 'Yes'"), params).all()
        return render_template("edit_address_default.html", addresses=addresses)

    else:
        params = {"user_id":session["account_num"]}
        addresses = db.execute(text("select * from addresses where user_id = :user_id and default_address = 'Yes' and is_active = 'Yes'"), params).all()
        return render_template("edit_address_default.html", addresses=addresses)

# admin routes
@app.route("/view", methods=["GET", "POST"])
@login_required
def view():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        vendor = request.form.get("vendor")
        if name:
            name = "%" + name + "%"
        else:
            name = "%"
        if description:
            description = "%" + description + "%"
        else:
            description = "%"
        if vendor:
            vendor = "%" + vendor + "%"
        else:
            vendor = "%"

        if request.form.get("category"):
            category = request.form.get("category")
        else:
            category = "%"
        if request.form.get("color"):
            color = request.form.get("color")
        else:
            color = "%"
        if request.form.get("size"):
            size = request.form.get("size")
        else:
            size = "%"


        params = {"name":name, "description":description, "vendor":vendor}
        users = db.execute(text("select user_id from users where username like :vendor and user_type = 'Vendor'"), params).all()
        final_products = []
        #iterate over users, grab all their products and filter by other values as well
        for user in users:
            params = {"name":name, "description":description, "vendor":vendor, "user_id":user[0], "size": size, "color":color, "category":category}
            products = db.execute(text("select distinct * from items join describer on (items.item_id = describer.item_id) where user_id = :user_id and item_name like :name and descript like :description and category like :category and size like :size and color like :color order by user_id"), params).all()
            if products:
                for product in products:
                    final_products.append(product)
        users = db.execute(text("select user_id, username from users")).all()
        users = db.execute(text("select user_id, username from users")).all()
        colors = db.execute(text("select distinct color from describer where color != 'N/A'")).all()
        sizes = db.execute(text("select distinct size from describer where size != 'N/A'")).all()
        categories = db.execute(text("select distinct category from describer where category != 'N/A'")).all()
        discounts = db.execute(text("select * from discounts")).all()
        return render_template("view.html", products=final_products, users=users, colors=colors, sizes=sizes, categories=categories, discounts=discounts)
    else:
        products = db.execute(text("select * from items order by user_id")).all()
        users = db.execute(text("select user_id, username from users")).all()
        colors = db.execute(text("select distinct color from describer where color != 'N/A'")).all()
        sizes = db.execute(text("select distinct size from describer where size != 'N/A'")).all()
        categories = db.execute(text("select distinct category from describer where category != 'N/A'")).all()
        discounts = db.execute(text("select * from discounts")).all()
        return render_template("view.html", products=products, users=users, colors=colors, sizes=sizes, categories=categories, discounts=discounts)
    

@app.route("/item/<item_id>", methods=["GET", "POST"])
@login_required
def item_page(item_id):
    if request.method == "POST":
        if not request.form.get("isFilter"):

            user_id = session["account_num"]
            variation = request.form.get("color_size")
            quanitity = request.form.get("quant")
            params = {"user_id":user_id, "item_id":item_id, "color_id":variation, "quantity":quanitity}
            in_cart = db.execute(text("select * from cart where user_id = :user_id and item_id = :item_id and color_id = :color_id"), params).all()
            if len(in_cart) > 0:
                print(quanitity)
                print(in_cart)
                print(in_cart[0][3])
                quanitity = in_cart[0][3] + int(quanitity)
                params = {"user_id":user_id, "item_id":item_id, "quant":quanitity, "color_id":variation}
                db.execute(text("update cart set quantity = :quant where user_id = :user_id and item_id = :item_id and color_id = :color_id"), params)
                db.commit()
            else:
                db.execute(text("insert into cart (user_id, item_id, quantity, color_id) values (:user_id, :item_id, :quantity, :color_id)"), params)
                db.commit()

            products = db.execute(text("select * from items order by user_id")).all()
            users = db.execute(text("select user_id, username from users")).all()
            colors = db.execute(text("select distinct color from describer where color != 'N/A'")).all()
            sizes = db.execute(text("select distinct size from describer where size != 'N/A'")).all()
            categories = db.execute(text("select distinct category from describer where category != 'N/A'")).all()
            discounts = db.execute(text("select * from discounts")).all()

            return render_template("view.html", products=products, users=users, colors=colors, sizes=sizes, categories=categories, discounts=discounts)
        else:
            params = {"item_id":item_id}
            product = db.execute(text("select * from items where item_id = :item_id"), params).all()
            users = db.execute(text("select * from users")).all()
            reviews = db.execute(text("select review_text, time_review, stars, email from reviews join users on (reviews.user_id = users.user_id) where reviews.item_id = :item_id"), params).all()

            if request.form.get("filter") != "N/A":
                params = {"stars":request.form.get("filter"), "item_id":item_id}

                #execute statements where filter is used
                if request.form.get("sort") == "Ratings":
                    reviews = db.execute(text("select review_text, time_review, stars, email from reviews join users on (reviews.user_id = users.user_id) where reviews.stars = :stars and reviews.item_id = :item_id order by stars"), params).all()
                elif request.form.get("sort") == "Time":
                    reviews = db.execute(text("select review_text, time_review, stars, email from reviews join users on (reviews.user_id = users.user_id) where reviews.stars = :stars and reviews.item_id = :item_id order by time_review"), params).all()
                else:
                    reviews = db.execute(text("select review_text, time_review, stars, email from reviews join users on (reviews.user_id = users.user_id) where reviews.stars = :stars and reviews.item_id = :item_id"), params).all()

            else:
                #execute statements where filter is not used
                if request.form.get("sort") == "Ratings":
                    reviews = db.execute(text("select review_text, time_review, stars, email from reviews join users on (reviews.user_id = users.user_id) where reviews.item_id = :item_id order by stars"), params).all()
                elif request.form.get("sort") == "Time":
                    reviews = db.execute(text("select review_text, time_review, stars, email from reviews join users on (reviews.user_id = users.user_id) where reviews.item_id = :item_id order by time_review"), params).all()
            
            variations = db.execute(text("select * from describer where item_id = :item_id"), params).all()
            discounts = db.execute(text("select * from discounts")).all()
            params = {"id":item_id}
            images = db.execute(text("select * from images where item_id = :id"), params).all()
            return render_template("view_item.html", product=product[0], users=users, reviews=reviews, discounts=discounts, variations=variations, images=images)
        
    else:
        params = {"item_id":item_id}
        product = db.execute(text("select * from items where item_id = :item_id"), params).all()
        reviews = db.execute(text("select review_text, time_review, stars, email from reviews join users on (reviews.user_id = users.user_id) where reviews.item_id = :item_id"), params).all()
        variations = db.execute(text("select * from describer where item_id = :item_id"), params).all()
        discounts = db.execute(text("select * from discounts")).all()
        users = db.execute(text("select * from users")).all()
        params = {"id":item_id}
        images = db.execute(text("select * from images where item_id = :id"), params).all()
        return render_template("view_item.html", product=product[0], users=users, reviews=reviews, discounts=discounts, variations=variations, images=images)
    

@app.route("/reviews", methods=["GET", "POST"])
@login_required
@customer_page
def make_review():   
    if request.method == "POST":
        stars = request.form.get("stars")
        description = request.form.get("description")
        item_id = request.form.get("item_id")

        if not stars or not description:
            return apology("Missing info")
        
        params = {"stars":stars, "description":description, "user_id":session["account_num"], "item_id":item_id}
        db.execute(text("insert into reviews (user_id, item_id, review_text, time_review, stars) values (:user_id, :item_id, :description, now(), :stars)"), params)
        db.commit()

        params = {"user_id":session["account_num"]}
        products_able_to_review = db.execute(text("select items.item_id, items.item_name, items.price, items.descript from items join order_items on (items.item_id = order_items.item_id) join orders on (order_items.order_id = orders.order_id) where orders.user_id = :user_id"), params).all()
        return render_template("reviews.html", products = products_able_to_review)
    
    else:
        params = {"user_id":session["account_num"]}
        products_able_to_review = db.execute(text("select items.item_id, items.item_name, items.price, items.descript from items join order_items on (items.item_id = order_items.item_id) join orders on (order_items.order_id = orders.order_id) where orders.user_id = :user_id"), params).all()
        return render_template("reviews.html", products = products_able_to_review)


@app.route("/admin/add", methods=["GET", "POST"])
@login_required
@admin_page
def admin_add():
    if request.method == "POST":
        name = request.form.get("item_name")
        desc = request.form.get("desc")
        price = request.form.get("item_price")
        stock = request.form.get("curr_stock")
        image = request.form.get("image_link")
        warranty = request.form.get("warranty_length")
        color = request.form.getlist("color")
        size = request.form.getlist("size")
        dis_percent = request.form.get("discount_percent")
        dis_length = request.form.get("discount_length")
        dis_time_type = request.form.get("discount_time_type")
        if not request.form.get("vendor"):
            return apology("No vendor selected")
        params = {"user":request.form.get("vendor"), "name":name}
        item_check = db.execute(text("select * from items where user_id = :user and item_name = :name"), params).all()
        
        if len(item_check) < 1:

            params = {"name":name, "price":price, "stock":stock, "user":request.form.get("vendor"), "warranty":warranty, "desc":desc}
            db.execute(text("insert into items (item_name, price, in_stock, user_id, warranty_length, descript) values (:name, :price, :stock, :user, :warranty, :desc)"), params)
            db.commit()
            item_id = db.execute(text("select item_id from items order by item_id desc")).all()[0][0]
            params = {"image":image, "item_id":item_id}
            db.execute(text("insert into images (image_url, item_id) values (:image, :item_id)"), params)
            db.commit()

            curr_items = db.execute(text("select max(item_id) from items")).all()
            for i in range(len(color)):
                curr_color = color[i]
                curr_size = size[i]
                if curr_color == "":
                    curr_color = "N/A"
                if curr_size == "":
                    curr_size = "N/A"
                if (curr_color != "N/A") and (curr_size != "N/A"):
                    params = {"size":curr_size, "color":curr_color, "id":curr_items[0][0]}
                    db.execute(text("insert into describer (size, color, item_id) values (:size, :color, :id)"), params)
                    db.commit()

            if dis_percent != "" and dis_length != "" and dis_time_type != "%":
                current_date = datetime.now()
                if dis_time_type == "minutes":
                    discount_expire = current_date + timedelta(seconds=int(dis_length) * 60)
                    params = {"expire":discount_expire, "percent":dis_percent, "id":curr_items[0][0]}
                    db.execute(text("insert into discounts (discount_expire, discount_percent, item_id) values (:expire, :percent, :id)"), params)
                    db.commit()
                elif dis_time_type == "hours":
                    discount_expire = current_date + timedelta(hours=int(dis_length))
                    params = {"expire":discount_expire, "percent":dis_percent, "id":curr_items[0][0]}
                    db.execute(text("insert into discounts (discount_expire, discount_percent, item_id) values (:expire, :percent, :id)"), params)
                    db.commit()
                elif dis_time_type == "days":
                    discount_expire = current_date + timedelta(days=int(dis_length))
                    params = {"expire":discount_expire, "percent":dis_percent, "id":curr_items[0][0]}
                    db.execute(text("insert into discounts (discount_expire, discount_percent, item_id) values (:expire, :percent, :id)"), params)
                    db.commit()
                elif dis_time_type == "weeks":
                    discount_expire = current_date + timedelta(weeks=int(dis_length))
                    params = {"expire":discount_expire, "percent":dis_percent, "id":curr_items[0][0]}
                    db.execute(text("insert into discounts (discount_expire, discount_percent, item_id) values (:expire, :percent, :id)"), params)
                    db.commit()
                elif dis_time_type == "months":
                    discount_expire = current_date + timedelta(days=int(dis_length) * 31)
                    params = {"expire":discount_expire, "percent":dis_percent, "id":curr_items[0][0]}
                    db.execute(text("insert into discounts (discount_expire, discount_percent, item_id) values (:expire, :percent, :id)"), params)
                    db.commit()
            else:
                params = {"expire":datetime.now(), "percent":0, "id":curr_items[0][0]}
                db.execute(text("insert into discounts (discount_expire, discount_percent, item_id) values (:expire, :percent, :id)"), params)
                db.commit()
        else:
            return apology("Item already exists")

        vendors = db.execute(text("select user_id, username from users where user_type = 'Vendor'")).all()
        return render_template("admin_add_item.html", vendors=vendors)
    else:
        vendors = db.execute(text("select user_id, username from users where user_type = 'Vendor'")).all()
        return render_template("admin_add_item.html", vendors=vendors)

@app.route("/admin/delete", methods=["GET", "POST"])
@login_required
@admin_page
def admin_delete():
    if request.method == "POST":
        product = request.form.get("product_id")
        params = {"product_id":product}
        db.execute(text("delete from images where item_id = :product_id"), params)
        db.execute(text("delete from order_items where item_id = :product_id"), params)
        db.execute(text("delete from describer where item_id = :product_id"), params)
        db.execute(text("delete from cart where item_id = :product_id"), params)
        db.execute(text("delete from complaints where item_id = :product_id"), params)
        db.execute(text("delete from reviews where item_id = :product_id"), params)
        db.execute(text("delete from discounts where item_id = :product_id"), params)
        db.execute(text("delete from items where item_id = :product_id"), params)
        db.commit()

        products = db.execute(text("select * from items order by user_id")).all()
        users = db.execute(text("select user_id, username from users")).all()
        return render_template("admin_delete.html", products=products, users=users)
    
    else:
        products = db.execute(text("select * from items order by user_id")).all()
        users = db.execute(text("select user_id, username from users")).all()
        return render_template("admin_delete.html", products=products, users=users)

@app.route("/admin/edit", methods=["GET", "POST"])
@login_required
@admin_page
def admin_edit():
    if request.method == "POST":
        items = db.execute(text("select * from items")).all()

        name = request.form.get("new_name")
        price = request.form.get("new_price")
        stock = request.form.get("new_stock")
        warranty = request.form.get("new_warranty")
        desc = request.form.get("new_desc")
        
        if (name != "" and items[0][1] != name):
            params = {"new_name":name, "name":items[0][1], "account_num":session["account_num"]}
            db.execute(text("update items set item_name = :new_name where item_name = :name and user_id = :account_num"), params)
            db.commit()
        
        if (price != "" and items[0][2] != price):
            params = {"new_price":price, "name":items[0][1], "account_num":session["account_num"]}
            db.execute(text("update items set price = :new_price where item_name = :name and user_id = :account_num"), params)
            db.commit()

        if (stock != "" and items[0][3] != price):
            params = {"new_stock":stock, "name":items[0][1], "account_num":session["account_num"]}
            db.execute(text("update items set in_stock = :new_stock where item_name = :name and user_id = :account_num"), params)
            db.commit()

        if (warranty != "" and items[0][5] != warranty):
            params = {"new_warranty":warranty, "name":items[0][1], "account_num":session["account_num"]}
            db.execute(text("update items set warranty_length = :new_warranty where item_name = :name and user_id = :account_num"), params)
            db.commit()

        if (desc != "" and items[0][6] != desc):
            params = {"new_desc":desc, "name":items[0][1], "account_num":session["account_num"]}
            db.execute(text("update items set descript = :new_desc where item_name = :name and user_id = :account_num"), params)
            db.commit()

        new_size = request.form.getlist("new_size")
        new_color = request.form.getlist("new_color")
        hidden_item_id = request.form.get("item_hidden_id")
        hidden_id = request.form.getlist("hidden_id")
        removals = request.form.getlist("removal")
        new_percent = request.form.get("new_percent")

        for i in range(len(request.form.getlist("hidden_id"))):

            if hidden_id[i] != "none" and removals[i] != "yes":
                
                if new_size[i] != "":
                    if new_color[i] != "":
                        params = {"size":new_size[i], "color":new_color[i], "id":request.form.getlist("hidden_id")[i]}
                        db.execute(text("update describer set size = :size, color = :color where color_id = :id"), params)
                        db.commit()
                    else:
                        params = {"size":new_size[i], "id":request.form.getlist("hidden_id")[i]}
                        db.execute(text("update describer set size = :size where color_id = :id"), params)
                        db.commit()
                
                elif new_color[i] != "" and new_size[i] == "":
                    params = {"color":new_color[i], "id":request.form.getlist("hidden_id")[i]}
                    db.execute(text("update describer set color = :color where color_id = :id"), params)
                    db.commit()

            elif hidden_id[i] == "none" and removals[i] != "yes":
                
                if new_size[i] != "":
                    if new_color[i] != "":
                        params = {"size":new_size[i], "color":new_color[i], "item_id":hidden_item_id}
                        db.execute(text("insert into describer (size, color, item_id) values (:size, :color, :item_id)"), params)
                        db.commit()
                    else:
                        params = {"size":new_size[i], "color":"N/A", "item_id":hidden_item_id}
                        db.execute(text("insert into describer (size, color, item_id) values (:size, :color, :item_id)"), params)
                        db.commit()
                
                elif new_color[i] != "" and new_size[i] == "":
                    params = {"size":"N/A", "color":new_color[i], "item_id":hidden_item_id}
                    db.execute(text("insert into describer (size, color, item_id) values (:size, :color, :item_id)"), params)
                    db.commit()

            elif hidden_id[i] != "none" and removals[i] == "yes":
                params = {"id":request.form.getlist("hidden_id")[i]}
                db.execute(text("delete from describer where color_id = :id;"), params)
                db.commit()

        if new_percent != "":
            params = {"percent":new_percent, "id":hidden_item_id}
            db.execute(text("update discounts set discount_percent = :percent where item_id = :id"), params)
            db.commit()

        form_month = request.form.get("month_input")
        form_day = request.form.get("day_input")
        form_year = request.form.get("year_input")
        form_hour = request.form.get("hour_input")
        form_minute = request.form.get("minute_input")
        form_second = request.form.get("second_input")
        params = {"id":hidden_item_id}
        discount_original = db.execute(text("select discount_expire from discounts join items on (discounts.item_id = items.item_id) where items.item_id = :id"), params).all()[0][0]
        final_new_date = ""

        if form_month != "":
            final_new_date += form_month + "/"

        else:
            final_new_date += discount_original.strftime("%m") + "/"

        if form_day != "":
            final_new_date += form_day + "/"

        else:
            final_new_date += discount_original.strftime("%d") + "/"

        if form_year != "":
            final_new_date += form_year + " "

        else:
            final_new_date += discount_original.strftime("%Y") + " "

        if form_hour != "":
            final_new_date += form_hour + ":"

        else:
            final_new_date += discount_original.strftime("%H") + ":"

        if form_minute != "":
            final_new_date += form_minute + ":"

        else:
            final_new_date += discount_original.strftime("%M") + ":"

        if form_second != "":
            final_new_date += form_second

        else:
            final_new_date += discount_original.strftime("%S")

        final_new_date = datetime.strptime(final_new_date, "%m/%d/%Y %H:%M:%S")
        params = {"new_date":final_new_date, "id":hidden_item_id}
        db.execute(text("update discounts set discount_expire = :new_date where item_id = :id"), params)
        db.commit()

        params = {"account_num":session["account_num"]}
        items = db.execute(text("select * from items where user_id = :account_num"),params).all()
        params = {"id":session["account_num"]}
        describers = db.execute(text("select color_id, size, color, category, describer.item_id from describer join items on (describer.item_id = items.item_id) where user_id = :id"), params).all()
        params = {"id":session["account_num"]}
        discounts = db.execute(text("select discount_id, discount_expire, discount_percent, discounts.item_id from discounts join items on (discounts.item_id = items.item_id) where user_id = :id"), params).all()
        formatted_discounts = []

        for i in discounts:
            day = i[1].strftime("%d")
            month = i[1].strftime("%m")
            year = i[1].strftime("%Y")
            second = i[1].strftime("%S")
            minute = i[1].strftime("%M")
            hour = i[1].strftime("%H")
            formatted_discounts.append([i[0], month, day, year, hour, minute, second, i[2], i[3]])

        expires_in = []
        current_time = datetime.now()
        ct_year = int(current_time.strftime("%Y")) # CT stands for current time
        
        for i in discounts:
            difference = datetime.now() - i[1]
            negative_difference = i[1] - datetime.now()

            if i[1] < datetime.now():

                if difference >= timedelta(days=365):
                    expires_in.append([f"This discount is expired by {(difference.days//365)%365}+ year(s).", i[3]])

                elif difference >= timedelta(days=31):
                    expires_in.append([f"This discount is expired by {(difference.days//31)%31}+ month(s).", i[3]])

                elif difference >= timedelta(weeks=1):
                    expires_in.append([f"This discount is expired by {(difference.days//7)%7}+ week(s).", i[3]])

                elif difference >= timedelta(days=1):
                    expires_in.append([f"This discount is expired by {difference.days}+ day(s).", i[3]])

                elif difference >= timedelta(hours=1):
                    expires_in.append([f"This discount is expired by {difference.seconds//3600}+ hour(s).", i[3]])
                    
                elif difference >= timedelta(minutes=1):
                    expires_in.append([f"This discount is expired by {(difference.seconds//60)%60}+ minute(s).", i[3]])
                
                elif difference >= timedelta(seconds=1):
                    expires_in.append([f"This discount is expired by {difference.seconds}+ second(s).", i[3]])
            
            else:
                
                if negative_difference >= timedelta(days=365):
                    expires_in.append([f"This discount expires in {(negative_difference.days//365)%365}+ year(s).", i[3]])

                elif negative_difference >= timedelta(days=31):
                    expires_in.append([f"This discount expires in {(negative_difference.days//31)%31}+ month(s).", i[3]])

                elif negative_difference >= timedelta(weeks=1):
                    expires_in.append([f"This discount expires in {(negative_difference.days//7)%7}+ week(s).", i[3]])

                elif negative_difference >= timedelta(days=1):
                    expires_in.append([f"This discount expires in {negative_difference.days}+ days(s).", i[3]])

                elif negative_difference >= timedelta(hours=1):
                    expires_in.append([f"This discount expires in {negative_difference.seconds//3600}+ hours(s).", i[3]])

                elif negative_difference >= timedelta(minutes=1):
                    expires_in.append([f"This discount expires in {(negative_difference.seconds//60)%60}+ minutes(s).", i[3]])
                    
                elif negative_difference >= timedelta(seconds=1):
                    expires_in.append([f"This discount expires in {negative_difference.seconds}+ seconds(s).", i[3]])

        images = db.execute(text("select image_id, image_url, items.item_id, users.user_id from images join items on (images.item_id = items.item_id) join users on (items.user_id = users.user_id)")).all()

        return render_template("edit_item.html", items=items, describers=describers, discounts=formatted_discounts, expires_in=expires_in, ct_year=ct_year, images=images)
    
    else:
        items = db.execute(text("select * from items")).all()
        describers = db.execute(text("select color_id, size, color, category, describer.item_id from describer join items on (describer.item_id = items.item_id)")).all()
        discounts = db.execute(text("select discount_id, discount_expire, discount_percent, discounts.item_id from discounts join items on (discounts.item_id = items.item_id)")).all()
        formatted_discounts = []

        for i in discounts:
            day = i[1].strftime("%d")
            month = i[1].strftime("%m")
            year = i[1].strftime("%Y")
            second = i[1].strftime("%S")
            minute = i[1].strftime("%M")
            hour = i[1].strftime("%H")
            formatted_discounts.append([i[0], month, day, year, hour, minute, second, i[2], i[3]])

        expires_in = []
        current_time = datetime.now()
        ct_year = int(current_time.strftime("%Y")) # CT stands for current time
        
        for i in discounts:
            difference = datetime.now() - i[1]
            negative_difference = i[1] - datetime.now()

            if i[1] < datetime.now():

                if difference >= timedelta(days=365):
                    expires_in.append([f"This discount is expired by {(difference.days//365)%365}+ year(s).", i[3]])

                elif difference >= timedelta(days=31):
                    expires_in.append([f"This discount is expired by {(difference.days//31)%31}+ month(s).", i[3]])

                elif difference >= timedelta(weeks=1):
                    expires_in.append([f"This discount is expired by {(difference.days//7)%7}+ week(s).", i[3]])

                elif difference >= timedelta(days=1):
                    expires_in.append([f"This discount is expired by {difference.days}+ day(s).", i[3]])

                elif difference >= timedelta(hours=1):
                    expires_in.append([f"This discount is expired by {difference.seconds//3600}+ hour(s).", i[3]])
                    
                elif difference >= timedelta(minutes=1):
                    expires_in.append([f"This discount is expired by {(difference.seconds//60)%60}+ minute(s).", i[3]])
                
                elif difference >= timedelta(seconds=1):
                    expires_in.append([f"This discount is expired by {difference.seconds}+ second(s).", i[3]])
            
            else:
                
                if negative_difference >= timedelta(days=365):
                    expires_in.append([f"This discount expires in {(negative_difference.days//365)%365}+ year(s).", i[3]])

                elif negative_difference >= timedelta(days=31):
                    expires_in.append([f"This discount expires in {(negative_difference.days//31)%31}+ month(s).", i[3]])

                elif negative_difference >= timedelta(weeks=1):
                    expires_in.append([f"This discount expires in {(negative_difference.days//7)%7}+ week(s).", i[3]])

                elif negative_difference >= timedelta(days=1):
                    expires_in.append([f"This discount expires in {negative_difference.days}+ days(s).", i[3]])

                elif negative_difference >= timedelta(hours=1):
                    expires_in.append([f"This discount expires in {negative_difference.seconds//3600}+ hours(s).", i[3]])

                elif negative_difference >= timedelta(minutes=1):
                    expires_in.append([f"This discount expires in {(negative_difference.seconds//60)%60}+ minutes(s).", i[3]])
                    
                elif negative_difference >= timedelta(seconds=1):
                    expires_in.append([f"This discount expires in {negative_difference.seconds}+ seconds(s).", i[3]])

        return render_template("edit_item.html", items=items, describers=describers, discounts=formatted_discounts, expires_in=expires_in, ct_year=ct_year)

# vendor routes
@app.route("/vendor", methods=["GET", "POST"])
@login_required
@vendor_page
def vendor():
    params = {"account_num":session["account_num"]}
    products = db.execute(text("select * from items where user_id = :account_num"),params).all()
    discounts = db.execute(text("select * from discounts")).all()
    return render_template("vendor.html", products=products, discounts=discounts)

@app.route("/vendor/add", methods=["GET", "POST"])
@login_required
@vendor_page
def add_item():
    if request.method == "POST":
        name = request.form.get("item_name")
        desc = request.form.get("desc")
        price = request.form.get("item_price")
        stock = request.form.get("curr_stock")
        image = request.form.get("image_link")
        warranty = request.form.get("warranty_length")
        category = request.form.get("category")
        color = request.form.getlist("color")
        size = request.form.getlist("size")
        dis_percent = request.form.get("discount_percent")
        dis_length = request.form.get("discount_length")
        dis_time_type = request.form.get("discount_time_type")
        params = {"email":session["user_id"]}
        user = db.execute(text("select * from users where email = :email"), params).all()
        params = {"user":user[0][0], "name":name}
        item_check = db.execute(text("select * from items where user_id = :user and item_name = :name"), params).all()
        
        if len(item_check) < 1:

            params = {"name":name, "price":price, "stock":stock, "user":user[0][0], "warranty":warranty, "desc":desc}
            db.execute(text("insert into items (item_name, price, in_stock, user_id, warranty_length, descript) values (:name, :price, :stock, :user, :warranty, :desc)"), params)
            db.commit()
            item_id = db.execute(text("select item_id from items order by item_id desc")).all()[0][0]
            params = {"image":image, "item_id":item_id}
            db.execute(text("insert into images (image_url, item_id) values (:image, :item_id)"), params)
            db.commit()

            curr_items = db.execute(text("select max(item_id) from items")).all()
            for i in range(len(color)):
                curr_color = color[i]
                curr_size = size[i]
                if curr_color == "":
                    curr_color = "N/A"
                if curr_size == "":
                    curr_size = "N/A"
                if (curr_color != "N/A") and (curr_size != "N/A"):
                    params = {"size":curr_size, "color":curr_color, "category":category, "id":curr_items[0][0]}
                    db.execute(text("insert into describer (size, color, category, item_id) values (:size, :color, :category, :id)"), params)
                    db.commit()

            if dis_percent != "" and dis_length != "" and dis_time_type != "%":
                current_date = datetime.now()
                if dis_time_type == "minutes":
                    discount_expire = current_date + timedelta(seconds=int(dis_length) * 60)
                    params = {"expire":discount_expire, "percent":dis_percent, "id":curr_items[0][0]}
                    db.execute(text("insert into discounts (discount_expire, discount_percent, item_id) values (:expire, :percent, :id)"), params)
                    db.commit()
                elif dis_time_type == "hours":
                    discount_expire = current_date + timedelta(hours=int(dis_length))
                    params = {"expire":discount_expire, "percent":dis_percent, "id":curr_items[0][0]}
                    db.execute(text("insert into discounts (discount_expire, discount_percent, item_id) values (:expire, :percent, :id)"), params)
                    db.commit()
                elif dis_time_type == "days":
                    discount_expire = current_date + timedelta(days=int(dis_length))
                    params = {"expire":discount_expire, "percent":dis_percent, "id":curr_items[0][0]}
                    db.execute(text("insert into discounts (discount_expire, discount_percent, item_id) values (:expire, :percent, :id)"), params)
                    db.commit()
                elif dis_time_type == "weeks":
                    discount_expire = current_date + timedelta(weeks=int(dis_length))
                    params = {"expire":discount_expire, "percent":dis_percent, "id":curr_items[0][0]}
                    db.execute(text("insert into discounts (discount_expire, discount_percent, item_id) values (:expire, :percent, :id)"), params)
                    db.commit()
                elif dis_time_type == "months":
                    discount_expire = current_date + timedelta(days=int(dis_length) * 31)
                    params = {"expire":discount_expire, "percent":dis_percent, "id":curr_items[0][0]}
                    db.execute(text("insert into discounts (discount_expire, discount_percent, item_id) values (:expire, :percent, :id)"), params)
                    db.commit()
            else:
                params = {"expire":datetime.now(), "percent":0, "id":curr_items[0][0]}
                db.execute(text("insert into discounts (discount_expire, discount_percent, item_id) values (:expire, :percent, :id)"), params)
                db.commit()

        else:
            return apology("Item already exists")
        
        return render_template("add_item.html")
    else:
        return render_template("add_item.html")
    

@app.route("/vendor/delete", methods=["GET", "POST"])
@login_required
@vendor_page
def vendor_delete():
    if request.method == "POST":
        product = request.form.get("product_id")
        params = {"product_id":product, "user_id":session["account_num"]}
        db.execute(text("delete from images where item_id = :product_id"), params)
        db.execute(text("delete from order_items where item_id = :product_id"), params)
        db.execute(text("delete from describer where item_id = :product_id"), params)
        db.execute(text("delete from cart where item_id = :product_id"), params)
        db.execute(text("delete from complaints where item_id = :product_id"), params)
        db.execute(text("delete from reviews where item_id = :product_id"), params)
        db.execute(text("delete from discounts where item_id = :product_id"), params)
        db.execute(text("delete from items where item_id = :product_id"), params)
        db.commit()

        products = db.execute(text("select * from items where user_id = :user_id order by user_id"), params).all()
        return render_template("vendor_delete.html", products=products)
    
    else:
        params = {"user_id":session["account_num"]}
        products = db.execute(text("select * from items where user_id = :user_id order by user_id"), params).all()
        return render_template("vendor_delete.html", products=products)
    
@app.route("/vendor/edit", methods=["GET", "POST"])
@login_required
@vendor_page
def edit_vendor_item():
    if request.method == "POST":
        params = {"account_num":session["account_num"]}
        items = db.execute(text("select * from items where user_id = :account_num"),params).all()

        name = request.form.get("new_name")
        price = request.form.get("new_price")
        stock = request.form.get("new_stock")
        warranty = request.form.get("new_warranty")
        desc = request.form.get("new_desc")
        
        if (name != "" and items[0][1] != name):
            params = {"new_name":name, "name":items[0][1], "account_num":session["account_num"]}
            db.execute(text("update items set item_name = :new_name where item_name = :name and user_id = :account_num"), params)
            db.commit()
        
        if (price != "" and items[0][2] != price):
            params = {"new_price":price, "name":items[0][1], "account_num":session["account_num"]}
            db.execute(text("update items set price = :new_price where item_name = :name and user_id = :account_num"), params)
            db.commit()

        if (stock != "" and items[0][3] != price):
            params = {"new_stock":stock, "name":items[0][1], "account_num":session["account_num"]}
            db.execute(text("update items set in_stock = :new_stock where item_name = :name and user_id = :account_num"), params)
            db.commit()

        if (warranty != "" and items[0][5] != warranty):
            params = {"new_warranty":warranty, "name":items[0][1], "account_num":session["account_num"]}
            db.execute(text("update items set warranty_length = :new_warranty where item_name = :name and user_id = :account_num"), params)
            db.commit()

        if (desc != "" and items[0][6] != desc):
            params = {"new_desc":desc, "name":items[0][1], "account_num":session["account_num"]}
            db.execute(text("update items set descript = :new_desc where item_name = :name and user_id = :account_num"), params)
            db.commit()

        new_size = request.form.getlist("new_size")
        new_color = request.form.getlist("new_color")
        hidden_item_id = request.form.get("item_hidden_id")
        hidden_id = request.form.getlist("hidden_id")
        removals = request.form.getlist("removal")
        new_percent = request.form.get("new_percent")

        for i in range(len(request.form.getlist("hidden_id"))):

            if hidden_id[i] != "none" and removals[i] != "yes":
                
                if new_size[i] != "":
                    if new_color[i] != "":
                        params = {"size":new_size[i], "color":new_color[i], "id":request.form.getlist("hidden_id")[i]}
                        db.execute(text("update describer set size = :size, color = :color where color_id = :id"), params)
                        db.commit()
                    else:
                        params = {"size":new_size[i], "id":request.form.getlist("hidden_id")[i]}
                        db.execute(text("update describer set size = :size where color_id = :id"), params)
                        db.commit()
                
                elif new_color[i] != "" and new_size[i] == "":
                    params = {"color":new_color[i], "id":request.form.getlist("hidden_id")[i]}
                    db.execute(text("update describer set color = :color where color_id = :id"), params)
                    db.commit()

            elif hidden_id[i] == "none" and removals[i] != "yes":
                
                if new_size[i] != "":
                    if new_color[i] != "":
                        params = {"size":new_size[i], "color":new_color[i], "item_id":hidden_item_id}
                        db.execute(text("insert into describer (size, color, item_id) values (:size, :color, :item_id)"), params)
                        db.commit()
                    else:
                        params = {"size":new_size[i], "color":"N/A", "item_id":hidden_item_id}
                        db.execute(text("insert into describer (size, color, item_id) values (:size, :color, :item_id)"), params)
                        db.commit()
                
                elif new_color[i] != "" and new_size[i] == "":
                    params = {"size":"N/A", "color":new_color[i], "item_id":hidden_item_id}
                    db.execute(text("insert into describer (size, color, item_id) values (:size, :color, :item_id)"), params)
                    db.commit()

            elif hidden_id[i] != "none" and removals[i] == "yes":
                params = {"id":request.form.getlist("hidden_id")[i]}
                db.execute(text("delete from describer where color_id = :id;"), params)
                db.commit()

        if new_percent != "":
            params = {"percent":new_percent, "id":hidden_item_id}
            db.execute(text("update discounts set discount_percent = :percent where item_id = :id"), params)
            db.commit()

        form_month = request.form.get("month_input")
        form_day = request.form.get("day_input")
        form_year = request.form.get("year_input")
        form_hour = request.form.get("hour_input")
        form_minute = request.form.get("minute_input")
        form_second = request.form.get("second_input")
        params = {"id":hidden_item_id}
        discount_original = db.execute(text("select discount_expire from discounts join items on (discounts.item_id = items.item_id) where items.item_id = :id"), params).all()[0][0]
        final_new_date = ""

        if form_month != "":
            final_new_date += form_month + "/"

        else:
            final_new_date += discount_original.strftime("%m") + "/"

        if form_day != "":
            final_new_date += form_day + "/"

        else:
            final_new_date += discount_original.strftime("%d") + "/"

        if form_year != "":
            final_new_date += form_year + " "

        else:
            final_new_date += discount_original.strftime("%Y") + " "

        if form_hour != "":
            final_new_date += form_hour + ":"

        else:
            final_new_date += discount_original.strftime("%H") + ":"

        if form_minute != "":
            final_new_date += form_minute + ":"

        else:
            final_new_date += discount_original.strftime("%M") + ":"

        if form_second != "":
            final_new_date += form_second

        else:
            final_new_date += discount_original.strftime("%S")

        final_new_date = datetime.strptime(final_new_date, "%m/%d/%Y %H:%M:%S")
        params = {"new_date":final_new_date, "id":hidden_item_id}
        db.execute(text("update discounts set discount_expire = :new_date where item_id = :id"), params)
        db.commit()

        params = {"account_num":session["account_num"]}
        items = db.execute(text("select * from items where user_id = :account_num"),params).all()
        params = {"id":session["account_num"]}
        describers = db.execute(text("select color_id, size, color, category, describer.item_id from describer join items on (describer.item_id = items.item_id) where user_id = :id"), params).all()
        params = {"id":session["account_num"]}
        discounts = db.execute(text("select discount_id, discount_expire, discount_percent, discounts.item_id from discounts join items on (discounts.item_id = items.item_id) where user_id = :id"), params).all()
        formatted_discounts = []

        for i in discounts:
            day = i[1].strftime("%d")
            month = i[1].strftime("%m")
            year = i[1].strftime("%Y")
            second = i[1].strftime("%S")
            minute = i[1].strftime("%M")
            hour = i[1].strftime("%H")
            formatted_discounts.append([i[0], month, day, year, hour, minute, second, i[2], i[3]])

        expires_in = []
        current_time = datetime.now()
        ct_year = int(current_time.strftime("%Y")) # CT stands for current time
        
        for i in discounts:
            difference = datetime.now() - i[1]
            negative_difference = i[1] - datetime.now()

            if i[1] < datetime.now():

                if difference >= timedelta(days=365):
                    expires_in.append([f"This discount is expired by {(difference.days//365)%365}+ year(s).", i[3]])

                elif difference >= timedelta(days=31):
                    expires_in.append([f"This discount is expired by {(difference.days//31)%31}+ month(s).", i[3]])

                elif difference >= timedelta(weeks=1):
                    expires_in.append([f"This discount is expired by {(difference.days//7)%7}+ week(s).", i[3]])

                elif difference >= timedelta(days=1):
                    expires_in.append([f"This discount is expired by {difference.days}+ day(s).", i[3]])

                elif difference >= timedelta(hours=1):
                    expires_in.append([f"This discount is expired by {difference.seconds//3600}+ hour(s).", i[3]])
                    
                elif difference >= timedelta(minutes=1):
                    expires_in.append([f"This discount is expired by {(difference.seconds//60)%60}+ minute(s).", i[3]])
                
                elif difference >= timedelta(seconds=1):
                    expires_in.append([f"This discount is expired by {difference.seconds}+ second(s).", i[3]])
            
            else:
                
                if negative_difference >= timedelta(days=365):
                    expires_in.append([f"This discount expires in {(negative_difference.days//365)%365}+ year(s).", i[3]])

                elif negative_difference >= timedelta(days=31):
                    expires_in.append([f"This discount expires in {(negative_difference.days//31)%31}+ month(s).", i[3]])

                elif negative_difference >= timedelta(weeks=1):
                    expires_in.append([f"This discount expires in {(negative_difference.days//7)%7}+ week(s).", i[3]])

                elif negative_difference >= timedelta(days=1):
                    expires_in.append([f"This discount expires in {negative_difference.days}+ days(s).", i[3]])

                elif negative_difference >= timedelta(hours=1):
                    expires_in.append([f"This discount expires in {negative_difference.seconds//3600}+ hours(s).", i[3]])

                elif negative_difference >= timedelta(minutes=1):
                    expires_in.append([f"This discount expires in {(negative_difference.seconds//60)%60}+ minutes(s).", i[3]])
                    
                elif negative_difference >= timedelta(seconds=1):
                    expires_in.append([f"This discount expires in {negative_difference.seconds}+ seconds(s).", i[3]])

        params = {"id":session["account_num"]}
        images = db.execute(text("select image_id, image_url, items.item_id, users.user_id from images join items on (images.item_id = items.item_id) join users on (items.user_id = users.user_id) where users.user_id = :id"), params).all()

        return render_template("edit_item.html", items=items, describers=describers, discounts=formatted_discounts, expires_in=expires_in, ct_year=ct_year, images=images)
    
    else:
        params = {"account_num":session["account_num"]}
        items = db.execute(text("select * from items where user_id = :account_num"),params).all()
        params = {"id":session["account_num"]}
        describers = db.execute(text("select color_id, size, color, category, describer.item_id from describer join items on (describer.item_id = items.item_id) where user_id = :id"), params).all()
        params = {"id":session["account_num"]}
        discounts = db.execute(text("select discount_id, discount_expire, discount_percent, discounts.item_id from discounts join items on (discounts.item_id = items.item_id) where user_id = :id"), params).all()
        formatted_discounts = []

        for i in discounts:
            day = i[1].strftime("%d")
            month = i[1].strftime("%m")
            year = i[1].strftime("%Y")
            second = i[1].strftime("%S")
            minute = i[1].strftime("%M")
            hour = i[1].strftime("%H")
            formatted_discounts.append([i[0], month, day, year, hour, minute, second, i[2], i[3]])

        expires_in = []
        current_time = datetime.now()
        ct_year = int(current_time.strftime("%Y")) # CT stands for current time
        
        for i in discounts:
            difference = datetime.now() - i[1]
            negative_difference = i[1] - datetime.now()

            if i[1] < datetime.now():

                if difference >= timedelta(days=365):
                    expires_in.append([f"This discount is expired by {(difference.days//365)%365}+ year(s).", i[3]])

                elif difference >= timedelta(days=31):
                    expires_in.append([f"This discount is expired by {(difference.days//31)%31}+ month(s).", i[3]])

                elif difference >= timedelta(weeks=1):
                    expires_in.append([f"This discount is expired by {(difference.days//7)%7}+ week(s).", i[3]])

                elif difference >= timedelta(days=1):
                    expires_in.append([f"This discount is expired by {difference.days}+ day(s).", i[3]])

                elif difference >= timedelta(hours=1):
                    expires_in.append([f"This discount is expired by {difference.seconds//3600}+ hour(s).", i[3]])
                    
                elif difference >= timedelta(minutes=1):
                    expires_in.append([f"This discount is expired by {(difference.seconds//60)%60}+ minute(s).", i[3]])
                
                elif difference >= timedelta(seconds=1):
                    expires_in.append([f"This discount is expired by {difference.seconds}+ second(s).", i[3]])
            
            else:
                
                if negative_difference >= timedelta(days=365):
                    expires_in.append([f"This discount expires in {(negative_difference.days//365)%365}+ year(s).", i[3]])

                elif negative_difference >= timedelta(days=31):
                    expires_in.append([f"This discount expires in {(negative_difference.days//31)%31}+ month(s).", i[3]])

                elif negative_difference >= timedelta(weeks=1):
                    expires_in.append([f"This discount expires in {(negative_difference.days//7)%7}+ week(s).", i[3]])

                elif negative_difference >= timedelta(days=1):
                    expires_in.append([f"This discount expires in {negative_difference.days}+ days(s).", i[3]])

                elif negative_difference >= timedelta(hours=1):
                    expires_in.append([f"This discount expires in {negative_difference.seconds//3600}+ hours(s).", i[3]])

                elif negative_difference >= timedelta(minutes=1):
                    expires_in.append([f"This discount expires in {(negative_difference.seconds//60)%60}+ minutes(s).", i[3]])
                    
                elif negative_difference >= timedelta(seconds=1):
                    expires_in.append([f"This discount expires in {negative_difference.seconds}+ seconds(s).", i[3]])

        params = {"id":session["account_num"]}
        images = db.execute(text("select image_id, image_url, items.item_id, users.user_id from images join items on (images.item_id = items.item_id) join users on (items.user_id = users.user_id) where users.user_id = :id"), params).all()

        return render_template("edit_item.html", items=items, describers=describers, discounts=formatted_discounts, expires_in=expires_in, ct_year=ct_year, images=images)

@app.route("/vendor/orders", methods=["GET", "POST"])
@login_required
@vendor_page
def view_orders():
    params = {"id":session["account_num"]}
    orders = db.execute(text("select * from orders join addresses on (orders.address_id = addresses.address_id) join order_items on (order_items.order_id = orders.order_id) join items on (order_items.item_id = items.item_id) where items.user_id = :id order by orders.date_ordered desc"), params).all()
    print(orders)
    if (len(orders) > 0):
        order_infos = db.execute(text("select * from orders join order_items on (orders.order_id = order_items.order_id) join describer on (order_items.color_id = describer.color_id) join items on (order_items.item_id = items.item_id) where items.user_id = :id"), params).all()
        totals = []
        for order in orders:
            total = 0
            for order_info in order_infos:
                if order_info[6] == order[0]:
                    total += order_info[7] * order_info[8]
            totals.append(total)
        totals.reverse()    
        return render_template("order.html", orders=orders, order_info=order_infos, totals=totals)
    
    else:
        return render_template("order.html", orders="None", order_info="None", totals="None")


@app.route("/vendor/order", methods=["GET", "POST"])
@login_required
@vendor_page
def confirm_orders():
    if request.method == "POST":
        params = {"order_id":request.form.get("order_id"), "ordered_item_id":request.form.get("order_item_id")}
        db.execute(text("update order_items set order_status = 'Confirmed' where ordered_item_id = :ordered_item_id"), params)
        db.commit()

        #check all items in order and set overall order status
        check_orders = db.execute(text("select order_status from order_items where order_id = :order_id"), params).all()
        flag = True

        for order in check_orders:
            if order[0] == "Pending":
                flag = False
        
        if flag:
            db.execute(text("update orders set order_status = 'Confirmed' where order_id = :order_id"), params)
            db.commit()

       
        params = {"user_id":session["account_num"]}
        orders = db.execute(text("select order_items.ordered_item_id, order_items.order_id, order_items.price, order_items.quantity, order_items.item_name, describer.size, describer.color from order_items join items on (order_items.item_id = items.item_id) join describer on (order_items.color_id = describer.color_id) where items.user_id = :user_id and order_items.order_status = 'Pending'"), params).all()
        return render_template("vendor_order.html", orders=orders)

    else:
        params = {"user_id":session["account_num"]}
        orders = db.execute(text("select order_items.ordered_item_id, order_items.order_id, order_items.price, order_items.quantity, order_items.item_name, describer.size, describer.color from order_items join items on (order_items.item_id = items.item_id) join describer on (order_items.color_id = describer.color_id) where items.user_id = :user_id and order_items.order_status = 'Pending'"), params).all()
        return render_template("vendor_order.html", orders=orders)
    
@app.route("/vendor/delivery", methods=["GET", "POST"])
@login_required
@vendor_page
def delivery_orders():
    if request.method == "POST":
        params = {"order_id":request.form.get("order_id"), "ordered_item_id":request.form.get("order_item_id")}
        db.execute(text("update order_items set order_status = 'Handed to Delivery Partner' where ordered_item_id = :ordered_item_id"), params)
        db.commit()

        #check all items in order and set overall order status
        check_orders = db.execute(text("select order_status from order_items where order_id = :order_id"), params).all()
        flag = True

        for order in check_orders:
            if order[0] == "Confirmed":
                flag = False
        
        if flag:
            db.execute(text("update orders set order_status = 'Handed to Delivery Partner' where order_id = :order_id"), params)
            db.commit()

       
        params = {"user_id":session["account_num"]}
        orders = db.execute(text("select order_items.ordered_item_id, order_items.order_id, order_items.price, order_items.quantity, order_items.item_name, describer.size, describer.color from order_items join items on (order_items.item_id = items.item_id) join describer on (order_items.color_id = describer.color_id) join orders on (orders.order_id = order_items.order_id) where items.user_id = :user_id and orders.order_status = 'Confirmed' and order_items.order_status = 'Confirmed'"), params).all()
        return render_template("vendor_deliver.html", orders=orders)

    else:
        params = {"user_id":session["account_num"]}
        orders = db.execute(text("select order_items.ordered_item_id, order_items.order_id, order_items.price, order_items.quantity, order_items.item_name, describer.size, describer.color from order_items join items on (order_items.item_id = items.item_id) join describer on (order_items.color_id = describer.color_id) join orders on (orders.order_id = order_items.order_id) where items.user_id = :user_id and orders.order_status = 'Confirmed' and order_items.order_status = 'Confirmed'"), params).all()
        return render_template("vendor_deliver.html", orders=orders)
    
@app.route("/vendor/ship", methods=["GET", "POST"])
@login_required
@vendor_page
def ship_orders():
    if request.method == "POST":
        params = {"order_id":request.form.get("order_id"), "ordered_item_id":request.form.get("order_item_id")}
        db.execute(text("update order_items set order_status = 'Shipped' where ordered_item_id = :ordered_item_id"), params)
        db.commit()

        #check all items in order and set overall order status
        check_orders = db.execute(text("select order_status from order_items where order_id = :order_id"), params).all()
        flag = True

        for order in check_orders:
            if order[0] == "Handed to Delivery Partner":
                flag = False
        
        if flag:
            db.execute(text("update orders set order_status = 'Shipped' where order_id = :order_id"), params)
            db.commit()

       
        params = {"user_id":session["account_num"]}
        orders = db.execute(text("select order_items.ordered_item_id, order_items.order_id, order_items.price, order_items.quantity, order_items.item_name, describer.size, describer.color from order_items join items on (order_items.item_id = items.item_id) join describer on (order_items.color_id = describer.color_id) join orders on (orders.order_id = order_items.order_id) where items.user_id = :user_id and orders.order_status = 'Handed to Delivery Partner' and order_items.order_status = 'Handed to Delivery Partner'"), params).all()
        return render_template("vendor_ship.html", orders=orders)

    else:
        params = {"user_id":session["account_num"]}
        orders = db.execute(text("select order_items.ordered_item_id, order_items.order_id, order_items.price, order_items.quantity, order_items.item_name, describer.size, describer.color from order_items join items on (order_items.item_id = items.item_id) join describer on (order_items.color_id = describer.color_id) join orders on (orders.order_id = order_items.order_id) where items.user_id = :user_id and orders.order_status = 'Handed to Delivery Partner' and order_items.order_status = 'Handed to Delivery Partner'"), params).all()
        return render_template("vendor_ship.html", orders=orders)
    

@app.route("/customer/cart", methods=["GET", "POST"])
@login_required
@customer_page
def cart():
    if request.method == "POST":
        date_ordered = datetime.now()
        address = request.form.get("address")
        if not address:
            return redirect ("/my_account/add")
        params = {"id":session["account_num"]}
        current_info = db.execute(text("select items.item_id, item_name, price, in_stock, cart_id, cart.user_id, quantity, users.username, users_2.username, describer.color_id from items join cart on (items.item_id = cart.item_id) join users on (items.user_id = users.user_id) join users as users_2 on (cart.user_id = users_2.user_id) join describer on (cart.color_id = describer.color_id) where cart.user_id = :id;"), params).all()
        #check all items and return apology if there isnt enough in stock
        for item in current_info:
            if item[3] < item[6]:
                return apology(f"{item[1]} doesn't have enough stock")
        
        # Adds to order and then removes the cart items via their cart_id
        params = {"date_ordered":date_ordered, "id":session["account_num"], "status":"Pending", "address":address}
        db.execute(text("insert into orders (date_ordered, user_id, order_status, address_id) values (:date_ordered, :id, :status, :address)"), params)
        db.commit()
        for i in range(len(current_info)):
            params = {"id":session["account_num"]}
            order_id = db.execute(text("select * from orders where user_id = :id order by order_id desc;"), params).all()
            params = {"id":order_id[0][0], "price":current_info[i][2], "quantity":current_info[i][6], "name":current_info[i][1], "item_id":current_info[i][0], "color_id":current_info[i][9], "status":"Pending"}
            db.execute(text("insert into order_items (order_id, price, quantity, item_name, item_id, color_id, order_status) values (:id, :price, :quantity, :name, :item_id, :color_id, :status)"), params)
            db.commit()
            
            params = {"id":current_info[i][4]}
            db.execute(text("delete from cart where cart_id = :id"), params)
            db.commit()

            params = {"stock":current_info[i][3]-current_info[i][6], "item_id":current_info[i][0]}
            if params["stock"] < 0:
                return apology("Something went wrong")
            db.execute(text("update items set in_stock = :stock where item_id = :item_id"), params)
            db.commit()
        return redirect("/customer/order")
    else:
        params = {"id":session["account_num"]}
        cart_info = db.execute(text("select items.item_id, item_name, price, in_stock, cart_id, cart.user_id, quantity, users.username, users_2.username, describer.color, describer.size from items join cart on (items.item_id = cart.item_id) join users on (items.user_id = users.user_id) join users as users_2 on (cart.user_id = users_2.user_id) join describer on (cart.color_id = describer.color_id) where cart.user_id = :id;"), params).all()
        if (len(cart_info) < 1):
            cart_info = "None"
        addresses = db.execute(text("select * from addresses where user_id = :id and is_active = 'Yes' order by default_address desc"), params).all()
        if len(addresses) == 0:
            addresses = [0]
        return render_template("cart.html", cart_info=cart_info, addresses=addresses)
    
@app.route("/customer/order")
@login_required
@customer_page
def orders():
    params = {"id":session["account_num"]}
    orders = db.execute(text("select * from orders join addresses on (orders.address_id = addresses.address_id) where orders.user_id = :id order by orders.date_ordered desc"), params).all()
    if (len(orders) > 0):
        order_infos = db.execute(text("select * from orders join order_items on (orders.order_id = order_items.order_id) join describer on (order_items.color_id = describer.color_id) where user_id = :id"), params).all()
        totals = []
        for order in orders:
            total = 0
            for order_info in order_infos:
                if order_info[6] == order[0]:
                    total += order_info[7] * order_info[8]
            totals.append(total)
        totals.reverse()         
        return render_template("order.html", orders=orders, order_info=order_infos, totals=totals)
    
    else:
        return render_template("order.html", orders="None", order_info="None", totals="None")
    
@app.route("/cart", methods=["GET", "POST"])
@login_required
@customer_page
def update_cart():
    params = {"user_id":session["account_num"], "item_id":request.form.get("item_id"), "quantity":request.form.get("quant")}
    db.execute(text("update cart set quantity = :quantity where user_id = :user_id and item_id = :item_id"), params)
    db.commit()

    params = {"id":session["account_num"]}
    cart_info = db.execute(text("select items.item_id, item_name, price, in_stock, cart_id, cart.user_id, quantity, users.username, users_2.username, describer.color, describer.size from items join cart on (items.item_id = cart.item_id) join users on (items.user_id = users.user_id) join users as users_2 on (cart.user_id = users_2.user_id) join describer on (cart.color_id = describer.color_id) where cart.user_id = :id;"), params).all()
    if (len(cart_info) < 1):
        cart_info = "None"

    addresses = db.execute(text("select * from addresses where user_id = :id order by default_address desc"), params).all()
    return render_template("cart.html", cart_info=cart_info, addresses=addresses)

@app.route("/cart/delete", methods=["GET", "POST"])
@login_required
def delete_cart():
    params = {"user_id":session["account_num"], "item_id":request.form.get("item_id")}
    db.execute(text("delete from cart where user_id = :user_id and item_id = :item_id"), params)
    db.commit()

    params = {"id":session["account_num"]}
    cart_info = db.execute(text("select items.item_id, item_name, price, in_stock, cart_id, cart.user_id, quantity, users.username, users_2.username, describer.color, describer.size from items join cart on (items.item_id = cart.item_id) join users on (items.user_id = users.user_id) join users as users_2 on (cart.user_id = users_2.user_id) join describer on (cart.color_id = describer.color_id) where cart.user_id = :id;"), params).all()
    if (len(cart_info) < 1):
        cart_info = "None"
    addresses = db.execute(text("select * from addresses where user_id = :id order by default_address desc"), params).all()
    return render_template("cart.html", cart_info=cart_info, addresses=addresses)

@app.route("/customer/complaint_make", methods=["GET", "POST"])
@login_required
@customer_page
def customer_complain():
    warning = ""
    
    if request.method == "POST":
        item = request.form.get("complaint_item")
        reason_type = request.form.get("complaint_reason")
        reason = request.form.get("reason")
        title = request.form.get("title")
        params = {"id":session["account_num"], "item_id":item}
        current_complaints = db.execute(text("select * from complaints where user_id = :id and item_id = :item_id"), params).all()
        if len(current_complaints) < 1:
            params = {"item_id":item, "user_id":session["account_num"], "time_date":datetime.now(), "title":title, "reason_type":reason_type, "reason":reason}
            db.execute(text("insert into complaints (item_id, user_id, time_date, title, reason_type, reason) values (:item_id, :user_id, :time_date, :title, :reason_type, :reason)"), params)
            db.commit()
        else:
            warning = "Complaint already exists!"
        params = {"id":session["account_num"], "status":"Shipped"}
        search_results = db.execute(text("select orders.order_id, user_id, orders.order_status, ordered_item_id, price, quantity, item_name, order_items.item_id, order_items.order_status, describer.color_id, size, color, category from orders join order_items on (orders.order_id = order_items.order_id) join describer on (order_items.color_id = describer.color_id) where user_id = :id and orders.order_status = :status"), params).all()
        return(render_template("complaints_create.html", search_results=search_results, warning=warning))
    
    else:
        params = {"id":session["account_num"], "status":"Shipped"}
        search_results = db.execute(text("select orders.order_id, user_id, orders.order_status, ordered_item_id, price, quantity, item_name, order_items.item_id, order_items.order_status, describer.color_id, size, color, category from orders join order_items on (orders.order_id = order_items.order_id) join describer on (order_items.color_id = describer.color_id) where user_id = :id and orders.order_status = :status"), params).all()
        return(render_template("complaints_create.html", search_results=search_results, warning=warning))
    
@app.route("/customer/complaint_view")
@login_required
@customer_page
def customer_view_complaints():
    params = {"id":session["account_num"]}
    complaints = db.execute(text("select * from complaints where user_id = :id"), params).all()
    return render_template("my_complaints.html", complaints=complaints)

@app.route("/admin/complaint_view", methods=["GET", "POST"])
@login_required
@admin_page
def admin_complaints():
    if request.method == "POST":
        button = request.form.get("button")
        params = {"button":button}
        db.execute(text("update complaints set review_status = :button"), params)
        db.commit()

        params = {"status":"Not yet reviewed"}
        complaints = db.execute(text("select * from complaints where review_status = :status"), params).all()
        return render_template("admin_complaints.html", complaints=complaints)
        
    else:
        params = {"status":"Not yet reviewed"}
        complaints = db.execute(text("select * from complaints where review_status = :status"), params).all()
        return render_template("admin_complaints.html", complaints=complaints)
    
@app.route("/vendor/complaint_view", methods=["GET", "POST"])
@login_required
@vendor_page
def vendor_complaints():
    if request.method == "POST":
        button = request.form.get("button")
        params = {"button":button}
        db.execute(text("update complaints set review_status = :button"), params)
        db.commit()

        params = {"status":"Processing"}
        complaints = db.execute(text("select * from complaints where review_status = :status"), params).all()
        if (len(complaints) < 1):
            warning = "You have no complaints."
        return render_template("vendor_complaints.html", complaints=complaints, warning=warning)
        
    else:
        params = {"status":"Processing"}
        complaints = db.execute(text("select * from complaints where review_status = :status"), params).all()
        if (len(complaints) < 1):
            warning = "You have no complaints."
        return render_template("vendor_complaints.html", complaints=complaints, warning=warning)

@app.route("/chats", methods=["GET", "POST"])
@login_required
def search_chats():
    if request.method == "POST":
        user_searched = request.form.get("user_search")
        params = {"id":session["account_num"]}
        current_rooms = db.execute(text("select * from chat_room where user_one_id = :id or user_two_id = :id"), params).all()
        
        chat_users = []
        for i in current_rooms:
            if (i[1] == session["account_num"]):
                params = {"id1":i[1], "id2":i[2]}
                chat_users.append([i[0], db.execute(text("select username from users where user_id = :id1"), params).all()[0][0], db.execute(text("select username from users where user_id = :id2"), params).all()[0][0]])

            else:
                params = {"id1":i[2], "id2":i[1]}
                chat_users.append([i[0], db.execute(text("select username from users where user_id = :id1"), params).all()[0][0], db.execute(text("select username from users where user_id = :id2"), params).all()[0][0]])

        if (user_searched != ""):
            params = {"user":'%' + user_searched + '%', "id":session["account_num"]}
            searched_users = db.execute(text("select * from users where username like :user and user_id <> :id"), params).all()

        return render_template("current_chats.html", chat_users=chat_users, searched_users=searched_users)
    
    else:
        params = {"id":session["account_num"]}
        current_rooms = db.execute(text("select * from chat_room where user_one_id = :id or user_two_id = :id"), params).all()
        
        chat_users = []
        for i in current_rooms:
            if (i[1] == session["account_num"]):
                params = {"id1":i[1], "id2":i[2]}
                chat_users.append([i[0], db.execute(text("select username from users where user_id = :id1"), params).all()[0][0], db.execute(text("select username from users where user_id = :id2"), params).all()[0][0]])

            else:
                params = {"id1":i[2], "id2":i[1]}
                chat_users.append([i[0], db.execute(text("select username from users where user_id = :id1"), params).all()[0][0], db.execute(text("select username from users where user_id = :id2"), params).all()[0][0]])
        print(chat_users)
        return render_template("current_chats.html", chat_users=chat_users)
    
@app.route("/new_chat", methods=["GET", "POST"])
@login_required
def make_new_chat():
    user_id = request.form.get("selected_user")
    if (user_id != "N/A"):
        params = {"id1":session["account_num"], "id2":user_id, "complaint":"No"}
        db.execute(text("insert into chat_room (user_one_id, user_two_id, is_complaint) values (:id1, :id2, :complaint)"), params)
        db.commit()
        chat_id = db.execute(text("select * from chat_room order by chat_id desc")).all()[0][0]
        return redirect("/chat/" + str(chat_id))
    else:
        return apology("Invalid user selected.")

@app.route("/chat/<chat_id>", methods=["GET", "POST"])
@login_required
def clientside_chat(chat_id):
    if request.method == "POST":
        send_message = request.form.get("message_input")
        params = {"message":send_message, "id":session["account_num"], "time":datetime.now(), "chat_id":chat_id}
        db.execute(text("insert into messages (message, sender_id, time_sent, chat_id) values (:message, :id, :time, :chat_id)"), params)
        db.commit()
        params = {"chat_id":chat_id}
        current_room = db.execute(text("select * from chat_room where chat_id = :chat_id"), params).all()[0]
        messages = db.execute(text("select * from messages where chat_id = :chat_id"), params).all()
        if (current_room[1] != session["account_num"]):
            params = {"id":current_room[1]}
        else:
            params = {"id":current_room[2]}
        other_user = db.execute(text("select username from users where user_id = :id"), params).all()[0][0]
        formatted_messages = []
        for i in messages:
            if i[2] == session["account_num"]:
                formatted_messages.append(["Sent", i[1]])
            else:
                formatted_messages.append(["Recieved", i[1]])
        if (current_room[1] == session["account_num"]) or (current_room[2] == session["account_num"]):
            return render_template("chat.html", formatted_messages=formatted_messages, other_user=other_user, chat_id=chat_id)
        else:
            return render_template("chat.html")
    
    else:
        params = {"chat_id":chat_id}
        current_room = db.execute(text("select * from chat_room where chat_id = :chat_id"), params).all()[0]
        messages = db.execute(text("select * from messages where chat_id = :chat_id"), params).all()
        if (current_room[1] != session["account_num"]):
            params = {"id":current_room[1]}
        else:
            params = {"id":current_room[2]}
        other_user = db.execute(text("select username from users where user_id = :id"), params).all()[0][0]
        formatted_messages = []
        for i in messages:
            if i[2] == session["account_num"]:
                formatted_messages.append(["Sent", i[1]])
            else:
                formatted_messages.append(["Recieved", i[1]])
        if (current_room[1] == session["account_num"]) or (current_room[2] == session["account_num"]):
            return render_template("chat.html", formatted_messages=formatted_messages, other_user=other_user, chat_id=chat_id)
        else:
            return apology("You do not have access to this page.")
        
@app.route("/vendor_image/<image_id>", methods=["GET", "POST"])
@login_required
def image_editor(image_id):
    if request.method == "POST":
        new_link = request.form.get("new_img_link")
        if new_link != "":
            params = {"new_link":new_link, "id":image_id}
            db.execute(text("update images set image_url = :new_link where image_id = :id"), params)
            db.commit()

        params = {"id":image_id}
        images = db.execute(text("select image_id, image_url, items.item_id, users.user_id from images join items on (images.item_id = items.item_id) join users on (items.user_id = users.user_id) where image_id = :id"), params).all()
        return render_template("item_image.html", images=images)
    
    else:
        
        params = {"id":image_id}
        images = db.execute(text("select image_id, image_url, items.item_id, users.user_id from images join items on (images.item_id = items.item_id) join users on (items.user_id = users.user_id) where image_id = :id"), params).all()
        return render_template("item_image.html", images=images)

@app.route("/vendor_del_image/<image_id>")
@login_required
@vendor_page
def remove_image(image_id):
    params = {"id":image_id}
    db.execute(text("delete from images where image_id = :id"), params)
    db.commit()
    return redirect("/vendor/edit")

@app.route("/vendor_new_image/<item_id>")
@login_required
def make_new_image(item_id):
    params = {"url":"None", "id":item_id}
    db.execute(text("insert into images (image_url, item_id) values (:url, :id)"), params)
    db.commit()
    image_id = db.execute(text("select * from images order by image_id desc")).all()[0][0]
    redirect_link = "/vendor_image/" + str(image_id)
    return redirect(redirect_link)

def apology(message, code=400):
    def escape(s):
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


if __name__ == '__main__':
    app.run(debug=True) # Auto restarts cause of debug mode when changes to code are made