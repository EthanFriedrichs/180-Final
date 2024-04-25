from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from sqlalchemy import create_engine, text
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

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
        return render_template("view.html", products=products, users=users)

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
        color = request.form.getlist("color")
        size = request.form.getlist("size")
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
                    params = {"size":curr_size, "color":curr_color, "id":len(curr_items)}
                    db.execute(text("insert into describer (size, color, item_id) values (:size, :color, :id)"), params)
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
        db.execute(text("delete from items where item_id = :product_id"), params)
        db.commit()

        products = db.execute(text("select * from items where user_id = :user_id order by user_id"), params).all()
        return render_template("vendor_delete.html", products=products)
    
    else:
        params = {"user_id":session["account_num"]}
        products = db.execute(text("select * from items where user_id = :user_id order by user_id"), params).all()
        return render_template("vendor_delete.html", products=products)

# Display all attributes of the item
# Add button to save the edits
# Add the correct amounts of inputs for size and color
    
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

        size = request.form.getlist("new_size")
        color = request.form.getlist("new_color")
        hidden_item_id = request.form.get("item_hidden_id")
        hidden_id = request.form.getlist("hidden_id")
        removals = request.form.getlist("removal")
        print(hidden_id, removals)

        for i in range(len(request.form.getlist("hidden_id"))):
            if (size[i] != "" and request.form.getlist("hidden_id")[i] != "none"):
                params = {"size":size[i], "id":request.form.getlist("hidden_id")[i]}
                db.execute(text("update describer set size = :size where color_id = :id"), params)
                db.commit()
            if (color[i] != ""  and request.form.getlist("hidden_id")[i] != "none"):
                params = {"color":color[i], "id":request.form.getlist("hidden_id")[i]}
                db.execute(text("update describer set color = :color where color_id = :id"), params)
                db.commit()
            if (color[i] != "" and size[i] == "" and request.form.getlist("hidden_id")[i] == "none"):
                params = {"size":"N/A", "color":color[i], "id":hidden_item_id}
                db.execute(text("insert into describer (size, color, item_id) values (:size, :color, :id);"), params)
                db.commit()
            if (color[i] == "" and size[i] != "" and request.form.getlist("hidden_id")[i] == "none"):
                params = {"size":size[i], "color":"N/A", "id":hidden_item_id}
                db.execute(text("insert into describer (size, color, item_id) values (:size, :color, :id);"), params)
                db.commit()
            if (color[i] != "" and size[i] != "" and request.form.getlist("hidden_id")[i] == "none"):
                params = {"size":size[i], "color":color[i], "id":hidden_item_id}
                db.execute(text("insert into describer (size, color, item_id) values (:size, :color, :id);"), params)
                db.commit()

        params = {"account_num":session["account_num"]}
        items = db.execute(text("select * from items where user_id = :account_num"),params).all()
        describers = db.execute(text("select * from describer")).all()
        return render_template("edit_item.html", items=items, describers=describers)
    else:
        params = {"account_num":session["account_num"]}
        items = db.execute(text("select * from items where user_id = :account_num"),params).all()
        describers = db.execute(text("select * from describer")).all()
        return render_template("edit_item.html", items=items, describers=describers)



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