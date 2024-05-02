from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from sqlalchemy import create_engine, text
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from datetime import datetime, timedelta

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
        if session.get("isAdmin") == False:
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
        if session.get("isAdmin") == True:
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
        if session.get("isAdmin") == True:
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
conn_str = "mysql://root:ethanpoe125@localhost/customers_2"
engine = create_engine(conn_str) # echo=True tells you if connection is successful or not
db = engine.connect()


@app.route("/")
@login_required
def main_page():
    return render_template("index.html")


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
                    return render_template("index.html")
            return apology("Wrong username and or password", 400)

        
        else:
            # Sign the user in as their current username and make the session "loggedIn"
            session["account_num"] = users[0][0]
            session["user_id"] = users[0][1]
            session["username"] = users[0][2]
            session["loggedIn"] = True
            session["account_type"] = users[0][5]

            return render_template("index.html")
    else:
        return render_template("login.html")

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return render_template("index.html")

@app.route("/my_account", methods=["Get", "POST"])
@login_required
def my_account():
    user_id = session["account_num"]
    params = {"user_id":user_id}
    info = db.execute(text("select * from users where user_id = :user_id"), params).all()
    return render_template("account.html", info=info[0])

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


        params = {"name":name, "description":description, "vendor":vendor}
        users = db.execute(text("select user_id from users where username like :vendor and user_type = 'Vendor'"), params).all()
        final_products = []
        #iterate over users, grab all their products and filter by other values as well
        for user in users:
            params = {"name":name, "description":description, "vendor":vendor, "user_id":user[0]}
            products = db.execute(text("select * from items where user_id = :user_id and item_name like :name and descript like :description order by user_id"), params).all()
            if products:
                for product in products:
                    final_products.append(product)
        users = db.execute(text("select user_id, username from users")).all()
        return render_template("view.html", products=final_products, users=users)
    else:
        products = db.execute(text("select * from items order by user_id")).all()
        users = db.execute(text("select user_id, username from users")).all()
        colors = db.execute(text("select distinct color from describer where color != 'N/A'")).all()
        sizes = db.execute(text("select distinct size from describer where size != 'N/A'")).all()
        categories = db.execute(text("select distinct category from describer where category != 'N/A'")).all()
        return render_template("view.html", products=products, users=users, colors=colors, sizes=sizes, categories=categories)
    

