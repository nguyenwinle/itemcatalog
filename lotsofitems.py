from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import City, Base, forSale, User

engine = create_engine('sqlite:///users.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Menu for UrbanBurger
city1 = City(user_id=1, name="Sacramento")

session.add(city1)
session.commit()

forSale2 = forSale(user_id=1, name="Famfit Shirt", description="large black made out of cotton",
                     price="$19.50", contact="916-233-6433", category="Fashion", city=city1)

session.add(forSale2)
session.commit()


forSale1 = forSale(user_id=1, name="Solar Power Bank", description="Solar Powered battery bank",
                     price="$10.99", contact="916-233-6433", category="Electronics", city=city1)

session.add(forSale1)
session.commit()

forSale2 = forSale(user_id=1, name="Chicken Burger", description="Juicy grilled chicken patty with tomato mayo and lettuce",
                     price="$5.50", contact="916-233-6433", category="food", city=city1)

session.add(forSale2)
session.commit()

forSale3 = forSale(user_id=1, name="Chocolate Cake", description="fresh baked and served with ice cream",
                     price="$3.99", contact="916-233-6433", category="food", city=city1)

session.add(forSale3)
session.commit()

forSale4 = forSale(user_id=1, name="basketball", description="made for the indoors",
                     price="$7.99", contact="916-233-6433", category="Sports Equipment", city=city1)

session.add(forSale4)
session.commit()


# Menu for Super Stir Fry
city2 = City(user_id=2, name="San Francisco")

session.add(city2)
session.commit()


forSale1 = forSale(user_id=2, name="Chicken Stir Fry", description="With your choice of noodles vegetables and sauces",
                     price="$7.99", contact="916-233-6433", category="food", city=city2)

session.add(forSale1)
session.commit()

forSale2 = forSale(user_id=2, name="Jordan 12", description="Brand New", price="$215", contact="916-233-6433", category="Fashion", city=city2)

session.add(forSale2)
session.commit()

forSale3 = forSale(user_id=2, name="Spicy Tuna Roll", description="Seared rare ahi, avocado, edamame, cucumber with wasabi soy sauce ",
                     price="15", contact="916-233-6433", category="food", city=city2)

session.add(forSale3)
session.commit()


# Menu for Panda Garden
city1 = City(user_id=3, name="San Jose")

session.add(city1)
session.commit()


forSale1 = forSale(user_id=3, name="Pho", description="a Vietnamese noodle soup consisting of broth, linguine-shaped rice noodles called banh pho, a few herbs, and meat.",
                     price="$8.99", contact="916-233-6433", category="Food", city=city1)

session.add(forSale1)
session.commit()

forSale2 = forSale(user_id=3, name="Jordan 12", description="Brand New", price="$215", contact="916-233-6433", category="Fashion", city=city1)

session.add(forSale2)
session.commit()

# Menu for Thyme for that
city1 = City(user_id=4, name="Los Angeles")

session.add(city1)
session.commit()


forSale1 = forSale(user_id=4, name="Solar Power Bank", description="Solar Powered battery bank",
                     price="$10.99", contact="916-233-6433", category="Electronics", city=city1)

session.add(forSale1)
session.commit()

forSale2 = forSale(user_id=4, name="Chicken Burger", description="Juicy grilled chicken patty with tomato mayo and lettuce",
                     price="$5.50", contact="916-233-6433", category="food", city=city1)

session.add(forSale2)
session.commit()




###update using query.filter_by()
##veggieBurgers = session.query(MenuItem)filter_by(name = "Veggie Burger")
##for veggieBurger in veggieBurgers:
##    print veggieBurger.id
##    print veggieBurger.restaurant.name
##    print veggieBurger.price
##    print "\n"
##
##urbanVeggieBurger = session.query(MenuItem).filter_by(id = 8).one()
##print urbanVeggieBurger.price
##
##urbanVeggieBurger.price = '$2.99'
##session.add(urbanVeggieBurger)
##session.commit()
##
##veggieBurgers = session.query(MenuItem)filter_by(name = "Veggie Burger")
##for veggieBurger in veggieBurgers:
##    print veggieBurger.id
##    print veggieBurger.restaurant.name
##    print veggieBurger.price
##    print "\n"
##
##for veggieBurger in veggieBurgers:
##    if veggieBurger.price != '2.99':
##        veggieBurger.price = '2.99'
##        session.add(veggieBurger)
##        session.commit()
##
###to update a employee's address
##rebecca = session.query(Employee).filter_by(name = 'Rebecca Allen').one()
##rebeccaAddress = session.query(Address).filter_by(employee_id = rebecca.id).one()
##rebeccaAddress.street = '7427 Patero Circle'
##rebeccaAddress.zip = '95823'
##session.add(rebeccaAddress)
##session.commit()
##
###Delete mark from employee
##
##mark = session.query(Employee).filter_by(name = 'Mark Gonzalez').one()
##session.delete(mark)
##session.commit()
##session.commit()

print "added items!"

