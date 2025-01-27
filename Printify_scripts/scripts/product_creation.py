import requests
import json
import os
import copy
import sys
from simple_chalk import chalk
import time
import base64
from dotenv import load_dotenv

#dynamic adding to path
from os.path import dirname,abspath
d = dirname(dirname(abspath(__file__)))
sys.path.append(d)

from AWS_scripts.s3_bucket_utility import get_img_url_from_bucket



load_dotenv()
token = os.getenv('PRINTIFY_TOKEN')
shop_id = os.getenv('PRINTIFY_SHOP_ID')

headers = {
    'Authorization': f'Bearer {token}',
    'User-Agent': 'PYTHON'
}
BP_ID = 1313
PP_ID = 41

img_upload_AP = "img-upload-bucket-pr-h47f8f6oj3z7sm858psudmjn3c47nuse1b-s3alias"

generic_payload = {
    "title": None,
    "description": None,
    "blueprint_id": None,
    "print_provider_id": None,
    "variants": [
          {
              "id": None,
              "price": None,
              "is_enabled": True
          }
      ],
      "print_areas": [
        {
          "variant_ids": None,
          "placeholders": None
        }
      ]
  }

#cache path
CACHE_FILE = os.path.join(os.path.dirname(__file__),"img_cache.json")



def load_cache():
    try:
        with open(CACHE_FILE,"r") as file:
            content = file.read()
            if len(content) == 0:
                #file is empty, return empty cache
                return {}
            else:
                cache_data = json.loads(content)
                return cache_data
            
    except FileNotFoundError:
        return {}
    
def save_cache(cache):
    with open(CACHE_FILE, "w") as file:
        json.dump(cache,file,indent=2)


#=======================================================================
def IMG_get_ALL_images_from_library_REQUEST():
    """FUNCTION DETAILS
        
        Purpose:
             gets all images currently in library to make images searchable by user as part of product creation
        
        Accepts: N/A


        Returns:
            images_id_and_names dict - img names mapped to img id's
            to make images searchable by user as part of product creation
            Ex.
                {
                    "fact-roundhouse-kick.png": "6559a537c92cf42ab73c9dae",
                    "fact-morning-coffee-lethal.png": "6559a53475c1ed302bb4aa75",
                    "fact-always-big-spoon.png": "6559986775c1ed302bb4a6ac",
                    "baby-fish.png": "655994c66ced2903364cc823",
                    "Zen as fuck.png": "6540763011f3db397cb81dc1",
                    "ciao mama.png": "6469b50d7c5f5a46e2461ddb",
                    "be patient its coming.png": "6469b4c57c5f5a46e2461dcd",
                }


        Process:
            Makes req to endpoint "https://api.printify.com/v1/uploads.json"
            Initial request puts at first page of media library
            To retrieve images from store library
            Images collected on a page by page basis
            Loop is used to go through all pages of media library
            Each retrieved img obj stored in images_id_and_names dict

        Considerations:
            -if media library is single page
            -if media libary is multiple pages
    """

    # global IMAGE_IDS_AND_NAMES output array
    IMAGE_IDS_AND_NAMES = {}
    """URL response looks like:::
            {
            "current_page": 1,
            "data": [
                {
                "id": "649f03a1e2fd0b711fce62be",
                "file_name": "161.png",
                "height": 3600,
                "width": 3000,
                "size": 2054731,
                "mime_type": "image/png",
                "preview_url": "https://pfy-prod-image-storage.s3.us-east-2.amazonaws.com/12746660/01bbd414-1948-4c26-8de0-738dcee9a87f",
                "upload_time": "2023-06-30 16:32:33"
                },
                {
                "id": "649effede2fd0b711fce6086",
                "file_name": "galaxy cosmic aesthetic (1).png",
                "height": 2000,
                "width": 2000,
                "size": 1252902,
                "mime_type": "image/png",
                "preview_url": "https://pfy-prod-image-storage.s3.us-east-2.amazonaws.com/12746660/3f795edd-4338-4bde-9b64-ae9a7776da94",
                "upload_time": "2023-06-30 16:16:45"
                },
            ....
            }
    
    """
    
    #make initial req to first pg of media library 
    url_media_library_first_pg = f"https://api.printify.com/v1/uploads.json"
    response = requests.get(url_media_library_first_pg,headers=headers)
    uploads_response = response.json() #root response object
    
    
    curr_pg_libary_imgs = uploads_response['data'] #'data' array property of root response
    # print(curr_pg_libary_imgs)
    last_pg_num = uploads_response['last_page'] #for use in while loop as terminating condition
    curr_pg_num = uploads_response['current_page'] #for use in while loop, this is the current page we're visiting
    imgs_collected_count = 0
    # print(last_pg_num)
    # print(curr_pg_num)
    
    # """WHILE LOOP DETAILS
    #         while not at last page of uploads
    #                 on each new page, store all image ids and titles in images dict   
    #                 from current pg, extract next_page_url value from 'next_page_url' property
    #                 append to url
    #                 make request to navigate to next page    
    #                 update curr_page# to be new page# 
    # """
    while curr_pg_num <= last_pg_num:

        #for current page, get all img ids and titles, store K:v pairs in IMAGE_IDS_AND_NAMES{}
        # print(f"::::::EXTRACTING IMAGES AND NAMES FROM UPLOADS PAGE->{curr_pg_num}:::::::")
        for img in curr_pg_libary_imgs:
            # print(img['file_name'])
            IMAGE_IDS_AND_NAMES[img['file_name']] = img['id']
            imgs_collected_count+=1
           
        #check if theres no link to next page preset on current page
        if (uploads_response['next_page_url']) == None:
            print(chalk.green(f"END OF PAGES REACHED: {curr_pg_num} - NO NEXT PAGE"))
            break;
        # from current pg, get next_pg_url
        next_pg_url = uploads_response['next_page_url']
        
        #make req to next_pg
        print(f"::::::MAKING REQEUST TO PAGE->{next_pg_url}::::::")    
        url = f"https://api.printify.com/v1/uploads.json/{next_pg_url}"
        response = requests.get(url,headers=headers)
        uploads_response = response.json()#root response object as json
        # print(uploads_response)
        curr_pg_libary_imgs = uploads_response['data'] #get 'data' array property of root response

        #update curr_page_num with new page val -> curr_pg += 1
        curr_pg_num = uploads_response['current_page']
        # print(f"::::::UPDATE CURRENT Page 'curr_pg_num' -> {curr_pg_num}::::::")
   

    return IMAGE_IDS_AND_NAMES
                                 
    # print(json.dumps(IMAGE_IDS_AND_NAMES,indent=2))
    # # # return IMAGE_IDS_AND_NAMES

