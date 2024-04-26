create database customers_2;
use customers_2;

-- Admin will be hard coded in
drop table users;
create table users (user_id int primary key auto_increment, email varchar(255), username varchar(255), proper_name varchar(255), pass varchar(255), user_type varchar(10));
select * from users;
update users set user_type = "Admin" where user_id = 1;

drop table items;
create table items (item_id int primary key auto_increment, item_name varchar(255), price float, in_stock int, user_id int, warranty_length int, descript varchar(255),
foreign key (user_id) references users(user_id));
select * from items;
insert into items (item_name, price, in_stock, user_id, warranty_length, descript) values 
("example item A", 1.50, 20, 2, 365, "Item A"),
("example item B", 3.00, 12, 2, 11, "Item B"),
("example item C", 12.75, 5, 2, 240, "Item C");

drop tables describer;
create table describer (color_id int primary key auto_increment, size varchar(255), color varchar(255), item_id int,
foreign key (item_id) references items(item_id));
insert into describer (size, color, item_id) values ("Other", "N/A", 3);
update describer set item_id = 4 where item_id = 1;
select * from describer;

drop table images;
create table images (image_url varchar(255) primary key);
select * from images;

drop table cart;
create table cart (cart_id int primary key auto_increment, user_id int, item_id int, quantity int,
foreign key (user_id) references users(user_id),
foreign key (item_id) references items(item_id));
select * from cart;
insert into cart (user_id, item_id, quantity) values (3, 4, 2), (3, 2, 12);
select items.item_id, item_name, price, in_stock, cart_id, cart.user_id, quantity, users.username, users_2.username from items join cart on (items.item_id = cart.item_id) join users on (items.user_id = users.user_id) join users as users_2 on (cart.user_id = users_2.user_id);
-- items.item_id, item_name, price, in_stock, cart_id, cart.user_id, quantity, users.username, users_2.username

drop table complaints;
create table complaints (complaint_id int primary key auto_increment, item_id int, time_date date not null, title varchar(20) not null, item_desc varchar(255) not null, demand varchar(14) not null, image_url varchar(255),
foreign key (item_id) references items(item_id),
foreign key (image_url) references images(image_url));
select * from complaints;

drop table reviews;
create table reviews (review_id int primary key auto_increment, user_id int, review_text varchar(255) not null, accept_reject varchar(6), time_review datetime, stars float not null, image blob,
foreign key (user_id) references users(user_id));
select * from reviews;

drop table orders;
create table orders (order_id int primary key auto_increment, date_ordered datetime not null, user_id int, order_status varchar(10) not null,
foreign key (user_id) references users(user_id));
select * from orders;

select orders.order_id, date_ordered, orders.user_id, order_status, ordered_item_id, price, quantity, item_name from orders join order_items on (orders.order_id = order_items.order_id) where user_id = 3;

drop table order_items;
create table order_items (ordered_item_id int primary key auto_increment, order_id int, price float, quantity int, item_name varchar(255),
foreign key (order_id) references orders(order_id));
select * from order_items;

drop table discounts;
create table discounts (discount_id int primary key auto_increment, discount_expire date not null, discount_percent int not null, item_id int,
foreign key (item_id) references items(item_id));
select * from discounts;