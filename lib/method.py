class Method:
    role = None
    
    def __init__(self, webob):
        self.webob = webob
        return

    def call(self, user, request, response):
        return True

    def __call__(self, user, request, response):
        return self.call(user, request, response)
