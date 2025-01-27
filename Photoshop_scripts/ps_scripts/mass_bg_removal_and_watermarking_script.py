from photoshop import Session
import os
from datetime import date
import time
# 



"""
GOOGLE DOC SCRIPT USE REFERENCE - https://docs.google.com/document/d/13VEBkfQTLDF91o0L8i09vpORevsfW23if4MB1jko1Zc/edit?usp=sharing


THIS SCRIPT IS FOR BG REMOVAL AND WATERMARKING MASS IMG FOLDERS
YOU SPECIFY THE ROOT DIR - WHICH CONTAINS THE FOLDERS FOR ALL PRODUCTS YOU WANT TO PROCESS
FOR EACH PRODUCT FOLDER, A 'WATERMARKED_OUTPUT' FOLDER IS CREATED INSIDE OF IT - WHICH WILL STORE THE FINAL PROCESSED IMGS FOR THE CURRENT PRODUCT 

Functions INSIDE of context are written as try/catch blocks    
    ALL methods that interact with ps will be nested in context,
    written as try/catch blocks - because you cant access context in functions defined outside of the context
    ALL others like img context checking can be out of context

ISSUE WITH PLC ("place") function
    
    Error can occur if you opened opened a photoshop document and instead are at the home menu thats given when no explicit file is opened
   
    So ofcourse "place" is not available - you cant place an image at home screen
    only in new document

"""








#parent directory for all products to process
ROOT_PRODUCTS_DIR = "C:/Users/balma/Documents/ecommerce/lady cosmica/automation_testing_2"
#filepath for watermark to be used
WATERMARK_FILE_PATH = "C:/Users/balma/Documents/ecommerce/lady cosmica/graphics-watermarks-backgrounds/Lady-Cosmica-Watermark.png"


# TEMPLATE_PATH = "C:/Users/balma/Documents/ecommerce/lady cosmica/background listing templates/base-template.png"
TEMPLATE_PATH = "C:/Users/balma/Documents/ecommerce/lady cosmica/background listing templates/base-template.png"

#Create path for error log directory to store error logs
ERROR_OUTPUT_LOG_DIR = os.path.join(os.getcwd(),"Photoshop_scripts/Error_Log_Dir")
#Column headers for error log csv
ERROR_LOG_COL_HEADERS = 'PRODUCT MOCKUP FILE,TRY-BLOCK-ID,ERROR \n'

Current_date = date.today()
#create error log filename with todays date
CURRENT_DATE_ERROR_LOG_FILENAME = os.path.join(ERROR_OUTPUT_LOG_DIR,f"{Current_date}-Error Log.csv")


def write_error_to_log(mockup_img,blockID,error):
    
    #check if file exists
    if os.path.isfile(CURRENT_DATE_ERROR_LOG_FILENAME):

        #check if first line already has headers written to it
        CURRENT_DATE_ERROR_LOG = open(CURRENT_DATE_ERROR_LOG_FILENAME, 'r')
        first_line = CURRENT_DATE_ERROR_LOG.readline()
        
        #if firstline not col headers, overwrite file contents and make first line col headers
        if first_line != ERROR_LOG_COL_HEADERS:
                CURRENT_DATE_ERROR_LOG = open(CURRENT_DATE_ERROR_LOG_FILENAME, 'w')
                CURRENT_DATE_ERROR_LOG.write(ERROR_LOG_COL_HEADERS)
        
    
        #error gets written to file regardless
        CURRENT_DATE_ERROR_LOG = open(CURRENT_DATE_ERROR_LOG_FILENAME, 'a')
        error_entry = f"{mockup_img},{blockID},{error} \n"
        CURRENT_DATE_ERROR_LOG.write(error_entry)

    #file doesnt exist, make as new
    else:
        #if theres no error log with todays date
        #create it,write headers, then write error
        CURRENT_DATE_ERROR_LOG = open(CURRENT_DATE_ERROR_LOG_FILENAME, 'w')
        #Write columns headers to error log file
        CURRENT_DATE_ERROR_LOG.write(ERROR_LOG_COL_HEADERS)

        #then write the error
        # error_entry = f"{mockup_img},{blockID},{error}"
        error_entry = f"{mockup_img},{blockID},{error}\n "
        CURRENT_DATE_ERROR_LOG.write(error_entry)


