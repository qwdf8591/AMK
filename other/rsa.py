from tkinter import Tk, Label, Entry, Button,StringVar
import tkinter.font as tkFont
import random

mainWin = Tk()
mainWin.title("RSA生成器")
mainWin.geometry("250x200")

ft = tkFont.Font(family='Fixdsys', size=20, weight=tkFont.BOLD)
firstNumLabel = Label(mainWin, text="公鑰",font=ft)
secondNumLabel = Label(mainWin, text="私鑰",font=ft)
public_key=StringVar()
private_key=StringVar()
firstNum = Entry(mainWin, text=public_key)
secondNum = Entry(mainWin, text=private_key)

def cal():

        
	prime=[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
	p,q=random.choices(prime,k=2)
	while p==q:
		q=random.choice(prime)
	n = p * q
	fn = (p-1) * (q-1)
	e=random.choice(prime)
	while fn%e==0 and e<fn:
		e=random.choice(prime)
	i = 1
	while 1:
		if (i*e)%fn==1:
			d=i
			break
		i+=1
	
	public_key.set("("+str(e)+","+str(n)+")")
	private_key.set("("+str(d)+","+str(n)+")")

Btn = Button(mainWin, text="生成",command=cal,font=ft)

firstNumLabel.grid(row=0,column=0)
firstNum.grid(row=0,column=2)
secondNumLabel.grid(row=1,column=0)
secondNum.grid(row=1,column=2)
Btn.place(x=120,y=120)

mainWin.mainloop()
