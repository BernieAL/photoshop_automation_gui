

import requests
import json
import os




# function called on each product - extracts image array from product
def get_product_img_array_off_product(product):
    product_images_array = product['images']
    print(product_images_array)
    return product_images_array


def get_product_img_urls_off_img_array(product_images_array):
    
    """ 
        Ex output structure built for img_src_urls to be returned
            img_src_urls [
                https://images.printify.com/mockup/6469b5c9e333bc68fe0a92bc/82432/52452/suerte.jpg?camera_label=front
                https://images.printify.com/mockup/6469b5c9e333bc68fe0a92bc/82432/53739/suerte.jpg?camera_label=back
                https://images.printify.com/mockup/6469b5c9e333bc68fe0a92bc/82432/53740/suerte.jpg?camera_label=context-1-front
                https://images.printify.com/mockup/6469b5c9e333bc68fe0a92bc/82432/53741/suerte.jpg?camera_label=context-1-back
                https://images.printify.com/mockup/6469b5c9e333bc68fe0a92bc/82432/53742/suerte.jpg?camera_label=context-2-front
                https://images.printify.com/mockup/6469b5c9e333bc68fe0a92bc/82432/53743/suerte.jpg?camera_label=context-2-back
                https://images.printify.com/mockup/6469b5c9e333bc68fe0a92bc/82432/53745/suerte.jpg?camera_label=detail
            ]
    """
    # temp storage for products src urls
    img_urls = []
    for img in product_images_array:
        img_urls.append(img['src'])
    return img_urls

def retrieve_imgs_and_save_in_dir(img_urls,product_outputFolderDir):
     for url in img_urls:
        response = requests.get(url)
        
        #create filename to store retrieved image under, from basename in url
        img_base_name = os.path.basename(url)
            
        """
        Modifying filename for readability before saving
            turning this: 
                coffee-stay-away.jpg?camera_label=front
            into this:
                coffee-stay-away-camera_label=front.jpg
        """
        
        #get query params off url, this is image context - after the '?'
        #Ex url coffee-stay-away.jpg?camera_label=front
        query_param_location = url.index('?')
        img_context = url[query_param_location+1:]

        #find location of '.jpg' in url, add img context right before this point
        jpg_extension_location = img_base_name.index('.jpg')
        #substring up to .jpg + img_context + '.jpg'
        img_basename_substring_upto_jpg = img_base_name[:jpg_extension_location]
        #print(img_filename_substring_to_jpg)
        
        #updated img_file_name to be 'filename-context.jpg'
        img_file_name = img_basename_substring_upto_jpg +'-'+img_context+'.jpg'
        #print(img_file_filename)
        
        #join created productOutFolderDir with created img_file_name
        #this is desired path we are saving retrieved file to
        output_file_path = os.path.join(product_outputFolderDir,img_file_name)
        
        #save the file in the target dir
        with open(output_file_path, "wb") as f:
            f.write(response.content)

        print(f"Image saved to: {output_file_path}")
        
def make_output_folders(product_list,current_dir):
    # # this makes output folders for all elements
    for product in product_list:
            # #create output folder for specific product to store DL mockup images
            # #using prodict title and ID
            product_id = product['id']
            product_title = product['title']
            # create product folder we will store retrieved images in
            product_outputFolderDir = f"{current_dir}\products\{product_title}-{product_id}"
            # print(product_outputFolderDir)
            try:
                if not os.path.exists(product_outputFolderDir):
                    os.makedirs(product_outputFolderDir)
                # os.umask(0)
                # os.makedirs(product_outputFolderDir,mode=0o777 )
            except:
                 print(f"Error creating dir for: {product_title} - {product_id}  - Probably product name has symbol that cant be used in a dir name 'e.g (*,')'")
                 #write the problem to the log
                 #like if a products name caused an issue creating a directory

    
#!!!!!!!!!!!  DRIVER CODE !!!!!!!!!!!!!!!!!!

import requests
import json
import os

token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzN2Q0YmQzMDM1ZmUxMWU5YTgwM2FiN2VlYjNjY2M5NyIsImp0aSI6IjlhMDVjZWNiYjc4MzcyYzIxMDk2N2UzNWM2MDNkYTMyNzE5YWZjYzc0NTQxOGM0NzRhNWIzNzA2MDFlNjBmZDk0ZTRmN2NjODEwZDZlMTMzIiwiaWF0IjoxNjg0OTQ0OTYzLjMwMTY0MywibmJmIjoxNjg0OTQ0OTYzLjMwMTY0OCwiZXhwIjoxNzE2NTY3MzYzLjI5Mjc1Nywic3ViIjoiMTI3NDY2NjAiLCJzY29wZXMiOlsic2hvcHMubWFuYWdlIiwic2hvcHMucmVhZCIsImNhdGFsb2cucmVhZCIsIm9yZGVycy5yZWFkIiwib3JkZXJzLndyaXRlIiwicHJvZHVjdHMucmVhZCIsInByb2R1Y3RzLndyaXRlIiwid2ViaG9va3MucmVhZCIsIndlYmhvb2tzLndyaXRlIiwidXBsb2Fkcy5yZWFkIiwidXBsb2Fkcy53cml0ZSIsInByaW50X3Byb3ZpZGVycy5yZWFkIl19.Aexvip9HWZgRfm-UCLBWFOw0R1_eF3aU8QMjkK9LaHymKuwosMCfrIwp4YyVqNNXggLZSbbEt2yjl-qarew'


# this makes initial reqeust to get list of products
shop_id = 9157753
url = f"https://api.printify.com/v1/shops/{shop_id}/products.json"

#required headers for printify reqeust
headers = {
    'Authorization': f'Bearer {token}',
    'User-Agent': 'PYTHON'
}

# make request to get all products
response = requests.get(url,headers=headers)
#convert raw response content to json
json_response = response.json()
#get data array which is array of product objects
product_list = json_response['data']
#get current dir
current_dir = os.getcwd()
make_output_folders(product_list,current_dir)

for product in product_list:
    product_id = product['id']
    product_title = product['title']
    
    product_outputFolderDir = f"{current_dir}\products\{product_title}-{product_id}"
    
    product_images_array = get_product_img_array_off_product(product)
    product_img_urls = get_product_img_urls_off_img_array(product_images_array)
    retrieve_imgs_and_save_in_dir(product_img_urls,product_outputFolderDir)    
    




