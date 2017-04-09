# Item Catalog

Developed a web application using the Flask framework in Python that provides a list of items within each city as well as building a user login via google and facebook to utilize the add/edit/delete features of the application. The application uses the OAuth protocol for authentication and authorization. 

Also implemented various HTTP methods and how these methods relate to CRUD (create, read, update and delete) operations. 

## Tools and Frameworks

HTML5, CSS, Bootstrap, Vagrant, Flask, SQLAlchemy, Google and Facebook Oauth2 & APIs.

## Project Requirements

Item Catalog includes:
* Home page of Web Application
* About page
* City and City's items page
* Contact page
 (The search bar and message form in the Contact page does not work at this time)

User's features:
* Users can add//edit/delete their own city an items

Login/Logout:
* Authorization and Authentication via Facebook and Google sign in

## Setup

This project requires a virtual machine such as VirtualBox and Vagrant.

Links to VirtualBox and Vagrant:
[Virtual Box](https://www.virtualbox.org/wiki/Downloads)
[Vagrant](https://www.vagrantup.com/)

### run the web application:
1. Clone this repository
2. Open terminal such as Git Bash
3. Change directory to vagrant
4. Run vagrant up (this will start a virtual machine)
5. After vagrant is running, run vagrant ssh to log into the virtual machine
6. Add the final project directory to the terminal
7. Test the project by adding 3 different python files by typing python before each file in the directory. The 3 files are:
database_setup.py, lotsofitems.py, and project.py
8. Access the application by visiting http://localhost:5000 locally on the browser.
