import cv2

from tkinter import *
from face_detect import detect_faces
from eyeglass_detector import detect_eyeglasses
from PhotoAgeGender import guessAgeGender
from human_activity_reco import activity_detector

from multiprocessing.pool import ThreadPool

root = Tk()
root.title("Describe Me")
root.geometry("300x180+500+250")

Label(root, text="Enter the file location:", font=("time new roman",10)).place(x=20,y=50)

warning = Label(root, text="",
                font=("time new roman",10), fg='red')
warning.pack()
warning.place(x=20,y=20)

file=Entry(root)

def describe(path):
    y_val = 25
    
    move_down = lambda y: y + 25

    pool = ThreadPool(processes=1)

    #determines whether the person is wearing eyeglasses
    async_result = pool.apply_async(detect_eyeglasses, (path,))
    glasses = async_result.get()
    
    #gets age and gender of person in the image (age first, gender last)
    async_result = pool.apply_async(guessAgeGender, (path,))
    guess = async_result.get()

    #gets the activity the person is performing
    async_result = pool.apply_async(activity_detector, (path,))
    human_activity = async_result.get()

    img = cv2.imread(path)
    if cv2.getWindowProperty("Describe Me", 0) == -1:
        # Close all cv2 windows
        cv2.destroyAllWindows()
    
    cv2.putText(img, "Age: " + str(guess[0]), (10, y_val), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
    y_val = move_down(y_val)
    
    cv2.putText(img, "Gender: " + str(guess[1]), (10, y_val), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
    y_val = move_down(y_val)
    
    if glasses:
        cv2.putText(img, "With Glasses", (10, y_val), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        y_val = move_down(y_val)
        
    if str(guess[1]) == "Male":
        cv2.putText(img, "He is " + str(human_activity), (10, y_val), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
    else:
        cv2.putText(img, "She is "  + str(human_activity), (10, y_val), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)           
    y_val = move_down(y_val)

    warning.configure(text="")
    
    cv2.imshow("Describe Me", img)

def face_check():    
    try:
        path = r""+str(file.get())
        face_count = detect_faces(path)
        if face_count > 1:
            warning.configure(text="* Only one face can be described.")
        else:
            describe(path)
        
    except TypeError:
        warning.configure(text="* Ensure there is a face in the image.")
    except:
        warning.configure(text="* Please use an existing file.")

def close_all():
    cv2.destroyAllWindows()
    root.destroy()

file.place(x=150,y=50)
 
Button(root, text='Describe Me',width=10, command=face_check).place(x=110,y=130)

root.protocol("WM_DELETE_WINDOW", close_all)
mainloop()
