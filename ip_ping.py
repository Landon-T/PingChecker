import os
import subprocess
import csv
import datetime
import time as Time
import tkinter as tk
from tkinter import messagebox
import threading

GlobalRun = False
sleepTime = 10
GlobalAverage = []
GlobalSent = 0
GlobalReceived = 0

def getAverage():
    sum = 0
    for number in GlobalAverage:
        sum+=number
    return round(sum/len(GlobalAverage) ,1)

def checkExists(filename):
    
    try:
        open(filename, "x")
        return 0
    except FileExistsError:
        #print("file already exists")
        return 1
    except:
        print("other error opening file")

def writeToCsv(filename, row):
    with open(filename, "a", newline='',encoding="utf-8") as csvfile:
        fieldnames = ["Sent", "Received","Average Time(ms)","Time"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(row)       
   
class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.IP = "ping "
        self.SLEEP = 10        

    def create_widgets(self):
        
        self.header = header = tk.Frame(master=self, height=3, bg="black")
        self.title = tk.Label(master=self.header,text="Ping Checker", fg="white",bg="black",width=20)
        self.title.pack()
        self.header.pack(fill=tk.X, padx=5, pady=5)
        
        self.inputFrame = tk.Frame(master=self)
        self.inputFrame.rowconfigure(2, minsize=10, weight=1)
        self.inputFrame.columnconfigure([0,1], minsize=10, weight =1)
        self.ipLabel = tk.Label(master=self.inputFrame, text="IP to Ping: ")
        self.ipLabel.grid(row=0, column=0)
        self.ipInput = tk.Entry(master=self.inputFrame, width=20)
        self.ipInput.grid(row=0, column=1, sticky="w")
        self.sleepLabel = tk.Label(master=self.inputFrame, text="Time to Sleep: ")
        self.sleepLabel.grid(row=1, column=0)        
        self.sleepInput = tk.Entry(master=self.inputFrame, width=5)
        self.sleepInput.grid(row=1, column=1, sticky="w") 
        self.inputFrame.pack(padx=5, pady=5)
        
        self.buttonFrame = tk.Frame(master=self)
        self.startButton = tk.Button(master=self.buttonFrame, text="Start", command=self.runPinger)
        self.stopButton = tk.Button(master=self.buttonFrame, text="Stop", command=self.stopPinger)    
        self.startButton.pack(padx=5, pady=5)
        self.stopButton.pack(padx=5, pady=5)
        self.buttonFrame.pack(padx=5, pady=5)
        
        self.labelFrame = tk.Frame(master=self)
        self.pinglabel = tk.Label(master=self.labelFrame, text="Ping Average: Not Started")
        self.pinglabel.pack()
        self.lossLabel = tk.Label(master=self.labelFrame, text="Loss %: Not Started")
        self.lossLabel.pack()
        self.labelFrame.pack(padx=5, pady=5)
        
        self.errorFrame = tk.Frame(master=self)
        self.errorLabel = tk.Label(master=self.labelFrame, text="")
        self.errorLabel.pack()
        self.errorFrame.pack
        
    def runPinger(self):
        global GlobalRun
        GlobalRun = True
        
        self.IP += self.ipInput.get().strip()
        self.SLEEP = int(self.sleepInput.get())
        
        print("Running")
        t = threading.Thread(target=self.Pinger)
        t.start()
        
    def stopPinger(self):
        global GlobalRun
        GlobalRun = False


    def Pinger(self):
        global GlobalAverage
        global GlobalSent
        global GlobalReceived
        global GlobalRun
        errorString = ""
        lost = 0
        while(GlobalRun):
            filename = "PingTest.csv"
            if(not(checkExists(filename))):
                with open(filename, "w", newline='',encoding="utf-8") as csvfile:
                    fieldnames = ["Sent", "Received","Average Time(ms)","Time"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()     
            
            time =  datetime.datetime.now()
            
            ipList = ["google.ca"]
            try:
                output = subprocess.check_output(self.IP, stderr=subprocess.STDOUT, shell=True)
                
            except subprocess.CalledProcessError as err:
                print(err.output)
                errorMessage = str(err.output)
                if "Ping request could not find host google.c. Please check the name and try again." in errorMessage:
                    print("Could not find host. Please enter a new one a try again.")
                    messagebox.showinfo("Ping Checker Error", "Could not find host. Please enter a new one a try again.")
                    GlobalRun = False
                    continue
                print("Error Internet is likely down")
                print("="*20)
                row = {
                    "Sent":"Error",
                    "Received": "Error",
                    "Average Time(ms)": "Error",
                    "Time": time
                }
                writeToCsv(filename, row)
                if len(GlobalAverage) <= 5:
                    GlobalAverage.append(1000)
                else:
                    GlobalAverage.append(1000)
                    GlobalAverage.pop(0)
                #print(GlobalAverage)
                GlobalSent += 4
                GlobalReceived += 0
                lost = int(GlobalSent)-int(GlobalReceived)
                
                self.pinglabel["text"] = "Average Ping: " + str(getAverage())
                self.lossLabel["text"] = "Lost: " + str(lost) + " / " + str(GlobalSent)
                errorString += "Internet Down: "+str(time)+"\n"
                self.errorLabel["text"] = errorString
                Time.sleep(self.SLEEP)
                continue
            
            output = str(output).split(" ")
            sent = "empty"
            received = "empty"
            average = "empty"
            if "Sent" in output:
                index = output.index("Sent")
                sent = output[index+2].strip(",")
                #print("Sent: "+sent)
            if "Received" in output:
                index = output.index("Received")
                received = output[index+2].strip(",")
                #print("Received: "+received)
            if "Average" in output:
                index = output.index("Average")
                average = output[index+2]
                average = average[0]+average[1]
                #print("Average: "+average)   
        
        
            if received < sent:
                #print("="*30)
                row = {
                    "Sent":sent,
                    "Received": received,
                    "Average Time(ms)": average,
                    "Time": time
                }     
                writeToCsv(filename, row)
                errorString += "Lost Packages: "+str(int(sent)-int(received))+" / "+sent+" - " +str(time)+"\n"
                self.errorLabel["text"] = errorString                

            #GlobalAverage = pingSum/pingCount
            if len(GlobalAverage) <= 5:
                GlobalAverage.append(int(average))
            else:
                GlobalAverage.append(int(average))
                GlobalAverage.pop(0)
            #print(GlobalAverage)
            GlobalSent += int(sent)
            GlobalReceived += int(received)
            lost = int(GlobalSent)-int(GlobalReceived)
            
            self.pinglabel["text"] = "Average Ping: " + str(getAverage())
            self.lossLabel["text"] = "Lost: " + str(lost) + " / " + str(GlobalSent)
            Time.sleep(self.SLEEP)    

    
def main():
    root = tk.Tk()
    app = Application(master=root)
    root.title("Ping Checker")
    app.mainloop()

         
main()