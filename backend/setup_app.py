import os
from flask import Flask

class SetupApp():
    def run(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
        frontend_dir = os.path.join(base_dir, 'frontend')
        template_dir = os.path.join(frontend_dir, 'templates')
        static_dir = os.path.join(frontend_dir, 'static')

        app = Flask(__name__, 
                    template_folder=template_dir,
                    static_url_path='', 
                    static_folder=static_dir,
                    instance_path=base_dir,
                    instance_relative_config=True)

        app.config.from_pyfile('env_variables.cfg')

        CONN_STR = "mysql+mysqlconnector://{0}:{1}@{2}:{3}" \
            .format(app.config['MYSQL_USER'], app.config['MYSQL_PASSWORD'], app.config['MYSQL_HOST'], app.config['MYSQL_PORT'])
        CONN_STR_W_DB = "mysql+mysqlconnector://{0}:{1}@{2}:{3}/{4}" \
                        .format(app.config['MYSQL_USER'], app.config['MYSQL_PASSWORD'], app.config['MYSQL_HOST'], app.config['MYSQL_PORT'], app.config['MYSQL_DB_NAME'])        
        app.config['CONN_STR'] = CONN_STR
        app.config['CONN_STR_W_DB'] = CONN_STR_W_DB

        return app