# TESTING                                 
# IMAGE_IDS_AND_NAMES = IMG_get_ALL_images_from_library_REQUEST()
# print(json.dumps(IMAGE_IDS_AND_NAMES,indent=2))
# print(IMAGE_IDS_AND_NAMES['Zen as fuck.png'])


#####  IMG SELECTION HELPERS ######


def number_images(IMAGE_IDS_AND_NAMES):
    """
        map each image to a num and store in dict where num is
        key and image name is value 
            Ex. 1: 'mr.fish.png'
    """
    # Number each print_area and return a dictionary
    numbered_print_areas = {}
    for i, print_area_obj in enumerate(IMAGE_IDS_AND_NAMES):
        numbered_print_areas[i] = print_area_obj['position']
    return numbered_print_areas

    

#NOT WORKING - DO NOT USE
def IMG_upload_to_library(images:list):
    """FUNCTION DETAILS

        Purpose:    
            Uploads image(s) to printify media library using post req

        Accepts:
            array of image names 
            Ex.
                ['Zen as fuck.png','Kombucha Queen.png']

        Returns:

        Process:
            using filename of img
            open image in binary mode using context manager
            read its contents
            encode to base64
            attach as payload to req

    """

    
    
    url = f"https://api.printify.com/v1/uploads/images.json"
        
    img_folder_path = ('Printify_scripts\images')
    
    

    for img in images:
        img_path = os.path.join(img_folder_path,img)
        # print(img_path)
        
        with open(img_path,'rb') as imagefile:
            converted_data = base64.b64encode(imagefile.read()).decode('utf-8')
            data={
                "file_name": img,
                "contents": str(converted_data)
            }
           
            print(data["file_name"])
            response = requests.post(url,headers=headers,data=data)
            print(response)
            res = response.json()
            print(res)

#TESTING
# test_images = ['Zen as fuck.png','mr.fish.png']
# IMG_upload_to_library(test_images)


#========================================================================
def IMG_upload_to_library_using_aws_url(images:list):
    """FUNCTION DETAILS

        Purpose:    
            Uploads image(s) to printify media library using post req

        Accepts:
            array of image names 
            Ex.
                ['Zen as fuck.png','Kombucha Queen.png']

        Returns:

        Process:
            using filename of img
            

    """

    url =f"https://api.printify.com/v1/uploads/images.json"
    # 

    for img in images:
        
        # img_url = get_img_url_from_bucket(img)

        data={
           "file_name": "mr.fish.png",
           "url": "https://img-upload-bucket-printify.s3.us-east-1.amazonaws.com/mr.fish.png"
        }
      
        
        response = requests.post(url,headers=headers,data=data)

        print(response.request.body)
        print(response.request.headers['Content-Type'])
        print(response)
        res = response.json()
        print(res)
    


    # url = get_img_url_from_bucket(images[0])
    # response = requests.get(url)
    # print(response)

# TESTING
# test_images = ['Zen as fuck.png','mr.fish.png']
# IMG_upload_to_library_using_aws_url(['mr.fish.png'])

#========================================================================
#checks if cache exists in loaded data
#if found, retrieve image_data from cache

def IMG_get_images_from_cache_or_request():
    

    """FUNCTION DETAILS
        
        Purpose:
            
        
        Accepts: N/A


        Returns:
           


        Process:
            

        Considerations:
            
    """


    cache_data = load_cache() #load in cache data

    #check cache data for "image_cache"
    if "image_cache" in cache_data:
        #cache found, use the data
        IMAGE_IDS_AND_NAMES = cache_data["image_cache"]
    else:
        #cache not found, make the reqeust
        IMAGE_IDS_AND_NAMES = IMG_get_ALL_images_from_library_REQUEST()
        # print(IMAGE_IDS_AND_NAMES)

        #update cache with the new data
        cache_data["image_cache"] = IMAGE_IDS_AND_NAMES
        save_cache(cache_data)

    return IMAGE_IDS_AND_NAMES

# print(json.dumps(IMG_get_images_from_cache_or_request(),indent=2))
IMAGE_IDS_AND_NAMES = IMG_get_images_from_cache_or_request()
# print(IMAGE_IDS_AND_NAMES)
# print(CACHE_FILE)






def IMG_master_img_source_choice():

    """FUNCTION DETAILS

        Purpose:
            This function asks the user how they want to supply images for product creation
            3 options:
                -User can opt to enter specific image filenames
                -User can opt to see numbered image selection and choose from that
                -User can opt to use all images from store media library for product creation
    """

    print(chalk.red("HOW DO YOU WANT TO SUPPLY IMAGES FOR PRODUCT CREATION?"))
    menu_prompt = (
    "1: Enter Specific Image filenames - If you already know the images you want to use\n"
    "2: See numbered selection of all images and choose this way\n"
    "3: Use all the images in the store media library\n"
    "SELECTION: "
    )

    user_input = input(chalk.yellow(menu_prompt))

    

    return user_input
#TESTING
# IMG_master_img_source_choice()
#========================================================================

# # FOR FINDING BY FILENAME AND RETRIEVING IMAGE ID's
def IMG_find_target_images_ids(target_filenames,IMAGE_IDS_AND_NAMES):

    """FUNCTION DETAILS
        
        Purpose:
            retrieve image ids for entered image titles
        
        Accepts: 
            file names to retrieve IDS for
            dict of image names mapped to their ids

        Returns:
            dict of mapped images to their ids
            Ex.
                Found images: [{'filename': 'fact-morning-coffee-lethal.png', 'ID': '6559a53475c1ed302bb4aa75'}, 
                               {'filename': 'ciao mama.png', 'ID': '6469b50d7c5f5a46e2461ddb'}]
        Process:
            
            
        Considerations:

            
    """

    found_images = []
    not_found = []


    for filename in target_filenames:
        
        try:
            if IMAGE_IDS_AND_NAMES[filename]:
                found_img_key = IMAGE_IDS_AND_NAMES[filename]
                found_images.append({
                'filename':filename,
                'ID': found_img_key
            })
        #if img filename not found as key in dict
        except KeyError:
            not_found.append(filename)

    return found_images,not_found