def img_presets(context):

    # these are to be hardcoded - to match the specific mockup image set you are working with
    #these are names given by printify 
    ['front','context-1-front','context-2-front']
    
    """
         These vals are determined by user, they determine all attributes of the img on template

        Mockup desired size,dimensions,opacity in PHOTOSHOP first!
        Then record the values and hardcode into corresponding context objects
        RESIZE THE IMAGE TO DESIRED SIZE BEFORE POSITIONING
            Resizing the image impacts the x,y vals
            So do positioning ONLY AFTER youve resized!!!!
        
        position: pass in target x,y pos
        size: pass in size increase relative to original, where 100 is full-size original
        size given by w,h or current img layer.
        110.3125 means 10.3125 increase over original size    
    
        if no change on an axis, do not use 0 to indicate no change - use the original axis value from ps
                on placement, I only changed the x pos, the y pos remained the same
                Instead of putting 0 in for y to indicate 'NO CHANGE'
                I enter the unchanged y value from ps which is 128
                if I used 0, it would be 0-128 which gives me -128 and messes up the y pos


    
    """
    context_1_front={
        # RECORD TARGET POSITION AFTER RESIZE!!
        'position':[612,34], #specify the target x and y, the arithmetic is handled in code later
        'rotate':0, 
        'size': [121.08,121.08], #size is percentage relative to 100%, where 100% is image at original full size
        'opacity':100,
    }
    context_2_front={
        'position':[574,77],
        'rotate':0,
        'size': [124.75,116.625],
        'opacity':100,
    }
    front = {
        'position':[404,-31],
        'rotate':2.28,
        'size': [124.875,125],
        'opacity':100,
    }
    

    if context =='context-1-front':
        return context_1_front
    elif context =='context-2-front':
        return context_2_front
    elif context =='front':
        return front
    # elif context =='back':
    #     return back
    else:
        return "NONE" #if none returned, we dont have a defined preset match for this context
   
# print(img_presets('context-1-front'))



def img_type_eval(img_context):



    """ NOTES
    This method accepts img_context argument 
    extracts image file context from long-format string
    passes image file name to img_presets() and recieves back an object
        containing the matching properties for the given img
    then returns this preset to calling statement where the properties are then destructured and applied
    

    Ex img_context value -> /products/be abstract 1-64685a7374e7edc2bf056007/be-abstract-1-camera_label=context-1-front.jpg"
       img_context_after_label = img_context[img_context.find('label')+6:-4] 
        We find 'label' in img_context string,
        we get the index of where 'label' starts in the img_context string
        from this index, we add 6 to account for 'label='
        create substring from this index to -4 of img_context, to account for '.jpg' 

        1)  input:  /products/be abstract 1-64685a7374e7edc2bf056007/be-abstract-1-camera_label=context-1-front.jpg"
        2)  output: context-1-front

    
    """


    
    # Find occurence of 'label' in img_context, create substring extracting only the filename
    img_context_after_label = img_context[img_context.find('label')+6:-4]
    #Retrieve placement presets object for img context
    result_preset = img_presets(img_context_after_label)
    # print(result_preset.keys())

    return result_preset
    # return f"{position}-{size}-{opacity}"


#helper function used to calculate x,y position deltas for use in translate()
def calculate_pos_deltas(layerbounds,target_x,target_y):
    """ FUNCTION movelayer() Details:
            

            Accepts:
                layerbounds[x,y]
                [target_x,target_y] from context_props[position]
            Returns:
                delta x, delta y
            
            Action:
                Because ps api translate function takes the change in x,y -
                    we retrieve the target x,y from context properties for this img context
                    then calculate the delta of x and y ->
                       
                        #the delta is negative - sliding down an axis 
                            if target < current:
                                delta = current - target
                        
                        #the delta is positive - sliding up on axis
                            if target > current:
                                delta = target - current

    """
    
    # # context_props['position'] contains target x and y where you want image to be
    # target_x,target_y= context_props['position']   

    curr_x = layerbounds[0]
    curr_y = layerbounds[1]
    
    """NOTE
        negative values are OK to use in translate()
    """

    fx = target_x - layer_bounds[0] 
    fy = target_y - layer_bounds[1]
                    

    return fx,fy

def get_watermark_props():

    """ Function Details - get_watermark_props() 
        this function is a getter method for watermark placement properties
        Properties are specified manually - you have to know the properties of how you want it to be placed
                                            You have to manually place the watermark in the desired way ONCE

        Accepts:
            N/a

        Returns:
            watermark_props{} - hardcoded watermark placement props as object

        Action:
            User must open a photoshop document and manually place the watermark at desired visual location
            After this, record the details of the placement - these same details will be used for mass placement on the future img set

            Size - this is given by typing 'Ctrl-t' on target layer  - to enter transform mode
                   Once in transform mode, the user will see X,Y,W,H values for the watermark layer
                    100 means the size of the layer is at 100%
                    -If you wanted to increase the layer size:
                        -record original dimension as img was imported into ps (meaning youve only imported and done nothing else)
                        -perform desired visual adjustments(resize, move etc..)
                        -record new dimensions after adjustments
                        -Quick maths: 
                            new / old * 100 = new size as a percentage of original

            Opacity - no explanation needed
            Position - the values needed for change in position is the difference from where it was to where it is now
                       -To calculate the delta (which is the change), subtract new x,y from prev x,y
                       -If no change on an axis, leave it at 0
                            



    """

    watermark_props = {
        'size':[373.875,373.875],
        'opacity':22,
        'position':[0,245] #MANUALLY CALCUALTE AND SPECIFY THE DELTA YOURSELF
    }

    return watermark_props


