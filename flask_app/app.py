from flask import Flask, render_template,redirect,request,url_for
import os,sys
from forms import IntakeForm
from config import Config,Printify_credentials

from Printify_scripts.scripts import product_creation
# Get the current directory of app.py
current_dir = os.path.dirname(os.path.abspath(__file__))







app = Flask(__name__)

app.config.from_object(Config)
app.config.from_object(Printify_credentials)

#hardcoded for now
BP_ID = 1092
PP_ID = 41

@app.route('/',methods=['GET','POST'])
def home():
    

    #create instance of IntakeForm
    form = IntakeForm()

    if request.method == 'POST':
        # print(form.token.data)
        # print(form.bp_id.data)
        
        # calls to product_creation module methods
        # product_details = product_creation.get_product_details(1092,Printify_credentials.HEADERS)
        
        # #create dropdown showing print provider options
        # # PP_ID = product_creation.get_print_provider_variant_ids(1092)

        # #dropdown - get variants from print provider
        # PP_product_variants = product_creation.get_product_variants_from_print_provider(PP_ID,BP_ID)
        # return PP_product_variants
    
        # #once variants selected, display print areas to user and prompt them to choose
    
    return render_template('index.html',form=form)


# app.route('/show_data',methods=['GET','POST'])
# def show_form_data():

#     form = IntakeForm()
#     print(form.token)
#     print(form.bp_id)
    


if __name__ == '__main__':
    app.run(debug=True)




#     """
#     REF:
#         importing
#          https://stackoverflow.com/questions/12229580/python-importing-a-sub-package-or-sub-module

#     """