#TESTING
# IMAGE_IDS_AND_NAMES = {
#                     "fact-roundhouse-kick.png": "6559a537c92cf42ab73c9dae",
#                     "fact-morning-coffee-lethal.png": "6559a53475c1ed302bb4aa75",
#                     "fact-always-big-spoon.png": "6559986775c1ed302bb4a6ac",
#                     "baby-fish.png": "655994c66ced2903364cc823",
#                     "Zen as fuck.png": "6540763011f3db397cb81dc1",
#                     "ciao mama.png": "6469b50d7c5f5a46e2461ddb",
#                     "be patient its coming.png": "6469b4c57c5f5a46e2461dcd",
#                     }
# found_images,not_found = IMG_find_target_images_ids(["fact-morning-coffee-lethal.png","ciao mama.png"],IMAGE_IDS_AND_NAMES)
# print(f"Found images: {found_images}")
# print(f"Not Found: {not_found}")


#========================================================================
def PRODUCT_get_product_details(BP_ID,headers):
   
    """FUNCTION get_product_details 
    This function isnt used as part of the creation flow
    It is for verifying you have the correct BP_ID visually

    GET BP ID from target product URL on printify 
        Ex.(https://printify.com/app/products/1092/bagmasters/canvas-shopping-tote)
        The BP ID for the product is 1092
        Its the ONLY number in the url 

    Accepts: BP_ID
    Returns: Product Details

    
    :::::::RESPONSE LOOKS LIKE::::::
        {
            "id": 478,
            "title": "Ceramic Mug 11oz",
            "description": "Warm-up with a nice cuppa out of this customized ceramic coffee mug. Personalize it with cool designs, photos or logos to make that \"aaahhh!\" moment even better. It\u2019s BPA and Lead-free, microwave & dishwasher-safe, and made of white, durable ceramic in 11-ounce size. Thanks to the advanced printing tech, your designs come to life with incredibly vivid colors \u2013 the perfect gift for coffee, tea, and chocolate lovers.<div>.:White ceramic</div><br /><div>.:11 oz (0.33 l)</div><br /><div>.:Rounded corners</div><br /><div>.:C-handle</div><br /><div>.:Lead and BPA-free</div>",
            "brand": "Generic brand",
            "model": "",
            "images": [
                "https://images.printify.com/5e440fbfd897db313b1987d1",
                "https://images.printify.com/6358ee8d99b22ccab005e8a7",
                "https://images.printify.com/633192f1139c053c2d0844d4",
                "https://images.printify.com/5fbe0785264960659838c207",
                "https://images.printify.com/5fbe078d3fac0c0ea83c2633",
                "https://images.printify.com/633192ed5a386e748404baf3",
                "https://images.printify.com/633192f49677c8d7500fd543",
                "https://images.printify.com/615b20688f1fba2fe521504b"
            ]
        }
    """
    url = f"https://api.printify.com/v1/catalog/blueprints/{BP_ID}.json"
    response = requests.get(url,headers=headers)
    target_blueprint_details = response.json()
   
    target_blueprint_details_formatted = json.dumps(target_blueprint_details,indent=2)
    print(target_blueprint_details_formatted)
    return target_blueprint_details

#TESTING
# print(PRODUCT_get_product_details(BP_ID))
#========================================================================
def get_print_provider_ids(BP_ID):
    """ FUNCTION DETAILS:
    Get list of print providers for target product - using product blueprint id
    Accepts:BP_ID
    Returns: list of print providers

    Modification for later: 
        if multiple print provders for BP, return list of all
        let user choose which print providers 
        possbibly return rating of PP and have user choose

    response looks like::::::
       [
            {
                "id": 28,
                "title": "District Photo"
            }
        ]
    """
    print(chalk.red(":::FINDING FIRST PRINT PROVIDER:::"))
    url = f"https://api.printify.com/v1/catalog/blueprints/{BP_ID}/print_providers.json"
    response = requests.get(url,headers=headers)
    print_provider_ids_list = response.json()
    
    #check step
    # print_provider_ids_array = json.dumps(print_provider_ids_list,indent=2)
    # print(print_provider_ids_formatted)

   
    numbered_print_providers={}
    #number each print provider in dict
    for i,pp in enumerate(print_provider_ids_list):
        #K:v pair of current index:value at index
        numbered_print_providers[i]=pp
    
    #Display print provider options to user
    print(chalk.red(f"PRINT PROVIDERS TO CHOOSE FROM:"))
    for num,pp in numbered_print_providers.items():
        print(chalk.green(f"{num}. {pp}"))
        
    user_selected_pp= int(input(chalk.red("SELECT PRINT PROVIDER TO USE (SELECT ONLY ONE OPTION):")))

    user_selected_pp_obj_details = numbered_print_providers[user_selected_pp]
    #use selected pp id to filter the pp_ids_list and retrieve this object 
    #to display to user
    print(f"Print Provider Selected: {user_selected_pp_obj_details}")

    return user_selected_pp_obj_details
    

    #OLD - THIS IS TO RETRIEVE FIRST PRINT PROVIDER - NO CHOICE TO USER
    # #get the first provider in list - just for convenience - can change later
    # first_provider_in_list = (print_provider_ids_list[0])['id']
    # # print("print provider ID:",first_provider_in_list)
    # return first_provider_in_list

#TESTING
# test_bp_id = 12
# user_selected_print_provider = get_print_provider_ids(test_bp_id)
# print(user_selected_print_provider)

#========================================================================
def PRODUCT_get_product_variants_from_print_provider(PP_ID,BP_ID):
   
    """FUNCTION DETAILS: #Get product variants for target item
        From print provider, we want to get the variants offered for the item
        What this means:
            for the selected item we're working with 
            the print provider will have variants, which are different version of the same item
            they could be of differnt color or material
            in another function, we load in the variants and choose which one we want to proceed with 

        ACCEPTS:
            PP_ID, BB_ID

        RETURNS :
            {
                'id': 41, 'title': 'Duplium', 'variants': [
                    {
                    'id': 81758, 'title': '18" x 15"', 
                    'options': {'size': '18" x 15"'}, 
                    'placeholders': 
                        [
                            {'position': 'front', 'height': 3600, 'width': 3000}, 
                            {'position': 'back', 'height': 3600, 'width': 3000}
                        ]
                    }
                ]
            }
"""

    print("FINDING PRODUCT VARIANTS FROM PRINT PROVIDER ")
    """response looks like:::
    {
        "id": 28,
        "title": "District Photo",
        "variants": [
            {
            "id": 65216,
            "title": "11oz",
            "options": {
                "size": "11oz"
            },
            "placeholders": [
                {
                "position": "front",
                "height": 1155,
                "width": 2475
                }
            ]
            }
        ]
    }
    """
    url = f"https://api.printify.com/v1/catalog/blueprints/{BP_ID}/print_providers/{PP_ID}/variants.json"
    response = requests.get(url,headers=headers)
    PP_product_variants = response.json()
    # product_variants_formatted = json.dumps(product_variants,indent=2)
    # print(variants_formatted)
    return PP_product_variants

