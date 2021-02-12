from api import app
import sys

""" get port number from command line and start api """

if __name__ == '__main__':
    app.run(host='localhost', port=int(sys.argv[1]))