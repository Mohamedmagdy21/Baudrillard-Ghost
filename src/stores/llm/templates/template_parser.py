import os

class TemplateParser():

    def __init__(self,language:str=None,default_langauge:str="en"):
        self.parentpath= os.dirname(os.file_path(os.path.abspath(__file__)))
        self.default_langauge=default_langauge
        self.language=None


    def set_langauage(self,langauge): 
        if not langauge:
            return False

        lang_path=os.path.join(self.parentpath,"lacales",langauge)  

        if not os.path.exists(lang_path):
            self.language=self.default_langauge

        else:
            self.language=langauge  



    def get(self,group:str,key:str,vars:dict={}):

        group_path=os.path.join(self.parentpath,"locales",self.language,f"{group}.py")  
        targeted_langauge=self.language

        if not os.path.exists(group_path):
            group_path= os.path.join(self.parentpath,"locales",self.default_langauge,f"{group}.py")       
            targeted_langauge=self.default_langauge
        if not os.path.exists(group_path):
            return None

        # import group module
        module=__import__(f"stores.llm.templates.locales.{targeted_langauge}.{group}",fromlist=[group])

        if not module:
            return None

        key_attribute=getattr(module,key)   
        return key_attribute.substitute(vars)     

       
        