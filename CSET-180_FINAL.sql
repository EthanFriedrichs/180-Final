create database customers_2;
use customers_2;
drop database customers_2;

-- Admin will be hard coded in
drop table users;
create table users (user_id int primary key auto_increment, email varchar(255), username varchar(255), proper_name varchar(255), pass varchar(255), user_type varchar(10));
select * from users;
update users set user_type = "Admin" where user_id = 1;

drop table addresses;
create table addresses (address_id int primary key auto_increment, user_id int, default_address varchar(3), reciever varchar(30), contact_number varchar(15), address_line_1 varchar(255), address_line_2 varchar(255), city varchar(20), state varchar(2), zip varchar(5), is_active varchar(3));
select * from addresses;


drop table items;
create table items (item_id int primary key auto_increment, item_name varchar(255), price float, in_stock int, user_id int, warranty_length int, descript varchar(255),
foreign key (user_id) references users(user_id));
select * from items;
select max(item_id) from items;
insert into items (item_name, price, in_stock, user_id, warranty_length, descript) values 
("Computer", 149.99, 20, 2, 365, "A very fast a reliable computer."),
("T-Shirt", 12.99, 12, 2, 10, "A fluffy shirt made of 100% cotton."),
("Chair", 56.99, 5, 2, 240, "A hardwood chair made of oak wood from the forests on Pandora.");
select * from items where item_name like "%ebay%";


drop tables describer;
create table describer (color_id int primary key auto_increment, size varchar(255), color varchar(255), category varchar(255), item_id int,
foreign key (item_id) references items(item_id));
insert into describer (size, color, category, item_id) values ("N/A", "Brown", "Furniture", 3);
update describer set item_id = 4 where item_id = 1;
select * from describer;
delete from describer where color_id between 7 and 12;
select color_id, size, color, category, describer.item_id from describer join items on (describer.item_id = items.item_id) where user_id = 2;

drop table images;
create table images (image_id int primary key auto_increment, image_url varchar(255), item_id int,
foreign key (item_id) references items(item_id));
select * from images;
insert into images (image_url, item_id) values 
("https://m.media-amazon.com/images/I/51ulmT3YUZL._AC_UY1000_.jpg", 4);

select * from images order by image_id desc;

select image_id, image_url, items.item_id, users.user_id from images join items on (images.item_id = items.item_id) join users on (items.user_id = users.user_id) where users.user_id = 2;

drop table cart;
create table cart (cart_id int primary key auto_increment, user_id int, item_id int, quantity int, color_id int,
foreign key (user_id) references users(user_id),
foreign key (item_id) references items(item_id),
foreign key (color_id) references describer(color_id));
select * from cart;
insert into cart (user_id, item_id, quantity) values (3, 4, 2), (3, 2, 12);
select items.item_id, item_name, price, in_stock, cart_id, cart.user_id, quantity, users.username, users_2.username from items join cart on (items.item_id = cart.item_id) join users on (items.user_id = users.user_id) join users as users_2 on (cart.user_id = users_2.user_id);
-- items.item_id, item_name, price, in_stock, cart_id, cart.user_id, quantity, users.username, users_2.username

drop table complaints;
create table complaints (complaint_id int primary key auto_increment, item_id int, user_id int, time_date date not null, title varchar(50), reason_type varchar(20) not null, reason varchar(255) not null, review_status varchar(50) default "Not yet reviewed",
foreign key (item_id) references items(item_id),
foreign key (user_id) references users(user_id));
select * from complaints;
update complaints set review_status = "Not yet reviewed";

drop table reviews;
create table reviews (review_id int primary key auto_increment, user_id int, item_id int, review_text varchar(255) not null, accept_reject varchar(6), time_review datetime, stars float not null, image blob,
foreign key (user_id) references users(user_id),
foreign key (item_id) references items(item_id));
select * from reviews;

drop table orders;
create table orders (order_id int primary key auto_increment, date_ordered datetime not null, user_id int, order_status varchar(26) not null, address_id int,
foreign key (address_id) references addresses(address_id),
foreign key (user_id) references users(user_id));
select * from orders;
update orders set order_status = "Shipped";

select items.item_id, item_name, price, in_stock, cart_id, cart.user_id, quantity, users.username, users_2.username, describer.color_id from items join cart on (items.item_id = cart.item_id) join users on (items.user_id = users.user_id) join users as users_2 on (cart.user_id = users_2.user_id) join describer on (cart.color_id = describer.color_id) where cart.user_id = 3;


drop table order_items;
create table order_items (ordered_item_id int primary key auto_increment, order_id int, price float, quantity int, item_name varchar(255), item_id int not null, color_id int, order_status varchar(26),
foreign key (order_id) references orders(order_id),
foreign key (item_id) references items(item_id),
foreign key (color_id) references describer(color_id));
select * from order_items;

drop table discounts;
create table discounts (discount_id int primary key auto_increment, discount_expire datetime not null, discount_percent int not null, item_id int,
foreign key (item_id) references items(item_id));
select * from discounts;
insert into discounts (discount_expire, discount_percent, item_id) values (now(), 20, 3);
select discount_id, discount_expire, discount_percent, discounts.item_id from discounts join items on (discounts.item_id = items.item_id) where user_id = 2;
update discounts set discount_expire = "DATE" where item_id = 2;

drop table chat_room;
create table chat_room (chat_id int primary key auto_increment, user_one_id int, user_two_id int, is_complaint varchar(5) not null);
select * from chat_room;
insert into chat_room (user_one_id, user_two_id, is_complaint) values (2, 1, "No"), (3, 2, "No");

select * from users where username like "%ebay%" and username <> "Ebay";

drop table messages;
create table messages (message_id int primary key auto_increment, message varchar(255), sender_id int, time_sent datetime, chat_id int,
foreign key (sender_id) references users(user_id),
foreign key (chat_id) references chat_room(chat_id));
select * from messages;
insert into messages (message, sender_id, time_sent, chat_id) values ("Hello", 2, now(), 1), ("Hello but admin text", 1, now(), 1), ("Hello I am the only message", 2, now(), 2);

select message_id, message, sender_id, time_sent, messages.chat_id, user_one_id, user_two_id, is_complaint from messages join chat_room on (messages.chat_id = chat_room.chat_id);