#TESTING
# variants = PRODUCT_get_product_variants_from_print_provider(PP_ID,BP_ID)
# print(variants)

#========================================================================
def PRODUCT_user_select_product_variants(PP_product_variants):
    """FUNCTION DETAILS
        ACCEPTS:
            product_variants array of objects

        RETURNS:
            array of selected_variant_objects

        
                    "selected_raw_variants": [
                        {
                        "id": 81758,
                        "title": "18\" x 15\"",
                        "options": {
                            "size": "18\" x 15\""
                        },
                        "placeholders": [
                            {
                            "position": "front",
                            "height": 3600,
                            "width": 3000
                            },
                            {
                            "position": "back",
                            "height": 3600,
                            "width": 3000
                            }
                        ]
                        },
                        {
                        "id": 81721,
                        "title": "18\" x 15\"",
                        "options": {
                            "size": "18\" x 15\""
                        },
                        "placeholders": [
                            {
                            "position": "front",
                            "height": 3600,
                            "width": 3000
                            },
                            {
                            "position": "back",
                            "height": 3600,
                            "width": 3000
                            }
                        ]
                        }
                    ]
                    }`
        """
    
    print(chalk.blue("--ENTERING PRODUCT VARIANT SELECTION--"))


    #get variants array from Print provider product variants
    variants_array = PP_product_variants['variants']
    #dictionary for numbering
    numbered_variants_dict = {}
    
    print(f"variants array: {variants_array}")
    #Number each variant and store in dict
    for i,variant in enumerate(variants_array):
        #K:v pair of current index:value at index
        # numbered_variants_dict[i]= variant['id']  - PREV 
        numbered_variants_dict[i]= {
                                    "id":variant['id'], 
                                    "title": variant['title'],
                                    "options": variant['options'],
                                    "placeholders":variant['placeholders']
                                    }


    #Display variant options to user
    print(chalk.red(f"VARIANTS TO CHOOSE FROM:"))
    for num,variant in numbered_variants_dict.items():
        print(chalk.green(f"{num}. {variant}"))
   

    selected_product_variants_as_num = input(chalk.red("SELECT VARIANTS TO USE BY NUMBER, SEPERATE VALUES BY COMMA: "))

    #if user input is multple digits seperated by commas, split at each comma and store all digits in array
    selected_product_variants_as_num = selected_product_variants_as_num.split(',')
    #convert above array to int
    selected_product_variants_as_num_int = [int(x.strip()) for x in selected_product_variants_as_num]

    # print(selected_product_variants_as_num_int)
    
    #for each num selected by user, retrieve variant ids from numbered_variants
    retrieved_selected_variant_ids_by_num = []
    for num in selected_product_variants_as_num_int:
        variant_id = numbered_variants_dict[num]
        retrieved_selected_variant_ids_by_num.append(variant_id)
    
    print(f"Variant(s) Selected:{retrieved_selected_variant_ids_by_num}")
    return retrieved_selected_variant_ids_by_num

    #go through variant objects in variants array, check if an object's id occurs in retrieved_selected_variant_ids_by_num
    #if it does, put object in list to be returned
    # filtered_variants = [var_obj for var_obj in variants_array if var_obj['id'] in retrieved_selected_variant_ids_by_num ]
    # # print(f"Filtered variants array {filtered_variants}")

    # return filtered_variants
    
#TESTING
# PP_variants = PRODUCT_get_product_variants_from_print_provider(42,12)
# print(PRODUCT_user_select_product_variants(PP_variants))
#========================================================================


#####  PRINT AREA SELECTION HELPERS ######

#select_print_area helper 1
def PRINT_AREA_user_select_product_variants(placeholders):
    # Number each print_area and return a dictionary
    numbered_print_areas = {}
    for i, print_area_obj in enumerate(placeholders):
        numbered_print_areas[i] = print_area_obj['position']
    return numbered_print_areas

#select_print_area helper 2
def PRINT_AREA_display_print_areas(numbered_print_areas):
    # Display the numbered print areas to the user
    for num, print_area in numbered_print_areas.items():
        print(f"{num}. {print_area}")

#select_print_area helper 3
def get_user_input(numbered_print_areas):
    # Prompt the user to select print areas
    user_selected_print_area_nums = input("SELECT PRINT AREAS TO USE, SEPARATE VALUES BY COMMA: ").split(",")
    user_selected_print_area_nums_int = [int(x.strip()) for x in user_selected_print_area_nums]
    
    # Validate user input
    for print_area_num in user_selected_print_area_nums_int:
        if not (isinstance(print_area_num, (int, float))) or print_area_num >= len(numbered_print_areas):
            print("!!!YOU ENTERED AN INVALID INPUT FOR PRINT AREA\nINPUT MUST BE NUMERIC AND ONLY FROM AVAILABLE PRINT AREAS SHOWN!!!")
            return None
    
    return [numbered_print_areas[num] for num in user_selected_print_area_nums_int]


