# Flask Stripe MySQL Bootstrapped
Here is an overview of the folders. Everything in this template is contained in the current folder /app.

![System Overview](../demo/complex-system-overview.png)

- **setup_app**: contains the `__init__.py` file that sets up necessary databases and tables, Flask app and folders paths. You can also find the `config.py` file in this folder, where you can configure your various secrets and other stuff, which will propagate throughout the app for easy use. Note that you should probably make separate config files for development, staging and production.
- **templates**: contains only html files, which are used to display the website. This templates folder has some server-generated content with Jinja2, and it loads files from the static folder. Some files from static/partials are used a lot in the templates folder.
- **static**: The static folder contains various libraries, images and code. As the name suggests, this is (mostly) static files, and our app only serves what it needs to serve. The static folder has a lot of files which will not be served. In this folder, you can find the styling of the HTML under static/css. Remember to always minimize the css whenever you are adding to the css files - only the `.min.css` are used (except for pricing.css, for now).
- **services**: This folder/layer is the bread and butter of the backend services of the application. For each fold in the services folder, a main_something.py file is contained and is used to launch each service.
- **action**: This folder/layer is where the business logic happens, and the files are called from the services layer. The action layer is responsible for handling any logic, and it might call other services when needed.
- **data_access**: This folder/layer is strictly for accessing the database and delivering the data as needed, in the right format. No other layer has (and should not have) acccess to the database. 
- **models**: This folder contains object-relational mappings (ORMs), which we use in the `__init__.py` file to generate the tables from. Whenever the data_access layer accesses the database, it does it through a query on these models.