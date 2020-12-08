import tkinter as tk
from tkinter import messagebox
import numpy as np
import cv2
from PIL import Image
import os
import sys
import pickle
import cx_Oracle
import shutil
import pyttsx3
import PyInstaller

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        
engine=pyttsx3.init()
engine.setProperty('voice','HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0')
engine.setProperty('rate',170)

d_set=set()



def takeimages():
    name=e1.get()
    sno=int(e2.get())
    branch=e3.get()
    c=count=0
    #cur.execute("alter table db add column attendance INTEGER")
    cur.execute("insert into attendance(sno,name,branch,attendance,percent) values({},'{}','{}',{},{})".format(sno,name,branch,count,c))
    connection.commit()
    #cur.execute("select * from db")
    #for row in cur.fetchall():
     #   print(row)
    #label=tk.Label(root,text=name)
    #label.place(x=600,y=600)
    dirname='F:\python\project\images\{}'.format(sno)
    label=os.path.basename(dirname)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
        print("directory",dirname,"created")
        cap=cv2.VideoCapture(0)
        i=0
        while(True):
            ret, frame=cap.read()
            gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            faces=face_cascade.detectMultiScale(frame,1.5,5)
            for(x,y,w,h) in faces:
                roi_gray=gray[y:y+h,x:x+w]
                roi_color=frame[y:y+h,x:x+w]
                cv2.imwrite("{}\{}_{}.png".format(dirname,label,i),roi_color)
                cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
                cv2.imshow("IMAGE",frame)
                i+=1
            if cv2.waitKey(1) & 0xFF == ord('s'):
                break
        cap.release()
        cv2.destroyAllWindows();
        return 
    else:
        print("error")
    
def train_images():
    recognizer=cv2.face.LBPHFaceRecognizer_create()
    current_id=0
    label_ids={}
    x_train=[]
    y_labels=[]
    BASE_DIR=os.path.dirname(os.path.abspath(__file__))
    img_dir=os.path.join(BASE_DIR,"images")
    for root,dirs,files in os.walk(img_dir):
        for file in files:
            if file.endswith(".png") or file.endswith(".jpg"):
                path=os.path.join(root,file)
                label=os.path.basename(root).replace(" ","-").lower()
                #print(label)
                #print(path)
                if not label in label_ids:
                    label_ids[label]=current_id
                    current_id+=1
                id_=label_ids[label]
                print(id_)
                pil_image=Image.open(path).convert("L") # used for converting image into grayscale
                size=(550,550)
                final_image=pil_image.resize(size,Image.ANTIALIAS)
                img_array=np.array(final_image,"uint8") #uint8 is type and converts images to array format
                #print(img_array)
                faces=face_cascade.detectMultiScale(img_array,1.5,5)
                print(faces)
                for (x,y,w,h) in faces:
                    roi=img_array[y:y+h, x:x+w]
                    x_train.append(roi)
                    y_labels.append(id_)
    #print(x_train)
    #print(y_labels)
    with open("labels.pickle",'wb') as f:
        pickle.dump(label_ids,f)

    recognizer.train(x_train,np.array(y_labels))
    recognizer.save("trainner.yml")
    engine.say("training completed successfully")
    engine.runAndWait()
    
def track_images():
    dir_name=r'F:\python\project\tracked_images'
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
        recognizer=cv2.face.LBPHFaceRecognizer_create()
        label={}
        with open("labels.pickle",'rb') as f:
            og_label=pickle.load(f)
            label={v:k for k,v in og_label.items()}
        recognizer.read("trainner.yml")

        cap=cv2.VideoCapture(0)
        i=0
        while(True):
            ret, frame=cap.read()
            gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            faces=face_cascade.detectMultiScale(frame,1.5,5)
            
            for(x,y,w,h) in faces:
                cv2.rectangle(frame,(x,y),(x+w,y+h),(255,255,255),2)
                
                roi_gray=gray[y:y+h,x:x+w]
                roi_color=frame[y:y+h,x:x+w]
                id_,percent=recognizer.predict(roi_gray)
                if percent>30:
                #print(label[id_])
                    font=cv2.FONT_HERSHEY_SIMPLEX
                    color=(255,230,255)
                    stroke=2
                    cv2.putText(frame,"{}".format(label[id_]),(x,y),font,1,color,stroke,cv2.LINE_AA)
                    cv2.imshow("image",frame)
                    cv2.imwrite(r"{}\tracked{}.png".format(dir_name,i),roi_color)
                    i+=1
            if cv2.waitKey(1) & 0xFF == ord('s'):
                        break
        cap.release();
        cv2.destroyAllWindows();
        return
    else:
        messagebox.showerror("error","Directory already exists")
    
               
root=tk.Tk()
root.configure(bg="teal")
root.title("Face Recognition")
root.geometry("500x500")
l=tk.Label(root,text="FACE RECOGNITION",fg="black",bg="blue",width="100",height="2" ,font=("bold",20))
l.place(x=0,y=0)


label1=tk.Label(root,text="Name",fg="red",width="10",height="1",font=("bold",20))
label1.place(x=50,y=200)

e1=tk.Entry(root,width="10",font=("italic",20))
e1.place(x=250,y=200)

label2=tk.Label(root,text="ID",fg="red",width="10",height="1",font=("bold",20))
label2.place(x=550,y=200)

e2=tk.Entry(root,width="10",font=("italic",20))
e2.place(x=750,y=200)

label3=tk.Label(root,text="Branch",fg="red",width="10",height="1",font=("bold",20))
label3.place(x=1050,y=200)

e3=tk.Entry(root,width="10",font=("italic",20))

e3.place(x=1250,y=200)

button1=tk.Button(root,text="TAKE IMAGES",command=takeimages,fg="white",bg="black",width="30",height="2")
button1.place(x=650,y=300)

button2=tk.Button(root,text="TRAIN IMAGES",command=train_images,fg="white",bg="black",width="30",height="2")
button2.place(x=650,y=400)

button3=tk.Button(root,text="TRACK IMAGES",command=track_images,fg="white",bg="black",width="30",height="2")
button3.place(x=650,y=500)

root.mainloop()

    