def PRINT_AREA_user_select_print_areas_NEW(User_selected_product_variants_raw=[81758]):
    
        """ FUNCTION DETAILS
        ACCEPTS: 
            array of user selected product variants
                [
                        {'id': 18068, 'title': 'Asphalt / S', 'options': {'color': 'Asphalt', 'size': 'S'}, 'placeholders': [{'position': 'back', 'height': 4203, 'width': 3709}, {'position': 'front', 'height': 4203, 'width': 3709}]}, 
                        
                        {'id': 18069, 'title': 'Asphalt / M', 'options': {'color': 'Asphalt', 'size': 'M'}, 'placeholders': [{'position': 'back', 'height': 4658, 'width': 4110}, {'position': 'front', 'height': 4658, 'width': 4110}]}, 
                ]
        RETURNS:
            obj of user selected print areas per variant and the raw user selected variants
                
            selected_print_areas_with_raw_details =
                 {
                    "selected_variants_and_print_areas": [
                        {
                            "id": 81758,
                            "selected_print_areas": ["front","back"]
                        },
                        {
                            "id": 81721,
                            "selected_print_areas": ["front"]
                        }
                    ],
                    "selected_raw_variants": [
                        {
                            "id": 81758,
                            "title": "18\" x 15\"",
                            "options": {
                                "size": "18\" x 15\""
                            },
                            "placeholders": [
                            
                                {"position": "front",
                                    "height": 3600,
                                    "width": 3000},

                                {"position": "back",
                                    "height": 3600,
                                    "width": 3000}
                            ]
                        },
                        {
                            "id": 81721,
                            "title": "18\" x 15\"",
                            "options": {
                                "size": "18\" x 15\""
                            },
                            "placeholders": [
                                { "position": "front",
                                    "height": 3600,
                                    "width": 3000},
                                {"position": "back",
                                    "height": 3600,
                                    "width": 3000}
                            ]        
                        }           
                    ]            
                }


        PROCESS:
            For each variant
            extract placeholders to get print areas
            number the print areas of 
            display to user
            take user input of selected print areas
            append to output array
        
        """
        selected_variants_and_print_areas = []

        """VARIANT OBJ EXAMPLE STRUCTURE
           {
              id': 81721, 'title': '18" x 15"', 
              'options': {'size': '18" x 15"'},     
              'placeholders':       
              [
               {'position': 'front', 'height': 3600, 'width': 3000}, 
               {'position': 'back', 'height': 3600, 'width': 3000}
              ]
          }
        """
        for variant in User_selected_product_variants_raw:
            
            #get placeholders from current variant
            """PLACEHOLDER OBJ EXAMPLE STRUCTURE
            
            'placeholders': [
                                {'position': 'front', 'height': 3600, 'width': 3000}, 
                                {'position': 'back', 'height': 3600, 'width': 3000}
                            ]
            """
            
            curr_variant_placeholders = variant['placeholders']
            print(curr_variant_placeholders)
            

            #number placeholders for selection by user
            #map the index to the value, have the user choose the index
            numbered_print_areas = PRINT_AREA_user_select_product_variants(curr_variant_placeholders)
            
            #display numbered print areas to user for selection
            PRINT_AREA_display_print_areas(numbered_print_areas)

            #get user selected print_areas
            selected_print_areas = get_user_input(numbered_print_areas)

            # print(selected_print_areas)

            selected_variants_and_print_areas.append(
                {"id":variant['id'],
                 "selected_print_areas":selected_print_areas
                })
            
        
        # print(selected_variants_and_print_areas)


        selected_print_areas_with_raw_details = {
            "selected_variants_and_print_areas": selected_variants_and_print_areas,
            "selected_raw_variant_details": User_selected_product_variants_raw
        }

        #formatted test print
        data = json.dumps(selected_print_areas_with_raw_details,indent=2)
        print(data)

        return selected_print_areas_with_raw_details

#TESTING
# print(PRINT_AREA_user_select_print_areas_NEW([81758]))
# multiple_variant_test_data = [{'id': 18068, 'title': 'Asphalt / S', 'options': {'color': 'Asphalt', 'size': 'S'}, 'placeholders': [{'position': 'back', 'height': 4203, 'width': 3709}, {'position': 'front', 'height': 4203, 'width': 3709}]}, {'id': 18069, 'title': 'Asphalt / M', 'options': {'color': 'Asphalt', 'size': 'M'}, 'placeholders': [{'position': 'back', 'height': 4658, 'width': 4110}, {'position': 'front', 'height': 4658, 'width': 4110}]}, {'id': 18070, 'title': 'Asphalt / L', 'options': {'color': 'Asphalt', 'size': 'L'}, 'placeholders': [{'position': 'back', 'height': 5091, 'width': 4500}, {'position': 'front', 'height': 5091, 'width': 4500}]}]
# print(PRINT_AREA_user_select_print_areas_NEW(multiple_variant_test_data))


#========================================================================
def PRODUCT_product_object_fail_safe_capture():

    """FUNCTION DETAILS

    Purpose: In the event the script fails in some way or the request to create the product to printify, the created product objects will be written to a file
    which the user can use instead of having to create all product objects over again
    """
#========================================================================
def PRODUCT_create_product_object_specific_img_selection(BP_ID,PP_ID,variants,images_to_place):


    """ FUNCTION DETAILS
        

        Purpose:
            For SINGLE VARIANT, creates a product object for each img specified
            Ex. 
                For single 11oz mug, create multiple product objects using the images, So create 1 product object for each image

        Accepts: 
            product_variants: BP_ID,PP_ID, product_variants, target images to place
        
        Returns: 
            array of constructed product_objects for single product

        Process:
            Extracts variant_id and placeholders[] from variant
            placeholders[] contains print_area objects (Ex. Position 'front')
            Define 'images[]' prop to be appended into print_area object
                    ('images[]' is prop where we define img objects to be placed on product)
            'images[]' inserted into print_area obj
            take newly modified variant_placeholders and save as new var 'modified_variant_placeholders'
            insert modified_variant_placeholders into generic_payload['placeholders']
    """

    # recieving variant ids and print_areas we want to use{81758: ['front', 'back'], 81721: ['back']}
    selected_variant_ids_and_print_areas = {81758: ['front', 'back'], 81721: ['back']}
    
    #!!!!for variant in selected_variants - we need the rest of the details for it like its placeholders
    #retrieve from PRODUCT_user_select_product_variants
    #key match to retrieve details


    constructed_payload_objects = [] #array to put constructed product_objects to be returned
    constructed_payload_obj = generic_payload.copy()

    for variant in variants:
        variant_id = variant["variants"][0]["id"] #Extract variant id -> Ex 61424
        variant_placeholders_array = variant["variants"][0]["placeholders"][0] #extract variant placeholders[], containing print areas
        print(variant_placeholders_array)

        # #to keep all instances seperate
        # # make fresh copy of placeholders for each img
        # # make fresh copy of print_area_obj for each img
        # for img in images_to_place:
        #     variant_placeholders_array_copy = copy.deepcopy(variant_placeholders_array)
        #     print_area_obj_copy = variant_placeholders_array_copy[0]  #variant_placeholders[0] is first print_area object in placeholders[]
            
        #     """ "placeholders": [
        #                 //!!!PRINT AREA OBJECT!!!
        #                 { 
        #                     "position": "front",
        #                     "height": 1155,
        #                     "width": 2475
        #                 }
        #                 //!!!END PRINT AREA OBJECT!!!
        #             ]
        #     """
        #     print_area_obj_copy['images'] = [{
        #                         "id": img['ID'], 
        #                         "x": 0.5, 
        #                         "y": 0.5, 
        #                         "scale": 1,
        #                         "angle": 0
        #                         }]

        #     #insert modified variant_placeholders into generic_payload['placeholders']
        #     constructed_payload_obj['print_areas'][0]['placeholders'] = variant_placeholders_array_copy
        #     print(constructed_payload_obj)

        #     #Populate remaining generic_payload properties 
        #     # generic_payload['print_areas'][0]['placeholders'] = generic_payload_placeholder
        #     # print(json.dumps(generic_payload_placeholder,indent=2))

        #     constructed_payload_obj['title']= img['filename']
        #     constructed_payload_obj['description']='a beautiful mug'
        #     constructed_payload_obj['blueprint_id'] = BP_ID
        #     constructed_payload_obj['print_provider_id'] = PP_ID
        #     constructed_payload_obj['variants'][0] = {
        #         'id':variant_id,
        #         'price':400,
        #         'is_enabled':True
        #     }
        #     constructed_payload_obj['print_areas'][0]['variant_ids']=[variant_id]

        #     #appending constructed payload object to array
        #     constructed_payload_objects.append(copy.deepcopy(constructed_payload_obj))

    return constructed_payload_objects