@app.route("/item/<item_id>", methods=["GET", "POST"])
@login_required
@customer_page
def item_page(item_id):
    if request.method == "POST":
        if not request.form.get("isFilter"):

            user_id = session["account_num"]
            params = {"user_id":user_id, "item_id":item_id}
            in_cart = db.execute(text("select * from cart where user_id = :user_id and item_id = :item_id"), params).all()
            if len(in_cart) > 0:
                quanitity = in_cart[0][3] + 1
                params = {"user_id":user_id, "item_id":item_id, "quant":quanitity}
                db.execute(text("update cart set quantity = :quant where user_id = :user_id and item_id = :item_id"), params)
                db.commit()
            else:
                db.execute(text("insert into cart (user_id, item_id, quantity) values (:user_id, :item_id, 1)"), params)
                db.commit()

            products = db.execute(text("select * from items order by user_id")).all()
            users = db.execute(text("select user_id, username from users")).all()
            colors = db.execute(text("select distinct color from describer where color != 'N/A'")).all()
            sizes = db.execute(text("select distinct size from describer where size != 'N/A'")).all()
            categories = db.execute(text("select distinct category from describer where category != 'N/A'")).all()
            return render_template("view.html", products=products, users=users, colors=colors, sizes=sizes, categories=categories)
        else:
            params = {"item_id":item_id}
            product = db.execute(text("select * from items where item_id = :item_id"), params).all()
            users = db.execute(text("select * from users")).all()
            reviews = db.execute(text("select * from reviews join users on (reviews.user_id = users.user_id)")).all()



            if request.form.get("filter") != "N/A":
                params = {"stars":request.form.get("filter")}

                #execute statements where filter is used
                if request.form.get("sort") == "Ratings":
                    reviews = db.execute(text("select * from reviews join users on (reviews.user_id = users.user_id) where reviews.stars = :stars order by stars"), params).all()
                elif request.form.get("sort") == "Time":
                    reviews = db.execute(text("select * from reviews join users on (reviews.user_id = users.user_id) where reviews.stars = :stars order by time_review"), params).all()
                else:
                    reviews = db.execute(text("select * from reviews join users on (reviews.user_id = users.user_id) where reviews.stars = :stars"), params).all()

            else:
                #execute statements where filter is not used
                if request.form.get("sort") == "Ratings":
                    reviews = db.execute(text("select * from reviews join users on (reviews.user_id = users.user_id) order by stars"), params).all()
                elif request.form.get("sort") == "Time":
                    reviews = db.execute(text("select * from reviews join users on (reviews.user_id = users.user_id) order by time_review"), params).all()
            
            return render_template("view_item.html", product=product[0], users=users, reviews=reviews)
        
    else:
        params = {"item_id":item_id}
        product = db.execute(text("select * from items where item_id = :item_id"), params).all()
        reviews = db.execute(text("select * from reviews join users on (reviews.user_id = users.user_id)")).all()
        users = db.execute(text("select * from users")).all()
        return render_template("view_item.html", product=product[0], users=users, reviews=reviews)
    

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
        return apology("TO DO")
    else:
        return apology("TO DO")

@app.route("/admin/edit", methods=["GET", "POST"])
@login_required
@admin_page
def admin_edit():
    if request.method == "POST":
        return apology("TO DO")
    else:
        return apology("TO DO")

@app.route("/admin/delete", methods=["GET", "POST"])
@login_required
@admin_page
def admin_delete():
    if request.method == "POST":
        product = request.form.get("product_id")
        params = {"product_id":product}
        db.execute(text("delete from describer where item_id = :product_id"), params)
        db.execute(text("delete from cart where item_id = :product_id"), params)
        db.execute(text("delete from complaints where item_id = :product_id"), params)
        db.execute(text("delete from reviews where item_id = :product_id"), params)
        db.execute(text("delete from order_items where item_id = :product_id"), params)
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



# vendor routes
@app.route("/vendor", methods=["GET", "POST"])
@login_required
@vendor_page
def vendor():
    params = {"account_num":session["account_num"]}
    products = db.execute(text("select * from items where user_id = :account_num"),params).all()
    return render_template("vendor.html", products=products)

