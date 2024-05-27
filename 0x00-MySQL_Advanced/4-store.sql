-- SQL script that creates a trigger that decreases an item

CREATE TRIGGER decrement
AFTER INSERT
ON orders
FOR EACH ROW
UPDATE items SET quantity = quantity - NEW.number WHERE NAME = NEW.item_name;