#========================================================================
def PRODUCT_create_product_object_specific_img_selection_2(BP_ID,PP_ID,selected_variants,images_to_place):

    print("ENTERING PRODUCT_create_product_object_specific_img_selection_2()")

    """ FUNCTION DETAILS

        Purpose: For MULTIPLE VARIANTS ON SAME PRODUCT, create product objects for each variant using each img

       1 product, 2 variants, 10 images -> 10 images per variant -> 10 product objects for each variant

       so for each variant,
            go through each image
                create product object for each image 

        Accepts:
            BP_ID int
            PP_ID int
            variants obj {selected_variant_print_areas={},selected_raw_variants={}}
            images_to_place [{'filename': 'name val', 'ID': 'id val'}]

        Returns:
          Array of Created product objects for each selected_variant_print_area
        
        Process:


        SELECTED VARIANTS OBJ structure: {
            "selected_variants_and_print_areas": [
                {
                "id": 18564,
                "selected_print_areas": [
                    "back"
                ]
                },
                {
                "id": 18619,
                "selected_print_areas": [
                    "front"
                ]
                }
            ],
            "selected_raw_variant_details": [
                {
                "id": 18564,
                "title": "2XL / Athletic Heather",
                "options": {
                    "size": "2XL",
                    "color": "Athletic Heather"
                },
                "placeholders": [
                    {
                    "position": "back",
                    "height": 4110,
                    "width": 3600
                    },
                    {
                    "position": "front",
                    "height": 4110,
                    "width": 3600
                    }
                ]
                },
                {
                "id": 18619,
                "title": "2XL / Navy",
                "options": {
                    "size": "2XL",
                    "color": "Navy"
                },
                "placeholders": [
                    {
                    "position": "back",
                    "height": 4110,
                    "width": 3600
                    },
                    {
                    "position": "front",
                    "height": 4110,
                    "width": 3600
                    }
                ]
                }
            ]
            }
"""

    constructed_payload_objects = []
    constructed_payload_obj = generic_payload.copy()

    #get obj of selected variants and print areas
    selected_variant_ids_and_print_areas = selected_variants['selected_variants_and_print_areas']
    

    #load raw variant objects into array
    selected_raw_variants = selected_variants['selected_raw_variant_details']


    #go through all selected variants
    for sel_variant in selected_variant_ids_and_print_areas:
        
        #get variant id
        sel_variant_id = sel_variant['id']

        #selected print areas for sel variant
        sel_variant_print_areas = sel_variant['selected_print_areas']

        #retrieve raw_placeholders for current sel variant id
        for raw_v in selected_raw_variants:
            if raw_v['id'] == sel_variant_id:
                raw_v_placeholders = raw_v['placeholders']
                break
            break

        #from raw_v_placeholders, filter out any placeholders that arent in sel_variant_print_areas
        filtered_placeholders = [placeholder_obj for placeholder_obj in raw_v_placeholders if placeholder_obj['position'] in sel_variant_print_areas]
        # print(f"Filtered Placeholders {filtered_placeholders}")
        
        modified_placeholders = copy.deepcopy(filtered_placeholders)
        # Modified placeholders represents placeholders for single variant, so theres only one placeholders[] for variant

        """
        For each img in images_to_place
            for each placeholder in modified_placeholders
               insert images array with img obj
        """

        for img in images_to_place:
            for placeholder in modified_placeholders:
                placeholder['images'] =[{
                    "id":img['ID'],
                    "x":0.5,
                    "y":0.5,
                    "scale":1,
                    "angle":0
                }]
            """
            Modified Placeholders = 
                [{'position': 'front', 'height': 3600, 'width': 3000, 'images': [{'id': '649f03a1e2fd0b711fce62be', 'x': 0.5, 'y': 0.5, 'scale': 0.1, 'angle': 0}]}, 
                {'position': 'back', 'height': 3600, 'width': 3000, 'images': [{'id': '649f03a1e2fd0b711fce62be', 'x': 0.5, 'y': 0.5, 'scale': 0.1, 'angle': 0}]}]
            """
            # print(f"Modified Placeholders- images inserted {modified_placeholders}")

            #populate 'print_area' array of constructed_payload_obj
            constructed_payload_obj["print_areas"] = [{
                    "variant_ids":[sel_variant_id],
                    "placeholders": modified_placeholders
            }]
            # print(f"CON OBJ TEST PRINT: {constructed_payload_obj}")
            # constructed_payload_obj["title"] = f"{img['filename']}"
            constructed_payload_obj["title"] = f"{BP_ID - img['filename']}"
            constructed_payload_obj["description"] = "None"
            constructed_payload_obj["blueprint_id"] = int(BP_ID)
            constructed_payload_obj["print_provider_id"] = int(PP_ID)
            constructed_payload_obj["variants"] = [{
                    "id":sel_variant_id,
                    "price":400,
                    "is_enabled":True
                }]

            # print({json.dumps(constructed_payload_obj,indent=2)})

            #make copy of constructed_payload_obj(for instance isolation) and append to array
            constructed_payload_objects.append(copy.deepcopy(constructed_payload_obj))
            
            
        
        #break for testing function with single variant
    print(f"Constructed Payload objects[]\n {json.dumps(constructed_payload_objects,indent=2)}")    
    return constructed_payload_objects

#TESTING
# multiple_variant_test_data = [
#                             {'id': 18068, 'title': 'Asphalt / S', 'options': {'color': 'Asphalt', 'size': 'S'}, 'placeholders': [{'position': 'back', 'height': 4203, 'width': 3709}, {'position': 'front', 'height': 4203, 'width': 3709}]}, 
                            
#                             {'id': 18069, 'title': 'Asphalt / M', 'options': {'color': 'Asphalt', 'size': 'M'}, 'placeholders': [{'position': 'back', 'height': 4658, 'width': 4110}, {'position': 'front', 'height': 4658, 'width': 4110}]}, 
                            