# print(movelayer((550.0,210,2150,1810),620,128))

# img_context = "C:/Users/balma/Documents/Programming/Python Projects/PrintifyAutomation/products/be abstract 1-64685a7374e7edc2bf056007/be-abstract-1-camera_label=context-1-front.jpg"
# # find index of 'label' in string, add 6 to that to get passed 'label='
# # get from this new index to -4 from the end to handle '.jpg'
# img_context_after_label = img_context[img_context.find('label')+6:-4]
# # print(img_context_after_label)
# # test = img_type_eval(img_context_after_label)
# # print(test.keys())



# ::::::::::MAIN SECTION - SCRIPT FOR OPENING AND INTERACTING WITH PS  :::::::::: #


with Session(TEMPLATE_PATH,action="open") as ps:

    # ps.app.preferences.rulerUnits = 1
    # app = ps.app
    # jsx = r"""
    #     var doc = app.activeDocument;
    #     var orig_name = doc.name;
    #     alert(orig_name);
    #        """
    # app.doJavaScript(jsx)

    ps.DialogModes.DisplayNoDialogs
    # ps.app.displayDialogs = ps.DialogModes.DisplayErrorDialogs

    # for each subdir in root_products_dir - visit subdir, and visit any nested dirs or files of subdir
    # subdir is iterator var for any immediate child dir of root_products_dir
    # dirs is iterator var for any immediate child dir of current subdir
    # files is iterator var for any immediate child files of current subidir
    """
        root_products_dir
            -product subdir
                -dirs
                -files
    """
    for subdir,dirs,files in os.walk(ROOT_PRODUCTS_DIR):
        
        

        # handling edge-cas - to skip dirs root_products_dir and ./ipynb_checkpoints
        if subdir == ROOT_PRODUCTS_DIR or subdir =='./ipynb_checkpoints':
            continue
        
        # #create output dir for current product subdir - using curr subdir path joined with "script-watermarked-output"
        # #Output dir -> ...{specific_product}/script-watermarked-output/
        watermarked_img_output_dir = os.path.join(subdir,"script-watermarked-output")
        if not(os.path.exists(watermarked_img_output_dir)):
            os.makedirs(watermarked_img_output_dir)

        # for each mockup image file in curr subdir
        for mockup_img in files:
            # print(mockup_img)
            product_img_path = os.path.join(subdir,mockup_img)
            product_img_path = product_img_path.replace("\\", "/")
            # print("IMAGE PATH" + product_img_path)


            #before importing img, if theres presets NOT defined for the img context, skip it
            #we dont want to use this img context because its blank - and havent defined presets for it as a result.
            #pass curr mockup_img file path to eval
            #eval will check for preset, if "none" returned, skip this image and dont import
            #if there is preset defined, retrieve it for later use in IMG CONTEXT EVAL
            context_props = img_type_eval(mockup_img)
            if context_props == "NONE":
                continue


            # Import image section - WORKING 7/17
            try:# this section imports image as layer and places onto document
                #  plc means to "place" an image
                desc = ps.ActionDescriptor
                desc.putPath(ps.app.charIDToTypeID("null"),product_img_path)
                event_id = ps.app.charIDToTypeID("Plc ")  # `Plc` need one space in here.
                ps.app.executeAction(ps.app.charIDToTypeID("Plc "), desc)
                time.sleep(1.5)
                # TEMP TESTING - CHECKING ORIGINAL BOUNDS OF IMPORT
                # removed_jpg_from_filename = mockup_img[:-4]
                # img_layer = ps.active_document.artLayers.getByName(removed_jpg_from_filename)
                # layer_bounds = ps.active_document.activeLayer.bounds
                # print(f"ORIGINAL LAYER BOUNDS BEFORE BG REMOVAL:{layer_bounds}")



              
               
                       
            except:
                print(":::::Error in Import image Section:::::")
                write_error_to_log(mockup_img,"-import img-","-Some problem")
            
            
            # IMG CONTEXT EVAL - front,back,etc - WORKING 7/17
            try:
                strip_jpg_from_filename = mockup_img[:-4]
                img_layer = ps.active_document.artLayers.getByName(strip_jpg_from_filename)
                layer_bounds = ps.active_document.activeLayer.bounds

            
                # print(f"ORIGINAL LAYER BOUNDS AFTER BG REMOVAL :{layer_bounds}")

                # # Adjustment code for img placement/sizing on template
                # # Rec obj back from functions and evaluate dynamically what props the object has
                               
                if context_props['opacity']:
                    val = context_props['opacity']
                    img_layer.opacity = val     

                if context_props['size']:
                    w,h = context_props['size']
                    img_layer.resize(w,h)
                    #if image resized, get update bounds to new img size
                    layer_bounds = ps.active_document.activeLayer.bounds
                    print(f"LAYER BOUNDS CHANGED FROM NEW SIZE:{layer_bounds}")
                    # break;

                if context_props['position']:

                    # targets are desired x,y positions to be moved to
                    target_x,target_y= context_props['position']       
                    
                    # #calulate deltas given current bounds and target bounds
                    delta_x,delta_y = calculate_pos_deltas(layer_bounds,target_x,target_y)

                    # calculate delta x -> (target x - current x) to get change
                    print(f"LAYER BOUNDS BEFORE TRANSLATE:{layer_bounds}")

                    # delta_x = target_x - layer_bounds[0] 
                    # delta_y = target_y - layer_bounds[1]
                    
        
                    img_layer.Translate(delta_x,delta_y)
                    layer_bounds_after_translate = ps.active_document.activeLayer.bounds        
                    print(f"LAYER BOUNDS AFTER TRANSLATE:{layer_bounds_after_translate}")
                    
                
                if context_props['rotate']:
                    val = context_props['rotate']
                    img_layer.rotate(val)
                
            
            except:
                pass
                # print(":::::Error in Eval Img Context::::: ") 
                write_error_to_log(mockup_img,"-IMG CONTEXT EVAL-","-Some problem \n")      
            
            
            #BG REMOVAL OF IMG - WORKING 6/15
            #Edge case - script breaks in PS with closeup img on object detection
            try:
                #run stored custom ps action to remove background
                ps.app.doAction(action="remove_bg")
               
            except Exception as e :

                print(e)
                write_error_to_log(mockup_img,"-BG-REMOVAL-","-Some problem \n")
                
            
            #WATERMARK LOAD IN AND PLACE - load,place,adjust opacity - WORKING 6/12
            try:
                #import watermark img as layer
                desc = ps.ActionDescriptor
                desc.putPath(ps.app.charIDToTypeID("null"),WATERMARK_FILE_PATH)
                event_id = ps.app.charIDToTypeID("Plc ")  # `Plc` need one space in here.
                ps.app.executeAction(ps.app.charIDToTypeID("Plc "), desc)

                watermark_props = get_watermark_props()
                # #get watermark layer by name
                watermark_layer = ps.active_document.artLayers.getByName("Lady-Cosmica-Watermark")
                # print(watermark_layer.name)

                # #resize watermark layer
                w,h = watermark_props['size']
                watermark_layer.resize(w,h)
                
                # # #adjust opacity
                watermark_layer.opacity=watermark_props['opacity']
                
                # #position watermark layer x,y from origin
                #movements are relative to prev/origin position - so its origin + value =  new position
                x_pos,y_pos = watermark_props['position']
                watermark_layer.Translate(x_pos,y_pos)
                
            except Exception as e:
                write_error_to_log(mockup_img,"-WATERMARK-",e)    
                

            
            
            # # SAVE CURRENT DOCUMENT - WORKING 6/15
            try:
                options = ps.JPEGSaveOptions(quality=5)
                jpg = f"{watermarked_img_output_dir}/{mockup_img}-edit"
                jpg_path = jpg.replace("\\", "/")
                print("JPG NAME TO BE USED::" + jpg_path)
                ps.active_document.saveAs(jpg, options, asCopy=True)
                # ps.app.doJavaScript(f'alert("Successfully saved to jpg: {jpg}")')
                print(f"Successfully saved to jpg: {jpg}")
            except:
                 write_error_to_log(mockup_img,"-SAVE-","-Some problem")

            # CLEAN UP AFTER SAVE SECTION - WORKING 6/15
            # remove watermark or resize watermark to original properties?
            # to avoid using last img's properties as origin properties for new img to resize from
            try:
                # get watermark layer and remove 
                watermark_layer = ps.active_document.artLayers.getByName("Lady-Cosmica-Watermark")
                # print(watermark_layer.name)
                watermark_layer.remove()

                #get img layer and remove 
                img_layer = ps.active_document.artLayers.getByName(strip_jpg_from_filename)
                img_layer.remove()

            except:
                 write_error_to_log(mockup_img,"-CLEANUP-","-Some problem")
            
            
            # break For indiv img testing
            # break

        break
















