from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from datetime import datetime
from datetime import timedelta
from os import curdir, sep

log = open('log.txt', 'wt', encoding='utf-8')
clients = {}
template = open('template.html', 'r').read()

# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    # Remove any clients who we haven't heard from in 10 seconds
    def pruneClients(self, now):
        expiry = timedelta(seconds=10)
        for k in list(clients):
            if (now - clients[k][1]) > expiry:
                del clients[k]

    # Render a table showing all clients
    def getHits(self):
        result = template.replace("__NUM_CLIENTS__", str(len(clients)))
        rows = ""
        for k, v in clients.items():
            rows += "<tr><td>" + k + "</td><td>" + str(v[0]) + "</td><td>" + v[1].strftime("%d-%m-%y %H:%M:%S") + "</td></tr>"
        result = result.replace("__CLIENT_ROWS__", rows)
        return result

    # GET
    def do_GET(self):    
        message = ""
        tstamp = datetime.now()

        fragments = self.requestline.split()
        parseresult = urlparse(fragments[1])
        if parseresult.path == "/hit":                                        #GET /hit?client=FOOBAR HTTP/1.1
            client = parseresult.query
            if client != "":
                hitcount = 1
                if client in clients:
                    hitcount = clients[client][0]+1
                clients[client] = hitcount, tstamp
                message = "Hello"
                log.write("Hit from " + client + "\n")
                log.flush()
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write(bytes(message, "utf8"))
                return
        else:
            if parseresult.path == "/rows":                                        #GET /rows HTTP/1.1
                self.pruneClients(tstamp)
                rows = ""
                for k, v in clients.items():
                    rows += "<tr><td>" + k + "</td><td>" + str(v[0]) + "</td><td>" + v[1].strftime("%d-%m-%y %H:%M:%S") + "</td></tr>"
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write(bytes(rows, "utf8"))
                return
            else:
                if parseresult.path == "/":                                        #GET / HTTP/1.1
                    print("Serving main page")
                    #self.pruneClients(tstamp)
                    message = self.getHits()
                    self.send_response(200)
                    self.send_header('Content-type','text/html')
                    self.end_headers()
                    self.wfile.write(bytes(message, "utf8"))
                    return
                else:                                                            # just serve up a file
                    print("Serving " + parseresult.path)
                    try:
                        sendReply = False
                        openMethod = 'r'
                        encoding = 'utf8'
                        if parseresult.path.endswith(".html"):
                            mimetype='text/html'
                            sendReply = True
                        if parseresult.path.endswith(".jpg"):
                            mimetype='image/jpg'
                            openMethod = 'rb'
                            encoding = ''
                            sendReply = True
                        if parseresult.path.endswith(".gif"):
                            mimetype='image/gif'
                            openMethod = 'rb'
                            encoding = ''
                            sendReply = True
                        if parseresult.path.endswith(".js"):
                            mimetype='application/javascript'
                            sendReply = True
                        if parseresult.path.endswith(".css"):
                            mimetype='text/css'
                            sendReply = True
    
                        if sendReply == True:
                            #Open the static file requested and send it
                            f = open(curdir + sep + parseresult.path, openMethod) 
                            self.send_response(200)
                            self.send_header('Content-type',mimetype)
                            self.end_headers()
                            buf = f.read()
                            if  encoding != '':
                                self.wfile.write(bytes(buf, encoding))
                            else:
                                self.wfile.write(bytes(buf))
                            f.close()
                        else:
                            print('Can not send file ' + parseresult.path)
                        return
                    except IOError:
                        self.send_error(404,'File Not Found: %s' % self.path)

def run():
    print('starting server...')

    # Server settings
    # Choose port 8080, for port 80, which is normally used for a http server, you need root access
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever()

run()