#                             {'id': 18070, 'title': 'Asphalt / L', 'options': {'color': 'Asphalt', 'size': 'L'}, 'placeholders': [{'position': 'back', 'height': 5091, 'width': 4500}, {'position': 'front', 'height': 5091, 'width': 4500}]}, 
#                         ]
# dummy_select_print_areas = PRINT_AREA_user_select_print_areas_NEW(multiple_variant_test_data)
# img_arr = [{'filename': 'Zen as fuck.png', 'ID': '6540763011f3db397cb81dc1'},{'filename': 'baby-fish.png', 'ID': '655994c66ced2903364cc823'},{'filename':'ciao mama.png','ID':'6469b50d7c5f5a46e2461ddb'}]
# test = PRODUCT_create_product_object_specific_img_selection_2(1092,41,dummy_select_print_areas,img_arr)
# print(json.dumps(test,indent=2))
 #========================================================================           


def PRODUCT_create_product_object_all_images(BP_ID,PP_ID,selected_variants,IMAGE_IDS_AND_NAMES):
    
    """FUNCTION DETAILS

        Purpose: 
        Using ALL images from media library
        For MULTIPLE VARIANTS ON SAME PRODUCT, create product objects for each variant using each img

        1 product, 2 variants, 10 images -> 10 images per variant -> 10 product objects for each variant

        so for each variant,
                go through each image
                    create product object for each image 

        IMAGE_IDS_AND_NAMES has no explicit filename or ID label,
        each key is the literal filename value and each value is the literal image id value
        meaning you cant access anything by 'ID' or 'filename' properties
        

        in order to iterate through each filename, we need to get .items of the IMAGE_IDS_AND_NAMES object
        

        Accepts:
            BP_ID int
            PP_ID int
            variants obj {selected_variant_print_areas={},selected_raw_variants={}}
            IMAGE_IDS_AND_NAMES = {
                            "39.png": "65627c96d602b02cffeb303b",
                            "40.png":"648237174667a70918677a13"
                            }
        Returns:
            Array of Created product objects for each selected_variant_print_area 
        
        Process:


        Considerations:
            if many images and we're building a massive array to hold all the constructed product objects, is there a memory concern here?
    """

    constructed_payload_objects = []
    constructed_payload_obj = generic_payload.copy()

    #get obj of selected variants and print areas
    selected_variant_ids_and_print_areas = selected_variants['selected_variants_and_print_areas']
    

    #load raw variant objects into array
    selected_raw_variants = selected_variants['selected_raw_variant_details']


    #go through all selected variants
    for sel_variant in selected_variant_ids_and_print_areas:
        
        #get variant id
        sel_variant_id = sel_variant['id']

        #selected print areas for sel variant
        sel_variant_print_areas = sel_variant['selected_print_areas']

        #retrieve raw_placeholders for current sel variant id
        for raw_v in selected_raw_variants:
            if raw_v['id'] == sel_variant_id:
                raw_v_placeholders = raw_v['placeholders']
                break
            break

        #from raw_v_placeholders, filter out any placeholders that arent in sel_variant_print_areas
        filtered_placeholders = [placeholder_obj for placeholder_obj in raw_v_placeholders if placeholder_obj['position'] in sel_variant_print_areas]
        # print(f"Filtered Placeholders {filtered_placeholders}")
        
        modified_placeholders = copy.deepcopy(filtered_placeholders)
        # Modified placeholders represents placeholders for single variant, so theres only one placeholders[] for variant

        """
        get img id val from IMAGES_AND_IDS by using img filename as key
            Ex. # print(f"{img_name}---{IMAGES_AND_IDS[img_name]}")

        For each img name in IMAGES_AND_IDS
            for each placeholder in modified_placeholders
               insert images array with img obj
        """

        for img_name in IMAGE_IDS_AND_NAMES.keys():
            print(f"{img_name}---{IMAGE_IDS_AND_NAMES[img_name]}")
            for placeholder in modified_placeholders:
                placeholder['images'] =[{
                    "id":IMAGE_IDS_AND_NAMES[img_name],  #use img_name as key to get img id value
                    "x":0.5,
                    "y":0.5,
                    "scale":1,
                    "angle":0
                }]
            """
            Modified Placeholders = 
                [{'position': 'front', 'height': 3600, 'width': 3000, 'images': [{'id': '649f03a1e2fd0b711fce62be', 'x': 0.5, 'y': 0.5, 'scale': 0.1, 'angle': 0}]}, 
                {'position': 'back', 'height': 3600, 'width': 3000, 'images': [{'id': '649f03a1e2fd0b711fce62be', 'x': 0.5, 'y': 0.5, 'scale': 0.1, 'angle': 0}]}]
            """
            # print(f"Modified Placeholders- images inserted {modified_placeholders}")

            #populate 'print_area' array of constructed_payload_obj
            constructed_payload_obj["print_areas"] = [{
                    "variant_ids":[sel_variant_id],
                    "placeholders": modified_placeholders
            }]
            # print(f"CON OBJ TEST PRINT: {constructed_payload_obj}")
            constructed_payload_obj["title"] = f"{img_name}"
            constructed_payload_obj["description"] = "None"
            constructed_payload_obj["blueprint_id"] = int(BP_ID)
            constructed_payload_obj["print_provider_id"] = int(PP_ID)
            constructed_payload_obj["variants"] = [{
                    "id":sel_variant_id,
                    "price":400,
                    "is_enabled":True
                }]

            # print({json.dumps(constructed_payload_obj,indent=2)})

            #make copy of constructed_payload_obj(for instance isolation) and append to array
            constructed_payload_objects.append(copy.deepcopy(constructed_payload_obj))
            
            
        
        #break for testing function with single variant
    print(f"Constructed Payload objects[]\n {json.dumps(constructed_payload_objects,indent=2)}")    
    return constructed_payload_objects
   

#TESTING
# multiple_variant_test_data = [
#                             {'id': 18068, 'title': 'Asphalt / S', 'options': {'color': 'Asphalt', 'size': 'S'}, 'placeholders': [{'position': 'back', 'height': 4203, 'width': 3709}, {'position': 'front', 'height': 4203, 'width': 3709}]}, 
                            
#                             {'id': 18069, 'title': 'Asphalt / M', 'options': {'color': 'Asphalt', 'size': 'M'}, 'placeholders': [{'position': 'back', 'height': 4658, 'width': 4110}, {'position': 'front', 'height': 4658, 'width': 4110}]}, 
                            
