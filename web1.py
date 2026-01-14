from flask import Flask, redirect, url_for #redirect is used to redirect to a different page

app = Flask(__name__) #app is an instance of Flask class

#each page should be given a route (the /sth that represents it in the url) 
@app.route("/") #if route is / or /home it will run the home page or default page
#a page is a function that returns a string
#it can be /pagename or /pagename/ if we want to add a slash at the end of the url

def home():
    return "hello world!<h1>Hello World</h1>" #an inline html code can be used here 

#to make the route dynamic, we use a variable called name in /<>, which is a parameter of the function
#The user function makes whatever route written in the url be passed to the return of the function 
@app.route("/<name>")
def user(name):
    return f"hello {name}"

#to redirect to a different page because the user might not be logged in or the user might not be allowed to access the page
#to do this, we use the redirect function and the url_for function
@app.route("/admin")
def admin():
    return redirect(url_for("user", name="admin")) #if we want it to redirect to user page, but since user in a function with an argument, we need to pass the argument to the redirectfunction







if __name__ == "__main__": #to run the app
    app.run() # starts a server which listens on http://127.0.0.1:5000/ by default
    