"""
SCRIPTING REFERENCES: 
    https://theiviaxx.github.io/photoshop-docs/Photoshop/


JSX REf
    
    #  app = ps.app
    #  jsx = r"""
    #  var doc = app.activeDocument;
    #  var orig_name = doc.name;
    #  alert(orig_name);
    # """
    # app.doJavaScript(jsx)

"""
#RESIZING- SUPER IMPORTANT!

    width of image given by x2 - x1 which is bounds[2] - bounds[0]
    where bounds is (x1,y1,x2,y2)
   
    Calculating Size:
  (desired size / original size) * 100
  Ex. Manually laying out img to desired size  gives you target w,h in PS
   target = 1765
   original = 1600
   new size relative to prev/orignal = (target / original) * 100 
   1765/1600 = 1.103125 * 100 = 110.3125 


    active_layer = ps.active_document.activeLayer
        current_bounds = active_layer.bounds
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]

        current_width = current_bounds[2] - current_bounds[0]
        current_height = current_bounds[3] - current_bounds[1]
        new_size = width / current_width * 100
        active_layer.resize(new_size, new_size, ps.AnchorPosition.MiddleCenter)
        print(f"current layer {active_layer.name}: {current_bounds}")




POSITIONING/TRANSLATE
    https://stackoverflow.com/questions/12064015/photoshop-scripting-move-an-image-to-position-x-y
    https://community.adobe.com/t5/photoshop-ecosystem-discussions/repositioning-layer-not-working-in-adobe-photoshop-cc-but-works-in-cs6/td-p/7491909
    https://developer.adobe.com/photoshop/uxp/2022/ps_reference/objects/bounds/
    https://community.adobe.com/t5/photoshop-ecosystem-discussions/layer-bounds-is-different-from-bounds-in-photoshop/td-p/10267673
    https://community.adobe.com/t5/photoshop-ecosystem-discussions/how-resize-layer-with-a-big-image-on-size-of-layer-mask/td-p/6196386




Overall process:
    -in root of products dir there is a folder for each product in the form "name-ID"
    -in each product folder are the unedited mockups from printify
    -this script goes through all product folders 
    -creates an output dir to write completed images into
    -loads each image into photoshop as a layer
    -removes the bg
    -uses image context in filename to match to specified placement properties
    -placement properties used to size,rotate,adjust image
    -append "-watermarked" to original filename, to save file under
    -save current document in output dir
    -remove this last added image layer from document ahead of next iteration
        


Note about forward and back slash mismatch:
    The issue you're facing is related to the difference in directory separators used in different 
    operating systems. Windows uses backslashes () as directory separators, 
    while Unix-based systems (including macOS and Linux) use forward slashes (/).

    When you're printing the subdirectories using os.walk, the directory separator used will match
    the one used by the underlying operating system. In your case, you're running the code on a Windows 
    system, so the directory separator used is a backslash (). However, the root directory path you provided seems to use forward slashes (/), which is why you're seeing the mismatched slashes in the output.

    To ensure consistent directory separators in your output, you can use the os.path.join() function, 
    which automatically selects the appropriate separator based on the underlying operating system. 
    Here's an example of how you can modify your code:
                 
                 subdir_path = os.path.join(root_products_dir, subdir)
                 subdir_path = subdir_path.replace("\\", "/")  # Replace backslashes with forward slashes
                 print(subdir_path)


Note about os.walk
    The statement for subdir, dirs, files in os.walk(root_products_dir) is using the os.walk() function to traverse a directory tree rooted at root_products_dir. This function generates the file names in a directory tree by walking through the tree either top-down or bottom-up.
    The os.walk() function returns a generator object that produces a tuple for each directory it visits. The tuple contains three elements: subdir, dirs, and files.
    subdir: It represents the current subdirectory being visited by os.walk(). This variable contains the path to the current directory.
    dirs: It is a list of directories in the current subdirectory. It represents the immediate subdirectories of subdir.
    files: It is a list of files in the current subdirectory. It represents the files contained directly in subdir.
    By using the for subdir, dirs, files in os.walk(root_products_dir) loop, you can iterate over each directory in the directory tree and perform specific actions on the subdirectories and files within them. The loop allows you to process the subdirectories and files in a structured manner, making it easier to perform operations on them.

"""