#                             {'id': 18070, 'title': 'Asphalt / L', 'options': {'color': 'Asphalt', 'size': 'L'}, 'placeholders': [{'position': 'back', 'height': 5091, 'width': 4500}, {'position': 'front', 'height': 5091, 'width': 4500}]}, 
#                         ]
# dummy_select_print_areas = PRINT_AREA_user_select_print_areas_NEW(multiple_variant_test_data)
# test = PRODUCT_create_product_object_all_images(1092,41,dummy_select_print_areas,IMAGE_IDS_AND_NAMES)
# print(json.dumps(test,indent=2))


#========================================================================

def PRODUCT_create_and_send_product_request(constructed_product_objects):
    """
    READ ME
    called by each create_product_object function 
    accepts single or array of product objects to make requests for 
    """
    errors = {} # for logging products that failed
    success = {} #for logging successful products
    url = f"https://api.printify.com/v1/shops/{shop_id}/products.json"


    for product_obj in constructed_product_objects:
        payload = product_obj
        print(json.dumps(product_obj,indent=2))
       
        response = requests.post(url,headers=headers,json=payload)
        
        if response.status_code == 200:
            print("Product created successfully!")
            print("Product ID:", response.json().get("id"))
            success[product_obj['title']] = f"SUCCESS - Product ID: {response.json().get('id')}"
        else:
            print("Error:", response.text)
            errors[product_obj['title']] = f"ERROR{response.text}"

    return [success,errors]
    #========================================================================
# get_images_from_library()

def main_driver():
   
   
    BP_ID = input(chalk.red("ENTER THE PRODUCT BLUEPRINT YOU WANT TO CREATE: "))
    print(chalk.green("BLUEPRINT ENTERED: " + BP_ID))

    time.sleep(1)
    #INDIV CALL FOR FIRST PROVIDER
    # PP_ID = get_print_provider_ids(BP_ID)
    # print(chalk.green("PRINT PROVIDER: " + str(PP_ID)))
    # print(PP_ID)
   
   
    PP_ID_OBJ= get_print_provider_ids(BP_ID)
    PP_ID = PP_ID_OBJ['id']
    print(chalk.green("PRINT PROVIDER ID : " + str(PP_ID)))

  
    
    time.sleep(1)
    product_variants = PRODUCT_get_product_variants_from_print_provider(PP_ID,BP_ID)
    print(chalk.green("PRODUCT VARIANTS: \n" + str(product_variants)))

    #user selects product variant from returned list of product_variants
    USER_selected_product_variants = PRODUCT_user_select_product_variants(product_variants)
    print(chalk.green(f"USER_SELECTED_product_variants : {USER_selected_product_variants}"))
    

    #user selects print areas to use from USER_selected_product_variants
    print_areas_selected_by_user = PRINT_AREA_user_select_print_areas_NEW(USER_selected_product_variants)


    #Get all images and their ids from store media library
    IMAGE_IDS_AND_NAMES = IMG_get_ALL_images_from_library_REQUEST()
    # print("MAIN() -> IMAGES_IDS_AND_NAMES", IMAGE_IDS_AND_NAMES)
     
    user_choice = IMG_master_img_source_choice()
    
    match user_choice:
        case "1":
            #IF YOU KMOW THE SPECIFIC IMAGES YOU WANT ALREADY
            #find target_images from user input
            images_to_use = ['40.png','6.png','4.png','37.png']
            target_images_found,not_found = IMG_find_target_images_ids(images_to_use,IMAGE_IDS_AND_NAMES)
            print("FOUND: ",target_images_found)
            print("NOT FOUND: ",not_found)

            print(chalk.cyan("You selected to enter specific images manually"))
            #call function to take in filenames manually
            product_objects = PRODUCT_create_product_object_specific_img_selection_2(BP_ID,PP_ID,print_areas_selected_by_user,target_images_found)
            print("CONSTRUCTED PRODUCT_OBJECT(S): ",json.dumps(product_objects,indent=2))

        case "2":
            print(chalk.cyan("You selected to choose from numbered selection of all library images"))
            #call function to display all images as numbered options
        case "3":
            print(chalk.cyan("You selected to use all library images for product creation"))
            #call function to create product objects using all images
            product_objects = PRODUCT_create_product_object_all_images(BP_ID,PP_ID,print_areas_selected_by_user,IMAGE_IDS_AND_NAMES)
            print("CONSTRUCTED PRODUCT_OBJECT(S): ",json.dumps(product_objects,indent=2))
        case _:
            print(chalk.red("You chose an invalid option"))

  
    


    
    
    
    success,errors =  PRODUCT_create_and_send_product_request(product_objects)
    print(f"Success: {success}")
    print(f"Errors: {errors}")


if __name__ == '__main__':
    main_driver()


"""READ ME - NOTES
:::::::::::::NOTES:::::::::::::::::::

Take BP_ID from url of item
Use BP_ID to get print providers that offer this item 
From list of print providers, choose a print provider ID
Using BP_ID and PP_ID to get varaint properties of the item 
Using variant properties, populate a generic payload object for product creation
send off reqeust with payload in request body

-WHen asked to describe a difficulty you encountered and how you overcame it
    explain how using shallow copy was causing an individual object updates to fail
    and i needed to enforce full instance isolation using copy.deepcopy from pythons copy module
    when trying to create seperate payload objects for a request, I was in circular loop that kept updating the same
    object instance
    so when i was pushing completed payload objects to the array, there were properties that were remaining unchanged
    
    
         -solution to the shallow and deep issue:::
            The issue is that when you make a copy of constructed_payload_obj 
            using constructed_payload_obj.copy(), it creates a shallow copy where nested objects such as 
            variant_placeholders_array and print_area_obj still refer to the same objects in memory.

            To ensure complete isolation between images, you can use the copy module's deepcopy function 
            to create a deep copy of constructed_payload_obj, including all nested objects. 
            This will create separate instances for each image.
            In this updated code, copy.deepcopy() is used to create deep copies of variant_placeholders_array
              and constructed_payload_obj. This ensures that each image has its own independent payload 
              object with separate instances of all nested objects.

    With these changes, the constructed_payload_objects array should contain separate payload objects for each 
    image, with the correct and isolated modifications.



-implemented cache to reduce url requests for images in library to improve performance


-A NOTE ABOUT JSON.DUMPS
    converts everything to string when outputting
    It turns this: {81758: {0: 'front', 1: 'back'}, 81721: {0: 'front', 1: 'back'}}
    Into this: {
                    "81758": {
                        "0": "front",
                        "1": "back"
                    },
                    "81721": {
                        "0": "front",
                        "1": "back"
                    }
                }
    And you will have trouble trying to enforce values as ints


"""