@app.route("/vendor/add", methods=["GET", "POST"])
@login_required
@vendor_page
def add_item():
    if request.method == "POST":
        name = request.form.get("item_name")
        desc = request.form.get("desc")
        price = request.form.get("item_price")
        stock = request.form.get("curr_stock")
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

            curr_items = db.execute(text("select * from items")).all()
            for i in range(len(color)):
                curr_color = color[i]
                curr_size = size[i]
                if curr_color == "":
                    curr_color = "N/A"
                if curr_size == "":
                    curr_size = "N/A"
                if (curr_color != "N/A") and (curr_size != "N/A"):
                    params = {"size":curr_size, "color":curr_color, "category":category, "id":len(curr_items)}
                    db.execute(text("insert into describer (size, color, category, item_id) values (:size, :color, :category, :id)"), params)
                    db.commit()

            if dis_percent != "" and dis_length != "" and dis_time_type != "%":
                current_date = datetime.now()
                if dis_time_type == "minutes":
                    discount_expire = current_date + timedelta(seconds=int(dis_length) * 60)
                    params = {"expire":discount_expire, "percent":dis_percent, "id":len(curr_items)}
                    db.execute(text("insert into discounts (discount_expire, discount_percent, item_id) values (:expire, :percent, :id)"), params)
                    db.commit()
                elif dis_time_type == "hours":
                    discount_expire = current_date + timedelta(hours=int(dis_length))
                    params = {"expire":discount_expire, "percent":dis_percent, "id":len(curr_items)}
                    db.execute(text("insert into discounts (discount_expire, discount_percent, item_id) values (:expire, :percent, :id)"), params)
                    db.commit()
                elif dis_time_type == "days":
                    discount_expire = current_date + timedelta(days=int(dis_length))
                    params = {"expire":discount_expire, "percent":dis_percent, "id":len(curr_items)}
                    db.execute(text("insert into discounts (discount_expire, discount_percent, item_id) values (:expire, :percent, :id)"), params)
                    db.commit()
                elif dis_time_type == "weeks":
                    discount_expire = current_date + timedelta(weeks=int(dis_length))
                    params = {"expire":discount_expire, "percent":dis_percent, "id":len(curr_items)}
                    db.execute(text("insert into discounts (discount_expire, discount_percent, item_id) values (:expire, :percent, :id)"), params)
                    db.commit()
                elif dis_time_type == "months":
                    discount_expire = current_date + timedelta(days=int(dis_length) * 31)
                    params = {"expire":discount_expire, "percent":dis_percent, "id":len(curr_items)}
                    db.execute(text("insert into discounts (discount_expire, discount_percent, item_id) values (:expire, :percent, :id)"), params)
                    db.commit()
                elif dis_time_type == "years":
                    discount_expire = current_date + timedelta(days=int(dis_length) * 365)
                    params = {"expire":discount_expire, "percent":dis_percent, "id":len(curr_items)}
                    db.execute(text("insert into discounts (discount_expire, discount_percent, item_id) values (:expire, :percent, :id)"), params)
                    db.commit()
            else:
                params = {"expire":datetime.now(), "percent":0, "id":len(curr_items)}
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
        db.execute(text("delete from describer where item_id = :product_id"), params)
        db.execute(text("delete from cart where item_id = :product_id"), params)
        db.execute(text("delete from complaints where item_id = :product_id"), params)
        db.execute(text("delete from reviews where item_id = :product_id"), params)
        db.execute(text("delete from order_items where item_id = :product_id"), params)
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

        for i in range(len(request.form.getlist("hidden_id"))):
            # print(request.form.getlist("hidden_id")[i])

            if hidden_id[i] != "none" and removals[i] != "yes":
                
                if new_size[i] != "":
                    if new_color[i] != "":
                        # print("Changing size and color:", new_size[i], "/", new_color[i], "| for color id:", request.form.getlist("hidden_id")[i])
                        params = {"size":new_size[i], "color":new_color[i], "id":request.form.getlist("hidden_id")[i]}
                        db.execute(text("update describer set size = :size, color = :color where color_id = :id"), params)
                        db.commit()
                    else:
                        # print("Changing only size:", new_size[i], "/ N/A | for color id:", request.form.getlist("hidden_id")[i])
                        params = {"size":new_size[i], "id":request.form.getlist("hidden_id")[i]}
                        db.execute(text("update describer set size = :size where color_id = :id"), params)
                        db.commit()
                
                elif new_color[i] != "" and new_size[i] == "":
                    # print("Changing only color: N/A /", new_color[i], "| for color id:", request.form.getlist("hidden_id")[i])
                    params = {"color":new_color[i], "id":request.form.getlist("hidden_id")[i]}
                    db.execute(text("update describer set color = :color where color_id = :id"), params)
                    db.commit()

            elif hidden_id[i] == "none" and removals[i] != "yes":
                
                if new_size[i] != "":
                    if new_color[i] != "":
                        # print("Changing new element size and color:", new_size[i], "/", new_color[i], "| ADD TO DATABASE")
                        params = {"size":new_size[i], "color":new_color[i], "item_id":hidden_item_id}
                        db.execute(text("insert into describer (size, color, item_id) values (:size, :color, :item_id)"), params)
                        db.commit()
                    else:
                        # print("Changing new element size:", new_size[i], "/ N/A | ADD TO DATABASE")
                        params = {"size":new_size[i], "color":"N/A", "item_id":hidden_item_id}
                        db.execute(text("insert into describer (size, color, item_id) values (:size, :color, :item_id)"), params)
                        db.commit()
                
                elif new_color[i] != "" and new_size[i] == "":
                    # print("Changing new element color: N/A /", new_color[i], "| ADD TO DATABASE")
                    params = {"size":"N/A", "color":new_color[i], "item_id":hidden_item_id}
                    db.execute(text("insert into describer (size, color, item_id) values (:size, :color, :item_id)"), params)
                    db.commit()

            elif hidden_id[i] != "none" and removals[i] == "yes":
                # print("Removing color id:", request.form.getlist("hidden_id")[i])
                params = {"id":request.form.getlist("hidden_id")[i]}
                db.execute(text("delete from describer where color_id = :id;"), params)
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
        ct_month = int(current_time.strftime("%m")) # ct refers to current time
        ct_day = int(current_time.strftime("%d"))
        ct_year = int(current_time.strftime("%Y"))
        ct_hour = int(current_time.strftime("%H"))
        ct_minute = int(current_time.strftime("%M"))
        ct_second = int(current_time.strftime("%S"))
        
        for i in range(len(discounts)):
            
            if int(formatted_discounts[i][3]) >= ct_year:
                
                if int(formatted_discounts[i][1]) >= ct_month:

                    if int(formatted_discounts[i][2]) >= ct_day:

                        if int(formatted_discounts[i][4]) >= ct_hour:

                            if int(formatted_discounts[i][5]) >= ct_minute:

                                if int(formatted_discounts[i][6]) >= ct_second:
                                    expires_in.append(["Not expired yet.", formatted_discounts[i][8]])

                                else:
                                    expires_in.append(["Expired " + str(ct_second - int(formatted_discounts[i][6])) + " second(s) ago.",formatted_discounts[i][8]])

                            else:
                                expires_in.append(["Expired " + str(ct_minute - int(formatted_discounts[i][5])) + " minute(s) ago.",formatted_discounts[i][8]])

                        else:
                            expires_in.append(["Expired " + str(ct_hour - int(formatted_discounts[i][4])) + " hour(s) ago.",formatted_discounts[i][8]])

                    else:
                        expires_in.append(["Expired " + str(ct_day - int(formatted_discounts[i][2])) + " day(s) ago.",formatted_discounts[i][8]])
                
                else:
                    expires_in.append(["Expired " + str(ct_month - int(formatted_discounts[i][1])) + " month(s) ago.",formatted_discounts[i][8]])

            else:
                expires_in.append(["Expired " + str(ct_year - int(formatted_discounts[i][3])) + " year(s) ago.",formatted_discounts[i][8]])

        return render_template("edit_item.html", items=items, describers=describers, discounts=discounts)
    
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
        ct_month = int(current_time.strftime("%m")) # ct refers to current time
        ct_day = int(current_time.strftime("%d"))
        ct_year = int(current_time.strftime("%Y"))
        ct_hour = int(current_time.strftime("%H"))
        ct_minute = int(current_time.strftime("%M"))
        ct_second = int(current_time.strftime("%S"))
        
        for i in range(len(discounts)):
            
            if int(formatted_discounts[i][3]) >= ct_year:
                
                if int(formatted_discounts[i][1]) >= ct_month:

                    if int(formatted_discounts[i][2]) >= ct_day:

                        if int(formatted_discounts[i][4]) >= ct_hour:

                            if int(formatted_discounts[i][5]) >= ct_minute:

                                if int(formatted_discounts[i][6]) >= ct_second:
                                    expires_in.append(["Not expired yet.", formatted_discounts[i][8]])

                                else:
                                    expires_in.append(["Expired " + str(ct_second - int(formatted_discounts[i][6])) + " second(s) ago.",formatted_discounts[i][8]])

                            else:
                                expires_in.append(["Expired " + str(ct_minute - int(formatted_discounts[i][5])) + " minute(s) ago.",formatted_discounts[i][8]])

                        else:
                            expires_in.append(["Expired " + str(ct_hour - int(formatted_discounts[i][4])) + " hour(s) ago.",formatted_discounts[i][8]])

                    else:
                        expires_in.append(["Expired " + str(ct_day - int(formatted_discounts[i][2])) + " day(s) ago.",formatted_discounts[i][8]])
                
                else:
                    expires_in.append(["Expired " + str(ct_month - int(formatted_discounts[i][1])) + " month(s) ago.",formatted_discounts[i][8]])

            else:
                expires_in.append(["Expired " + str(ct_year - int(formatted_discounts[i][3])) + " year(s) ago.",formatted_discounts[i][8]])

        return render_template("edit_item.html", items=items, describers=describers, discounts=formatted_discounts, expires_in=expires_in)

