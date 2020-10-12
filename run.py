from flaskaap import create_app
from flaskaap.instance.config import Config

app = create_app(Config)

if __name__ == '__main__':
    app.run()