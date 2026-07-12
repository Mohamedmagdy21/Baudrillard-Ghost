import os
import importlib

class TemplateParser():

    def __init__(self,language:str=None,default_langauge:str="en"):
        self.parent_path = os.path.dirname(os.path.abspath(__file__))
        self.default_langauge=default_langauge
        self.language=default_langauge


    def set_langauage(self,langauge): 
        if not langauge:
            return False

        lang_path=os.path.join(self.parent_path,"locales",langauge)  

        if not os.path.exists(lang_path):
            self.language=self.default_langauge

        else:
            self.language=langauge  



    def get(self,group:str,key:str,vars:dict={}):

        group_path=os.path.join(self.parent_path,"locales",self.language,f"{group}.py")  
        targeted_langauge=self.language

        if not os.path.exists(group_path):
            group_path= os.path.join(self.parent_path,"locales",self.default_langauge,f"{group}.py")       
            targeted_langauge=self.default_langauge
        if not os.path.exists(group_path):
            return None

        # import group module
        module=importlib.import_module(f".locales.{targeted_langauge}.{group}", package=__package__)
        if not module:
            return None

        key_attribute=getattr(module,key)   
        return key_attribute.substitute(vars)     

       
        