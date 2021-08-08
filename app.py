from flask import Flask
from flask_restplus import Resource, Api,fields, reqparse, apidoc, inputs, cors,marshal_with,marshal
import json
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS
import os


app = Flask(__name__)
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument('link',action='append')
parser.add_argument('word',action='append')
CORS(app)




path="https://novelfull.com"
@api.route('/init')
class InitApp(Resource):
    def get(self):

        return "App ok",200
    
@api.route('/inform')
class Novel(Resource):
    
    def get(self):

        return "Hello"

    def post(self):
        args = parser.parse_args()        
        response=args['link']
        obra=[]  
        page = requests.get(response[0])
        soup = BeautifulSoup(page.text, 'html.parser')
        capa="https://novelfull.com"+soup.find(class_="book").img.get("src")
        info=soup.find(class_="info").find_all("div")
        desc=soup.find(class_="desc-text").get_text()
        title=soup.find(class_="title").get_text()
        informat=[]
        #Pegando informações da obra
        for s in info:
            leng=len(s.h3.get_text())
            arg=s.h3.get_text().replace(" ","_")
            informat.append(s.get_text()[leng:])
        
        
        data={"title":title,"cover":capa,"description":desc,"inform":informat}  
        return data,200

        
@api.route('/chapters')
class NovelChap(Resource):
    def post(self):
        args = parser.parse_args()        
        response=args['link']
        obra=[]  
        page = requests.get(response[0])
        soup = BeautifulSoup(page.text, 'html.parser')
        last=soup.find(class_="last").a.get("data-page")
        lp=[]
        ind=0
        for x in range(int(last)+1):
            
            URL = response[0]+"?page="+str(x+1)
            page = requests.get(URL)
            soup = BeautifulSoup(page.text, 'html.parser')
            list_chapter=soup.find(id="list-chapter").find(class_="row").find_all("a")
            for n in list_chapter:
                lp.append({"id":ind,"link":"https://novelfull.com"+n.get('href')})   
                ind+=1 

        data={"chapters":lp}
        return data,200


@api.route('/viewchap')
class View(Resource):
    def post(self):
        args = parser.parse_args()        
        response=args['link']
        page = requests.get(response[0])
        soup = BeautifulSoup(page.text, 'html.parser')
        cap=soup.find_all('p')
        cp=[]
        ind=0
        for nn in cap:
            cp.append({"id":ind,"p":nn.get_text()})
            ind+=1
        return {"title":soup.h3.get_text(),"content":cp},200




@api.route('/search')
class Search(Resource):
    def post(self):
        args = parser.parse_args()        
        response=args['word']
        page = requests.get(path+"/search?keyword="+response[0])
        soup = BeautifulSoup(page.text, 'html.parser')
        lista=soup.find(class_="list list-truyen col-xs-12")
        pp=[]
        one_page=False
        last=0 
        try:
            last=soup.find(class_="last").a.get("data-page")
            one_page=False
        except:
            print("Só uma pagina")
            one_page=True    
        
        def passarLista(lista):
            for ln in lista.find_all("div"):
                
                try :
                    if ln.get("class")[0]=="row":
                    
                        pp.append({"cover":ln.find(class_="col-xs-3").div.img.get("src"),"name":ln.a.get("title"),"link":path+ln.a.get("href")})
                except:
                    print("None")

        if one_page:
            passarLista(lista)
        else:
            for i in range(int(last)+1):
                i+=1
                page = requests.get(path+"/search?keyword="+response[0]+"&page="+str(i))
                soup = BeautifulSoup(page.text, 'html.parser')
                lista=soup.find(class_="list list-truyen col-xs-12")
                
                passarLista(lista)                
        return{"pp":pp,"len":len(pp)}
    


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