@app.route("/customer/cart", methods=["GET", "POST"])
@login_required
def cart():
    if request.method == "POST":
        date_ordered = datetime.now()
        params = {"id":session["account_num"]}
        current_info = db.execute(text("select items.item_id, item_name, price, in_stock, cart_id, cart.user_id, quantity, users.username, users_2.username from items join cart on (items.item_id = cart.item_id) join users on (items.user_id = users.user_id) join users as users_2 on (cart.user_id = users_2.user_id) where cart.user_id = :id;"), params).all()
        # Adds to order and then removes the cart items via their cart_id
        params = {"date_ordered":date_ordered, "id":session["account_num"], "status":"Pending"}
        db.execute(text("insert into orders (date_ordered, user_id, order_status) values (:date_ordered, :id, :status)"), params)
        db.commit()
        for i in range(len(current_info)):
            params = {"id":session["account_num"]}
            order_id = db.execute(text("select * from orders where user_id = :id order by order_id desc;"), params).all()
            params = {"id":order_id[0][0], "price":current_info[i][2], "quantity":current_info[i][6], "name":current_info[i][1], "item_id":current_info[i][0]}
            db.execute(text("insert into order_items (order_id, price, quantity, item_name, item_id) values (:id, :price, :quantity, :name, :item_id)"), params)
            db.commit()
            params = {"id":current_info[i][4]}
            db.execute(text("delete from cart where cart_id = :id"), params)
            db.commit()
        return redirect("/customer/order")
    else:
        params = {"id":session["account_num"]}
        cart_info = db.execute(text("select items.item_id, item_name, price, in_stock, cart_id, cart.user_id, quantity, users.username, users_2.username from items join cart on (items.item_id = cart.item_id) join users on (items.user_id = users.user_id) join users as users_2 on (cart.user_id = users_2.user_id) where cart.user_id = :id;"), params).all()
        if (len(cart_info) < 1):
            cart_info = "None"
        return render_template("cart.html", cart_info=cart_info)
    
@app.route("/customer/order")
@login_required
def orders():
    params = {"id":session["account_num"]}
    orders = db.execute(text("select * from orders where user_id = :id"), params).all()
    if (len(orders) > 0):
        params = {"id":session["account_num"]}
        order_info = db.execute(text("select * from orders join order_items on (orders.order_id = order_items.order_id) where user_id = :id"), params).all()
        totals = []
        for i in range(len(orders)):
            added = 0
            for v in order_info:
                if v[0] == i + 1:
                    added += v[6] * v[7]
            totals.append(added)
                    
        return render_template("order.html", orders=orders, order_info=order_info, totals=totals)
    
    else:
        return render_template("order.html", orders="None", order_info="None", totals="None")

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