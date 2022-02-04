# Importing required modules
from tkinter import *
from tkinter import messagebox,ttk 
from tkcalendar import * # To have a graphic calendar object
from datetime import date # To use current date
from prettytable import PrettyTable # To print the overall ticket in nice format
import mysql.connector as myc
import random,colorama
from colorama import Fore # To add colors to terminal
from pyqrcode import create # To generate a qr code for baggage tag
colorama.init(autoreset=True)

# Initialising Main GUI window
root = Tk()
root.title("AZURE AVIATION!") # Adding a title to main root
root.iconbitmap('Logo.ico') # Adding an icon to root
root.geometry("1064x800") # Geometry of main Root window
canvas = Canvas(root,bg = "#ffffff",height = 800,width = 1064,bd = 0,highlightthickness = 0,relief = "ridge")
canvas.place(x = 0, y = 0)

# Initialising the mysql connection
database = myc.connect(user = 'root',password = 'tiger',host = 'localhost',database = 'airline')
mycursor = database.cursor()
SQL1 = 'CREATE TABLE IF NOT EXISTS AIRLINE_RESERVATION(PNR_NUMBER CHAR(6) PRIMARY KEY,FLIGHT_ID VARCHAR(6),NAME VARCHAR(50),PHONE_NUMBER BIGINT,DATE_SELECTED DATE,DATE_OF_FLIGHT DATE,SEATs_CHOSEN TEXT,TOTAL_COST DOUBLE)' # TEXT is used here because we need to separate seat numbers with comma and put in mysql database
mycursor.execute(SQL1)

# Returns the flightID, date of flight and seats chosen as a dictionary in which key is a tuple and value is a string
# If 2 passengers have same flight ID and same flight date then it takes their seats and puts them to values of dictionary
def CheckAllSeatsBooked():
    D = {}
    SQL = 'SELECT * FROM AIRLINE_RESERVATION'
    mycursor.execute(SQL)
    result = mycursor.fetchall()
    for i in result:
        if (i[1],i[5]) in D:
            a = ','+i[6]
            D[(i[1],i[5])]+=a # If 2 people have same flight id and date of flight then it appends their seats chosen to the dicitonary
        else:
            T = (i[1],i[5]) # If 2 people do not have same flight id or date of flight then simply put to dictionary
            D[T] = i[6]
    return D

def AllBooked():
    flightIds = []
    D = CheckAllSeatsBooked() # Returning the dictionary with flightids and their respective seats chosen
    a = list(D.items())
    for i in a:
        if len(i[-1]) == 278: # if all seats are chosen then the length of such a list if 278
            flightIds.append(i[0][0]) # Append all the flight ids of such flights with all seats booked to flightIds
    return flightIds

# Validating if PNR is not entered and if PNR is entered proceed to PNRGeneration()
def CheckPNR():
    SQL = 'SELECT * FROM AIRLINE_RESERVATION'
    mycursor.execute(SQL)
    result = mycursor.fetchall()
    # If no records in mysql database
    if len(result) == 0:
        pass 
    else:
        for i in result:
            if i[0] == PNR: # If such a PNR already exists then make a new PNR
                PNRGeneration()
            else:
                pass

# Formatting the list containing seats so as to add ',' after each seat number and put it as text in mysql database
def format(List_Pretty):
    string = ','
    return string.join(List_Pretty)# The output will look something like 'A1,A2,A3'

# Inserting the data into mysql table
def MYSQL_Insertion(List_SQL_Data):
    SQL2 = 'INSERT INTO AIRLINE_RESERVATION(PNR_NUMBER,FLIGHT_ID,NAME,PHONE_NUMBER,DATE_SELECTED,DATE_OF_FLIGHT,SEATs_CHOSEN,TOTAL_COST) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
    mycursor.execute(SQL2,List_SQL_Data)
    database.commit()

#=====GENERATING PNR NUMBER=====#
def PNRGeneration():
    global PNR
    L = [chr(i) for i in range(65,91)] # Generating Aphabets from A to Z 
    first,second,third = random.choice(L),random.choice(L),random.choice(L) # The 3 random alphabets to go in PNR number
    PNR = str(random.randint(0,9)) + first + str(random.randint(0,9)) + second + third + str(random.randint(0,9)) # Generating random PNR number having 6 places of the form A1A2A3 randint from 0-9 means 0 and 9 both included
    return PNR

def FlightSeat(Selected_FlightID):
    L = []
    SQL = 'SELECT * FROM AIRLINE_RESERVATION'
    mycursor.execute(SQL)
    result = mycursor.fetchall()

    # Formating the time so as to come in MYSQL time format of year-month-day
    def format(n):
        return n.strftime("%Y-%m-%d")

    # If nothing is in MYSQL database
    if len(result) == 0:
        return L 
    else:
        for i in result:
            if i[1] == Selected_FlightID and format(i[-3]) == g:
                if len(i[-2]) == 1:
                    L.append(i[-2])
                elif len(i[-2]) > 1:
                    Lst = [item.strip() for item in i[-2].split(',')]
                    L.extend(Lst)
                elif len(i) == 0:
                    pass
        return L

# Obtain the seat cost according to which flight selected and if student then give discount of 20%
def seatCost(seat_type_cost):
    global Price
    if is_Stud == 1:
        if sel1.get() == 1:
            Price = seat_type_cost[0] - seat_type_cost[0]*disc
        elif sel2.get() == 1:
            Price = seat_type_cost[1] - seat_type_cost[1]*disc
        elif sel3.get() == 1:
            Price = seat_type_cost[2] - seat_type_cost[2]*disc
    else:
        if sel1.get() == 1:
            Price = seat_type_cost[0]
        elif sel2.get() == 1:
            Price = seat_type_cost[1]
        elif sel3.get() == 1:
            Price = seat_type_cost[2]
    return Price

# Generating the Final ticket
def ticket():
    global l1
    global Selected_FlightID

    # Obtaining the Flight ID according to what user chooses
    if sel1.get() == 1:
        Selected_FlightID = FlightID[0]
    elif sel2.get() == 1:
        Selected_FlightID = FlightID[1]
    elif sel3.get() == 1:
        Selected_FlightID = FlightID[2]

    # Checking if user wants food
    if wantFood == True:
        food_type = Food_taken
        cost_index = Food_List.index(food_type)
        FoodCost = Food_Cost_List[cost_index]
        quanCost = FoodCost*int(quan)
    else:
        quanCost = 0

    # Checking which type of seat is chosen by user
    if seat_Chosen == 'Economy':
        sC = seatCost(cost_Economy)
    elif seat_Chosen == 'First Class':
        sC = seatCost(cost_1st_Class)
    elif seat_Chosen == 'Business':
        sC = seatCost(cost_Business)

    # Calculating The Total Cost and generating Ticket
    Total_Cost = seatno*sC + quanCost # Getting Total cost having seat and food quantity
    Selected_Date = str(sel.get()) # Finding Date selected by user
    Current_Date = str(today) # Getting current date
    prettyprint_List = [PNRGeneration(),Selected_FlightID, name_entry.get(),Mobile_entry.get(),Current_Date,Selected_Date,format(l1),Total_Cost] # Data of ticket in List format
    CheckPNR() # Checks if generated PNR already exists in mysql database if exists then generates new one
    MYSQL_Insertion(prettyprint_List) # Inserts data into mysql database
    table = PrettyTable(['PNR Number','Flight ID','Name','Phone Number','Date Selected ','Date of Flight','Seats Chosen','Total Cost'])
    table.add_row(prettyprint_List) # Adding the row into pretty printed table
    ticket_Payment = Toplevel() # Creating a new window
    ticket_Payment.iconbitmap('Logo.ico')
    ticket_Payment.title('ticket')
    ticket_Lbl = Label(ticket_Payment,text = 'Your Ticket').grid(row=0,column=0)
    nametable = Label(ticket_Payment , text = table , bg = 'white' , fg = 'black' , font = ('COURIER NEW' , 10)).grid(row=1,column=0)
    Payment_root.destroy() # Destroying the main Payment window

# Checking if the Credit Card is valid by returning True and False
def checkCCcard():
    cc_card = CreditCard_entry.get()
    if cc_card.isdigit() == False or len(str(cc_card)) != 16 or int(cc_card)<=0:
        return False
    else:
        return True

# Checking Validity of mobile number
def CheckMobile(MobileParameter):
    Mobile = MobileParameter.get()
    if Mobile.isdigit() == False or len(MobileParameter.get())!=10:
        return False
    else:
        return True

# Checking if name entry is empty or if Credit Card is invalid or if Mobile is invalid
def FinalPay():
    if name_entry.get() == '' or checkCCcard() == False or CheckMobile(Mobile_entry) == False :
            messagebox.showerror('ERROR', 'Select Appropriate Data!',parent = frame1_Payment)
    else:
        ticket()

# Main Payment Window
def Payment():
    global frame1_Payment
    global name_entry
    global bg_color_payment
    global Mobile_entry
    global CreditCard_entry
    global Payment_root
    Food_Display.destroy() # Destroying the Food window

    # Configuring the Payment window
    bg_color_payment = '#00BFFF'
    Payment_root = Toplevel()
    Payment_root.iconbitmap('Logo.ico')
    Payment_root.geometry('800x600')
    Payment_root.title('PAYMENT')
    Payment_root.configure(bg = bg_color_payment) # Adding a color to Payment window
    
    # Creating the payment Frame
    frame1_Payment = Frame(Payment_root,bg = bg_color_payment)
    frame2_Payment = Frame(Payment_root,bg = bg_color_payment)

    # Creating and placing the objects in payment frame
    Payment_Display = Label(frame2_Payment,text = 'Payment',font = ('Courier',30),bg=bg_color_payment).grid(row=0,column=0,padx=20)
    payment_name = Label(frame1_Payment,text = 'Enter Name',bg = bg_color_payment).grid(row=0,column=0)
    name_entry = Entry(frame1_Payment)
    name_entry.grid(row=0,column=1,pady=5,padx=20)
    payment_Mobile = Label(frame1_Payment, text = 'Enter Mobile Number',bg = bg_color_payment).grid(row = 1, column=0)
    Mobile_entry = Entry(frame1_Payment)
    Mobile_entry.grid(row=1, column=1,pady=5)
    payment_CreditCard = Label(frame1_Payment, text = 'Enter Credit Card Number',bg = bg_color_payment).grid(row = 2, column=0,pady=5)
    CreditCard_entry = Entry(frame1_Payment)
    CreditCard_entry.grid(row=2, column=1,pady=5)
    
    # Asking for student ID if user has ticked the Are you Student check box
    if is_Stud == 1:
        payment_StudID = Label(frame1_Payment, text = 'Enter Student ID',bg = bg_color_payment).grid(row = 3, column=0)
        StudID_entry = Entry(frame1_Payment).grid(row=3, column=1,pady=5)
    
    # Final Proceed to Payment Button
    Payment_Btn = Button(frame1_Payment, text = 'Proceed to pay', command = FinalPay, font = ('Courier', 10)).grid(row = 4, column = 0, pady = 50, columnspan=2)

    # Placing the Payment Frames
    frame1_Payment.place(relx = 0.5,rely = 0.5,anchor=CENTER)
    frame2_Payment.place(relx = 0.5,rely = 0.1,anchor=CENTER)

# Validating the quanity input given by user
def CheckQuan():
    global quan
    quan = quantity_input.get()
    try:
        # Making sure quantity is integer greater than 0 
        if int(quan)>0:
            return False
        else:
            return True
    except Exception: # If any other value given the return True
        return True

# Validating for cases when food or quantity is invalid or empty fields
def FinalFood():
    global Food_taken
    if Food_Combo.get() == '' or CheckQuan():
         messagebox.showerror('ERROR', 'Select Appropriate Data!',parent = frame1_Food)
    else:
        Food_taken = Food_Combo.get()
        Payment()

# If Food button is unchecked
def no_Btn_click():
    global wantFood
    wantFood = False
    Food_Display.destroy()
    Payment()

# If Food button is checked
def yes_Btn_click():
    global quantity_input
    global frame1_Food
    global Food_Combo
    global wantFood
    global Food_Cost_List
    global Food_List
    wantFood = True
    yes_Btn = Button(frame1_Food,text = 'YES',command = yes_Btn_click, state = DISABLED, font = ('Courier', 10)).grid(row=0,column=1)
    no_Btn = Button(frame1_Food, text = 'NO', command = no_Btn_click, state = DISABLED, font = ('Courier', 10)).grid(row=0, column=2)
    
    # List of available foods
    Food_List = ['Panner Sandwich (₹100)', 'Noodles (₹200)', 'Chicken Biryani (₹500)', 'Tacos (₹150)', 'Vada Pav (₹75)', 'Popcorn (₹100)', 'Cheese Pizza (₹250)','Pastry (₹80)','Mango Smoothi (₹50)', 'Mixed Fruit Juice (₹40)','Chocolate Mousse (₹90)']

    # Respective Food Costs
    Food_Cost_List = [100, 200, 500, 150 , 75, 100, 250, 80, 50, 40, 90]

    # Adding objects to main Payment Window
    Display_food_Lbl = Label(frame2_Food,text = 'Choose your Food',font = ('Courier',30),bg = bg_color_cancel).grid(row=0,column=0,padx=20)
    Choose_Food = Label(frame1_Food,text = 'Choose your food',bg = bg_color_cancel).grid(row=1,column=0,pady=5,padx=20)
    Food_Combo = ttk.Combobox(frame1_Food,values = Food_List)
    Food_Combo.grid(row=1,column=1,padx=20)
    quantity = Label(frame1_Food,text = 'Enter Quantity ',bg = bg_color_cancel).grid(row=2,column=0,padx=20)
    quantity_input = Entry(frame1_Food,width=23)
    quantity_input.grid(row=2,column=1,pady=5,padx=20)
    PrcdToPay_Btn = Button(frame1_Food, text = 'Proceed to pay', command = FinalFood, font = ('Courier', 10)).grid(row = 3, column = 0, pady = 50, columnspan=2)

#Creating a window for users to select Food
def Food():
    global Food_Display
    global frame1_Food
    global frame2_Food
    global bg_color_cancel

    # Configuring the main Food window
    bg_color_cancel = '#00BFFF'
    Food_Display = Toplevel()
    Food_Display.iconbitmap('Logo.ico')
    Food_Display.geometry('800x600')
    Food_Display.title('CHOOSE FOOD')
    Food_Display.configure(bg = bg_color_cancel)

    # Creating the Frames to hold objects in Food window
    frame1_Food = Frame(Food_Display,bg = bg_color_cancel)
    frame2_Food = Frame(Food_Display,bg = bg_color_cancel)

    # Adding objects to the main food window
    want_food = Label(frame1_Food,text = 'Do you want food?',bg = bg_color_cancel).grid(row=0,column=0,pady=5)
    yes_Btn = Button(frame1_Food,text = 'YES',command = yes_Btn_click, font = ('Courier', 10)).grid(row=0,column=1,pady=5)
    no_Btn = Button(frame1_Food, text = 'NO', command = no_Btn_click, font = ('Courier', 10)).grid(row=0, column=2,pady=5)

    # Placing the food frames
    frame1_Food.place(relx = 0.5,rely = 0.5,anchor=CENTER)
    frame2_Food.place(relx = 0.5,rely = 0.1,anchor=CENTER) 

#=====MAIN FUNCTION TO GENERATE SEATING ARRANGEMENT=====#
def Seating():
    Display_Level.destroy()
    def Display_Seating():
        global seats_Booked
        if sel1.get() == 1:
            Selected_FlightID = FlightID[0]
        elif sel2.get() == 1:
            Selected_FlightID = FlightID[1]
        elif sel3.get() == 1:
            Selected_FlightID = FlightID[2]
        seats_Booked = FlightSeat(Selected_FlightID)
        
        seat_List = [chr(i)+str(j) for i in range(65,74) for j in range(1,11)] # List containing all seat Numbers

        # Displays seating and adds red NA to those seats already booked for a particular flight
        def seat_selection():
            for i in range(65,74):
                for j in range(1,11):
                    if (chr(i)+str(j)) in seats_Booked:
                        print(Fore.RED+'NA',sep='',end=' ')
                    else:
                        print(chr(i),j,sep='',end=' ')
                print()

        seat_selection()
        global seatno
        print()
        
        def again(seatno):
            global l1
            l1=[]
            # After user selects number of seats
            for i in range(1,seatno+1):
                print('CHOOSING SEAT ',i)
                choice=input("ENTER THE SEAT NUMBER: ")

                # Validating if the seat entered by user is already booked by checking with mysql database
                if choice in seats_Booked:
                    print(Fore.RED+'INVALID INPUT')
                    print(Fore.RED+"PLEASE ENTER ALL VALUES AGAIN")
                    print()
                    again(seatno) # Again goes to seat choosing function
                else:
                    # If seat not in current List --> seat_List then append it to l1
                    # l1 is temporary list but seat_List is list of seats in that particular flight from mysql database
                    if choice in seat_List and choice not in l1:
                        l1.append(choice)
                    else:
                        print()
                        print(Fore.RED+'INVALID INPUT')
                        print(Fore.RED+"PLEASE ENTER ALL VALUES AGAINs")
                        again(seatno)

        # Checking if the number of seats entered is valid and not a string or a decimal by using try and except
        def ValidSeat():
            global seatno
            try:
                print(Fore.YELLOW+'*'*35)
                seatno=int(input('ENTER THE NUMBER OF SEATS YOU WANT:'))

                # Validating seatno
                if seatno<=0:
                    print(Fore.RED+'Enter Appropriate Data!')
                    print(Fore.YELLOW+'*'*30)
                    print()
                    Display_Seating()
                else:
                    again(seatno) # Again to display choosing seat
                    for i in range(65,74):
                        for j in range(1,11):
                            if (chr(i)+str(j)) in l1 or (chr(i)+str(j)) in seats_Booked: # If the seat being chosen already exists in seats_Booked or in the temporary list l1
                                print(Fore.RED+'NA',end=' ')
                            else:
                                print(chr(i),j,sep='',end=' ')
                        print()
                    
            except Exception:
                print(Fore.RED+"Invalid Seat number!")
                print()
                print(Fore.YELLOW+'*'*30)
                print()
                Display_Seating()
        ValidSeat()
    Display_Seating()
    print()
    print(Fore.YELLOW+"SELECT FOOD")
    Food()
        
# Data Validation for Check Button
def OptError():
    if sel1.get() == 1 and sel2.get() == 1 and sel3.get() == 1:
        messagebox.showerror('ERROR', 'Select Appropriate Flight!',parent = frame1_Display_Flight)
    elif sel1.get() == 1 and sel2.get() == 1 and sel3.get() == 0:
        messagebox.showerror('ERROR', 'Select Appropriate Flight!',parent = frame1_Display_Flight)
    elif sel1.get() == 1 and sel2.get() == 0 and sel3.get() == 1:
        messagebox.showerror('ERROR', 'Select Appropriate Flight!',parent = frame1_Display_Flight)
    elif sel1.get() == 0 and sel2.get() == 1 and sel3.get() == 1:
        messagebox.showerror('ERROR', 'Select Appropriate Flight!',parent = frame1_Display_Flight)
    elif sel1.get() == 0 and sel2.get() == 0 and sel3.get() == 0:
        messagebox.showerror('ERROR', 'Select Appropriate Flight!',parent = frame1_Display_Flight)
    if sel1.get() == 1 and sel2.get() == 0 and sel3.get() == 0:
        Seating()
    if sel1.get() == 0 and sel2.get() == 1 and sel3.get() == 0:
        Seating()
    if sel1.get() == 0 and sel2.get() == 0 and sel3.get() == 1:
        Seating()

# Generating Flights-IDs, Flight-Time
def From_To_Places(From_Entry,To_Entry,flight_IDs):
    global sel1,sel2,sel3
    global opt_box_1,opt_box_2,opt_box_3
    global is_Stud
    global FlightID
    global cost_Business,cost_1st_Class,cost_Economy
    global disc
    FlightID = flight_IDs

    def Display(cost):
        flight_1 = Label(frame1_Display_Flight,text = "Flight 1 (Connect)",font = ("Arial",12), bg = bg_color).grid(row=0,column=0,padx=30,pady=5)
        flight_2 = Label(frame1_Display_Flight,text = "Flight 2 (Non Stop)",font = ("Arial",12), bg = bg_color).grid(row=1,column=0,padx=30,pady=5)
        flight_3 = Label(frame1_Display_Flight,text = "Flight 3 (Non Stop)",font = ("Arial",12), bg = bg_color).grid(row=2,column=0,padx=30,pady=5)

        flight_id_1 = Label(frame1_Display_Flight,text = flight_IDs[0],font = ("Arial",12), bg = bg_color).grid(row=0,column=1,padx=30,pady=5)
        flight_id_2 = Label(frame1_Display_Flight,text = flight_IDs[1],font = ("Arial",12), bg = bg_color).grid(row=1,column=1,padx=30,pady=5)
        flight_id_3 = Label(frame1_Display_Flight,text = flight_IDs[2],font = ("Arial",12), bg = bg_color).grid(row=2,column=1,padx=30,pady=5)

        flight_time_1 = Label(frame1_Display_Flight,text = Flight_Times[0],font = ("Arial",12), bg = bg_color).grid(row=0,column=2,padx=30)
        flight_time_2 = Label(frame1_Display_Flight,text = Flight_Times[1],font = ("Arial",12),bg = bg_color).grid(row=1,column=2,padx=30)
        flight_time_3 = Label(frame1_Display_Flight,text = Flight_Times[2],font = ("Arial",12),bg = bg_color).grid(row=2,column=2,padx=30)

        # If Not a student then no 20% discount
        if is_Stud == 0:
            cost_1 = Label(frame1_Display_Flight,text = '₹'+str(cost[0]),font = ("Arial",12),bg = bg_color).grid(row=0,column=3,padx=30)
            cost_2 = Label(frame1_Display_Flight,text = '₹'+str(cost[2]),font = ("Arial",12),bg = bg_color).grid(row=1,column=3,padx=30)
            cost_3 = Label(frame1_Display_Flight,text = '₹'+str(cost[1]),font = ("Arial",12),bg = bg_color).grid(row=2,column=3,padx=30)

        # If student then giving 20% discount
        elif is_Stud == 1:
            cost_1 = Label(frame1_Display_Flight,text = '₹'+str(cost[0]-cost[0]*disc),font = ("Arial",12),bg = bg_color).grid(row=0,column=3,padx=30)
            cost_2 = Label(frame1_Display_Flight,text = '₹'+str(cost[2]-cost[2]*disc),font = ("Arial",12),bg = bg_color).grid(row=1,column=3,padx=30)
            cost_3 = Label(frame1_Display_Flight,text = '₹'+str(cost[1]-cost[1]*disc),font = ("Arial",12),bg = bg_color).grid(row=2,column=3,padx=30)

        opt_box_1 = Checkbutton(frame1_Display_Flight,variable=sel1,onvalue=1,offvalue=0,bg = bg_color).grid(row=0,column=4)
        opt_box_2 = Checkbutton(frame1_Display_Flight,variable=sel2,onvalue=1,offvalue=0,bg = bg_color).grid(row=1,column=4)
        opt_box_3 = Checkbutton(frame1_Display_Flight,variable=sel3,onvalue=1,offvalue=0,bg = bg_color).grid(row=2,column=4)

        D = AllBooked() # Getting the list with only flight ids where all seats are booked
        if len(D) == 0: # If such length is 0 then dont do anything
            pass
        else:
            for i in D:
                if i not in FlightID: # If the flight id in allBooked is not in the selectedFlight id
                    display_Btn = Button(frame1_Display_Flight,text = 'CONFIRM',command = OptError, font = ('Courier', 10)).grid(row=4,column=1,padx=20,ipadx=30,pady=(40,0),columnspan=2)
                else:
                    index = FlightID.index(i) # Getting index of the flight id from its list
                    if index == 0:
                            opt_box_1 = Checkbutton(frame1_Display_Flight,variable=sel1,onvalue=1,offvalue=0,bg = bg_color,state = DISABLED).grid(row=0,column=4)
                            booked_lbl = Label(frame1_Display_Flight,text = "(All seats Booked!)",foreground='red').grid(row=0,column=5)
                    if index == 1:
                            opt_box_2 = Checkbutton(frame1_Display_Flight,variable=sel2,onvalue=1,offvalue=0,bg = bg_color,state = DISABLED).grid(row=1,column=4)
                            booked_lbl = Label(frame1_Display_Flight,text = "(All seats Booked!)",foreground='red').grid(row=1,column=5)
                    if index == 2:
                            opt_box_3 = Checkbutton(frame1_Display_Flight,variable=sel3,onvalue=1,offvalue=0,bg = bg_color,state = DISABLED).grid(row=2,column=4)
                            booked_lbl = Label(frame1_Display_Flight,text="(All seats Booked!)",foreground='red').grid(row=2,column=5)
                    else:
                        pass
                    display_Btn = Button(frame1_Display_Flight,text = 'CONFIRM',command = OptError, font = ('Courier', 10)).grid(row=4,column=1,padx=20,ipadx=30,pady=(40,0),columnspan=3)

    From = From_Entry
    To = To_Entry
    is_Stud = var1.get()
    sel1 =  IntVar() # 0 if button not clicked, 1 if button clicked
    sel2 =  IntVar() # 0 if button not clicked, 1 if button clicked
    sel3 =  IntVar() # 0 if button not clicked, 1 if button clicked
    disc = 0.2 # Discount offered by Azure Aviation for students
    Flight_Times = ['6:00 AM','2:00 PM','8:00 PM'] # Flight times

    # Seat costs for different types
    cost_Economy = [6000.0,8000.0,10000.0]
    cost_Business = [10000.0,12000.0,14000.0]
    cost_1st_Class = [14000.0,16000.0,18000.0]
    if seat_Chosen == 'Economy':
        Display(cost_Economy)
    elif seat_Chosen == 'First Class':
        Display(cost_1st_Class)
    elif seat_Chosen == 'Business':
        Display(cost_Business)

# Main Search Flight window
def Search_Flight():
    global frame1_Display_Flight
    global frame2_Display_Flight
    global Flight_Ids
    global bg_color
    global Display_Level
    global Flight_ID_NestedList
    global booked

    # Configuring the Search Flight window
    Top.destroy()
    Display_Level = Toplevel()
    Display_Level.iconbitmap('Logo.ico')
    bg_color = '#00BFFF'
    frame1_Display_Flight = Frame(Display_Level,bg = bg_color)
    frame2_Display_Flight = Frame(Display_Level,bg = bg_color)
    
    # Creating the search flight window
    Display_Level.geometry('850x600')
    Display_Level.title('Display Flights')
    Display_Level.configure(bg = bg_color)
    
    # Creating main objects on search flight window
    Display_flight_Lbl = Label(frame2_Display_Flight,text = 'Displaying Flights...',font = ('Courier',30),bg = bg_color).grid(row=0,column=0)
    SubHeading_Lbl = Label(frame2_Display_Flight,text = '(Flights, Flight ID, Departure Time, Price)',font = ('Arial',15), bg = bg_color).grid(row=1,column=0,pady=(0,40))
    
    #=====FLIGHT IDs=====#
    Flight_ID_NestedList = [['7BTD1','7BTD2','7BTD3'],['7BTM1','7BTM2','7BTM3'],['7BTA1','7BTA2','7BTA3'],['7BTSH1','7BTSH2','7BTSH3'],['7BTG1','7BTG2','7BTG3'],['7DTB1','7DTB2','7DTB3'],['7DTM1','7DTM2','7DTM3'],['7DTA1','7DTA2','7DTA3'],['7DTSH1','7DTSH2','7DTSH3'],['7DTG1','7DTG2','7DTG3'],['7MTB1','7MTB2','7MTB3'],['7MTD1','7MTD2','7MTD3'],['7MTA1','7MTA2','7MTA3'],['7MTSH1','7MTSH2','7MTSH3'],['7MTG1','7MTG2','7MTG3'],['7ATSH1','7ATSH2','7ATSH3'],['7ATD1','7ATD2','7ATD3'],['7ATB1','7ATB2','7ATB3'],['7ATM1','7ATM2','7ATM3'],['7ATG1','7ATG2','7ATG3'],['7SHTD1','7SHTD2','7SHTD3'],['7SHTB1','7SHTB2','7SHTB3'],['7SHTA1','7SHTA2','7SHTA3'],['7SHTM1','7SHTM2','7SHTM3'],['7SHTG1','7SHTG2','7SHTG3'],['7GTB1','7GTB2','7GTB3'],['7GTD1','7GTD2','7GTD3'],['7GTM1','7GTM2','7GTM3'],['7GTA1','7GTA2','7GTA3'],['7GTSH1','7GTSH2','7GTSH3']]

    # Cases to check  From and To Location from users choice and pass to function From_To_Places along with its Flight ID
    if From_Entry == 'Bengaluru' and To_Entry == 'Delhi':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[0])
    elif From_Entry == 'Bengaluru' and To_Entry == 'Mumbai':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[1])
    elif From_Entry == 'Bengaluru' and To_Entry == 'Ahmedabad':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[2])
    elif From_Entry == 'Bengaluru' and To_Entry == 'Shillong':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[3])
    elif From_Entry == 'Bengaluru' and To_Entry == 'Goa':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[4])
    elif From_Entry == 'Delhi' and To_Entry == 'Bengaluru':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[5])
    elif From_Entry == 'Delhi' and To_Entry == 'Mumbai':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[6])
    elif From_Entry == 'Delhi' and To_Entry == 'Ahmedabad':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[7])
    elif From_Entry == 'Delhi' and To_Entry == 'Shillong':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[8])
    elif From_Entry == 'Delhi' and To_Entry == 'Goa':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[9])
    elif From_Entry == 'Mumbai' and To_Entry == 'Bengaluru':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[10])
    elif From_Entry == 'Mumbai' and To_Entry == 'Delhi':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[11])
    elif From_Entry == 'Mumbai' and To_Entry == 'Ahmedabad':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[12])
    elif From_Entry == 'Mumbai' and To_Entry == 'Shillong':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[13])
    elif From_Entry == 'Mumbai' and To_Entry == 'Goa':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[14])
    elif From_Entry == 'Ahmedabad' and To_Entry == 'Shillong':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[15])
    elif From_Entry == 'Ahmedabad' and To_Entry == 'Delhi':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[16])
    elif From_Entry == 'Ahmedabad' and To_Entry == 'Bengaluru':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[17])
    elif From_Entry == 'Ahmedabad' and To_Entry == 'Mumbai':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[18])
    elif From_Entry == 'Ahmedabad' and To_Entry == 'Goa':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[19])
    elif From_Entry == 'Shillong' and To_Entry == 'Delhi':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[20])
    elif From_Entry == 'Shillong' and To_Entry == 'Bengaluru':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[21])
    elif From_Entry == 'Shillong' and To_Entry == 'Ahmedabad':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[22])
    elif From_Entry == 'Shillong' and To_Entry == 'Mumbai':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[23])
    elif From_Entry == 'Shillong' and To_Entry == 'Goa':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[24])
    elif From_Entry == 'Goa' and To_Entry == 'Bengaluru':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[25])
    elif From_Entry == 'Goa' and To_Entry == 'Delhi':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[26])
    elif From_Entry == 'Goa' and To_Entry == 'Mumbai':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[27])
    elif From_Entry == 'Goa' and To_Entry == 'Ahmedabad':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[28])
    elif From_Entry == 'Goa' and To_Entry == 'Shillong':
        From_To_Places(From_Entry,To_Entry,Flight_ID_NestedList[29])
        booked = Flight_ID_NestedList[29]
    
    # Placing the Display Flight Frames
    frame1_Display_Flight.place(relx = 0.5,rely = 0.5,anchor=CENTER)
    frame2_Display_Flight.place(relx = 0.5,rely = 0.1,anchor=CENTER)

# Check Button for availing for Student discount
def Check_Btn():
    global var1
    var1 = IntVar()
    student_chk = Checkbutton(frame1, text ="Are You a student?", variable = var1,onvalue=1,offvalue=0, bg = bgcolor,font=('Arial', 12))
    student_chk.deselect()
    student_chk.grid(row=4,column=0,ipadx=50,pady=(30,0),columnspan=3)
    Submit_Btn = Button(frame1,text = 'Search Flight', command=Search_Flight, font = ('Courier', 10)).grid(row=5,column=0,ipadx=50,pady=30,columnspan=3)

# Building A Date Picker calendar
def calendar():
    global sel
    def submit():
        global string
        global g
        g = sel.get() # Getting Date entered by User
        string = str(g)
        crnt_date = str(today) # Getting current Date
        year = int(string[2:4])
        if g<=str(crnt_date) or year!=22: # Validating the Date
            messagebox.showerror("ERROR",'Choose Correct Date',parent = frame1)
        else:
            Check_Btn()

    sel = StringVar() # Holder to hold the date selected
    Date_Lbl = Label(frame1,text = 'Departure Date',font = ("Arial",15),bg = bgcolor).grid(row=3,column=0)
    Date_Entry = DateEntry(frame1, selectmode = 'day', year = 2022, month = 2, day=1,date_pattern='yyyy-mm-dd', textvariable = sel,width=20) # Tkinter calendar to select the date of flight
    Date_Entry.grid(row = 3, column=1)
    global today
    today = date.today() # Obtaining todays date
    cal_Submit = Button(frame1,text = 'SUBMIT',command=submit, font = ('Courier', 10)).grid(row=3,column=2, pady = 5)

# Checking is no seats chosen else run calendar function
def seatSubmit():
    global seat_Chosen
    seat_Chosen = seat_type.get()
    if seat_Chosen == '':
        messagebox.showerror("ERROR",'Choose Appropriate Data',parent = frame1)
    else:
        calendar()    

# Function to be called after user selects destination Flight
def To():
    global seat_type
    global To_Entry
    seat = StringVar() 
    To_Entry = To_Places.get()
    if To_Entry == '': # Checking if To Entry combobox is emppty
        messagebox.showerror("ERROR", "Please Fill the Field!",parent = frame1)
    else:
        seat_types = ['First Class','Business','Economy']
        pass_lbl = Label(frame1, text = "Seat Type",bg = bgcolor,font = ("Arial",15)).grid(row=2,column=0)
        seat_type = ttk.Combobox(frame1,values = seat_types)
        seat_type.grid(row=2,column=1)
        pass_entry_submit = Button(frame1,text = 'SUBMIT',command=seatSubmit, font = ('Courier', 10)).grid(row=2,column=2,padx=20,pady=5)

# Function to the button SUBMIT next to From places
def From():
    global To_Places
    global From_Entry
    L = ['Bengaluru', 'Delhi','Mumbai','Ahmedabad', 'Shillong', 'Goa']
    From_Entry = From_places.get() # Fetching input from From_places box

    # Checking for validity
    if From_Entry == '':
        messagebox.showerror("ERROR", "Please Fill the Field!",parent = frame1)
    else:
        L.remove(From_Entry) # If the From place exists in To places remove it
        To_Lbl = Label(frame1,text = "To",bg=bgcolor,font = ("Arial",15)).grid(row=1,column=0)
        To_Places = ttk.Combobox(frame1,values = L)
        To_Places.grid(row = 1, column=1)
        to_places_submit = Button(frame1,text = 'SUBMIT',command = To, font = ('Courier', 10)).grid(row=1,column=2,padx=20,pady=5) 

#=====BOOKING WINDOW=====#
def Booking():
    global bgcolor
    global frame1
    global From_places
    global Top
    L = ['Bengaluru', 'Delhi','Mumbai','Ahmedabad', 'Shillong', 'Goa']
    bgcolor = '#00BFFF'
    Top = Toplevel()
    Top.iconbitmap('Logo.ico')
    Top.geometry('800x600')
    Top.title('Booking Ticket')
    Top.configure(bg = bgcolor)

    # Creating Booking Frames
    frame1 = Frame(Top,bg = bgcolor)
    frame2 = Frame(Top,bg = bgcolor)

    # Creating and placing the Objects on the booking Frame
    Booking_Lbl = Label(frame2,text = 'BOOKING TICKET',bg = bgcolor ,font = ('Courier',30) ).grid(row=0,column=0)
    From_lbl = Label(frame1, text = "From",bg =bgcolor,font = ("Arial",15)).grid(row=0,column=0)
    From_places = ttk.Combobox(frame1,values=L)
    From_places.grid(row=0,column=1)
    from_places_submit = Button(frame1,text = 'SUBMIT',command=From, font = ('Courier', 10)).grid(row=0,column=2,padx=20,pady=5)
    space_label = Label(frame1,text = ' '*50,bg = bgcolor).grid(row=3,column=0)

    # Placing the Frames
    frame2.place(relx = 0.5,rely = 0.1,anchor=CENTER)
    frame1.place(relx=0.5,rely=0.5,anchor=CENTER)

#=====CANCELLATION - DATA VALIDATION=====#
def CancelTicket():
    string_PNR = str(PNR_entry_no)

    # Displaying the details when ticket is deleted
    SQL = "DELETE FROM AIRLINE_RESERVATION WHERE PNR_NUMBER = %s"
    statement = f'''
    Ticket Deleted!

    PNR Number : {record[0][0]}
    Passenger Name : {record[0][2]}
    Flight Number : {record[0][1]}
    Mobile Number : {record[0][3]}
    '''
    mycursor.execute(SQL,(string_PNR,))
    database.commit()
    messagebox.showinfo("DELETED!",statement,parent = frame1_cancellation)

# Checking if the Phone number entered really exists for that particular PNR no by comparing with mysql database
def Checker(result,PNR_entry_no):
    global record
    temp = 0
    record = []
    for i in result:
        if PNR_entry_no == i[0] and int(Phone.get())==i[3]:
            record.append(i) # Appending record with details where PNR_entry_no and Phone.get() matches with record in mysql
            temp = 1 # Temporary variable to hold 1
    if temp == 0:
        messagebox.showerror("ERROR", "Ticket Does not Exist!",parent = frame1_cancellation) # Parent makes the window pops on the same frame

    # If temp !=0
    else:
        CancelTicket()

# Checking if the ticket entered really exists by comparing with mysql database
def TicketExists():
    global PNR_entry_no
    PNR_entry_no = PNRno.get()
    SQL = 'SELECT * FROM AIRLINE_RESERVATION'
    mycursor.execute(SQL)
    result = mycursor.fetchall()
    # If no records in mysql table
    if len(result) == 0:
        messagebox.showerror("ERROR", "Ticket does not exist!",parent = frame1_cancellation)
    else:
        Checker(result,PNR_entry_no)

# Cancellation of Record
def CancelDetails():
    # If phone number if invalid
    if CheckMobile(Phone) == False:
        messagebox.showerror("ERROR", "INVALID ENTRIES!",parent = frame1_cancellation)
    else:
        TicketExists()

#=================CANCELLATION WINDOW==============#
def Cancellation():
    global Phone
    global frame1_cancellation
    global PNRno
    bg_color_cancel = '#00BFFF'
    Display = Toplevel()
    Display.iconbitmap('Logo.ico')
    Display.geometry('800x600')
    Display.title('CANCELLATION')
    Display.configure(bg = bg_color_cancel)

    # Creating Frames for cancellation
    frame1_cancellation = Frame(Display,bg = bg_color_cancel)
    frame2_cancellation = Frame(Display,bg = bg_color_cancel)
    
    # Creating and placing the window objects
    Cancel_Lbl = Label(frame2_cancellation,text = 'Cancellation',bg = bg_color_cancel ,font = ('Courier',30)).grid(row=0,column=0)
    PNR_lbl = Label(frame1_cancellation, text = 'Enter PNR Number', bg = bg_color_cancel, font = ('Arial',12)).grid(row = 0,column=0,pady=5, padx =20)
    PNRno = Entry(frame1_cancellation, width = 20)
    PNRno.grid(row=0,column=1)
    Phone_lbl = Label(frame1_cancellation, text = 'Enter Phone No', bg = bg_color_cancel,font = ('Arial',12)).grid(row = 2,column=0,pady=5)
    Phone = Entry(frame1_cancellation, width = 20)
    Phone.grid(row=2,column=1) 
    Final_Btn = Button(frame1_cancellation,text = 'Confirm',command = CancelDetails, font = ('Courier', 10)).grid(row=3,column=0,pady = 20, ipadx = 20, columnspan=2)

    # Placing the frames
    frame1_cancellation.place(relx = 0.5,rely = 0.5,anchor=CENTER)
    frame2_cancellation.place(relx = 0.5,rely = 0.1,anchor=CENTER) 

#===================BAGGAGE TAG====================#
def baggage_in_QR():
    # Final printing when QR code is scanned
    s = f'''
    \t\t\t\tBAGGAGE TAG
    \t\t\t\tAzure Aviation Happy Flying!
    \t\t\t\t25Kg Luggage Permitted
    
    ***********************************

    PNR Number : {Check_in_record[0][0]}
    Passenger Name : {Check_in_record[0][2]}
    Flight Number : {Check_in_record[0][1]}
    Seat(s) Chosen: {Check_in_record[0][6]}
    Date of Flight: {Check_in_record[0][5]}
    Mobile Number : {Check_in_record[0][3]}
    '''
    return s # Returning the formatted string

#=====BAGGAGE TAG WINDOW=====#    
def Show_baggage_tag(PNR_entry_no):
    global frame1_Check_in
    bg_color_baggage_tag = '#00BFFF'
    Display = Toplevel()
    Display.iconbitmap('Logo.ico')
    Display.geometry('800x600')
    Display.title('Baggage Tag')
    Display.configure(bg = bg_color_baggage_tag)

    # Creating the window Frames
    frame1_baggage_tag = Frame(Display,bg = bg_color_baggage_tag)
    frame2_baggage_tag = Frame(Display,bg = bg_color_baggage_tag)

    # Baggage tag window objects
    Baggage_tag_heading = Label(frame2_baggage_tag, text = 'Baggage Tag', bg = bg_color_baggage_tag, font = ('Courier',30)).grid(row = 0, column=0)
    Baggage_tag_SubHeading = Label(frame2_baggage_tag, text = 'Your Baggage Tag Has Been Successfully Generated ✅ \n Scan to Print Baggage Tag!', bg = bg_color_baggage_tag,font = ('Courier',15)).grid(row = 1, column=0)
    image_view = Label(frame1_baggage_tag)
    image_view.grid(row=0,column=1)

    #=====QR CODE=====#
    QR_Data = baggage_in_QR()
    img = create(QR_Data) # Creating the QR code from QR_Data
    test = img.xbm(scale = 2) # Scaling the image to 2
    global xbm_image
    xbm_image = BitmapImage(data=test,foreground='Blue',background='yellow')# Creating a BitmapImage out of the QR code 
    image_view.config(image = xbm_image) # Configuring the Label with the QR code

    # Packing the Frames
    frame1_baggage_tag.place(relx = 0.5,rely = 0.5,anchor=CENTER)
    frame2_baggage_tag.place(relx = 0.5,rely = 0.1,anchor=CENTER)

# Checking validity of PNR and Phone entered with mysql database
def Checker_baggage_tag(result,PNR_entry_no):
    global Check_in_record
    Check_in_record = []
    temp = 0
    for i in result:
        if PNR_entry_no == i[0] and int(Phone.get())==i[3]: # If PNR_entry_no == i[0] and phone.get() then append to Check_in_record
            Check_in_record.append(i)
            temp = 1
    if temp == 0:
        messagebox.showerror("ERROR", "Ticket Does not Exist!",parent = frame1_Check_in)
    else:
        Show_baggage_tag(PNR_entry_no)

# Checking validity of PNR number by connecting to mysql
def Ticket_baggage():
    global result
    global PNR_entry_no
    PNR_entry_no = PNRno.get()
    SQL = 'SELECT * FROM AIRLINE_RESERVATION'
    mycursor.execute(SQL)
    result = mycursor.fetchall()

    # If no records in MYSQL database
    if len(result) == 0:
        messagebox.showerror("ERROR","INVALID ENTRIES!",parent = frame1_Check_in)
    else:
        Checker_baggage_tag(result,PNR_entry_no)

# Checking if Entries are valid
def Baggage_tag():
    global  PNR_entry_no
    PNR_entry_no = PNRno.get()
    # Checking if PNR entry is empty or is Phone entry is invalid or if Phone entered is not valid
    if PNRno.get() == '' or Phone.get() == '':
        messagebox.showerror("ERROR", "Please Fill the Field",parent = frame1_Check_in)
    elif Phone.get().isalpha():
        messagebox.showerror("ERROR", "Please Fill appropriately",parent = frame1_Check_in)
    else:
        Ticket_baggage()

#=====CHECK IN WINDOW=====#        
def Check_in():
    global frame1_Check_in
    global PNRno
    global Phone

    # Configuring the Check in Window
    bg_color_check_in = '#00BFFF'
    Display = Toplevel()
    Display.iconbitmap('Logo.ico')
    Display.geometry('800x600')
    Display.title('Check in')
    Display.configure(bg = bg_color_check_in)

    # Creating Check in Frames
    frame1_Check_in = Frame(Display,bg = bg_color_check_in)
    frame2_Check_in = Frame(Display,bg = bg_color_check_in)

    # Creating and placing objects in Check in window
    Checkin_Lbl = Label(frame2_Check_in,text = 'CHECKING IN',bg = bg_color_check_in ,font = ('Courier',30)).grid(row=0,column=0)
    PNR_lbl = Label(frame1_Check_in, text = 'Enter PNR number', bg = bg_color_check_in,font = ('Arial',12)).grid(row = 0,column=0,pady=5, padx = 20)
    PNRno = Entry(frame1_Check_in, width = 20)
    PNRno.grid(row=0,column=1)
    Phone_lbl = Label(frame1_Check_in, text = 'Enter Phone no', bg = bg_color_check_in,font = ('Arial',12)).grid(row = 2,column=0,pady=10)
    Phone = Entry(frame1_Check_in, width = 20)
    Phone.grid(row=2,column=1) 
    Final_Btn = Button(frame1_Check_in,text = 'Confirm', font = ('Courier', 10),padx=3, pady = 1, command = Baggage_tag).grid(row=3,column=0,pady = 15, ipadx = 15, columnspan=2)

    # Placing the Check in Frames
    frame1_Check_in.place(relx = 0.5,rely = 0.5,anchor=CENTER)
    frame2_Check_in.place(relx = 0.5,rely = 0.1,anchor=CENTER)

#=============MAIN WINDOW OBJECTS=============#     
check_in_pic = PhotoImage(file = f"Check_in.png")
Checkin_button = Button(image = check_in_pic,borderwidth = 0,highlightthickness = 0,relief = "flat",command=Check_in)
Checkin_button.place(x = 671, y = 556,width = 294,height = 65)

img1 = PhotoImage(file = f"cancel.png")
Cancellation_button = Button(image = img1,borderwidth = 0,highlightthickness = 0,relief = "flat",command=Cancellation)
Cancellation_button.place(x = 671, y = 442,width = 294,height = 69)

img2 = PhotoImage(file = f"booking.png")
Booking_button = Button(image = img2,borderwidth = 0,highlightthickness = 0,relief = "flat",command=Booking)
Booking_button.place(x = 671, y = 334,width = 293,height = 65)

background_img = PhotoImage(file = f"background.png")
background = canvas.create_image(529.0, 400.0,image=background_img)

# Making the Main window non-resizable
root.resizable(False, False) 

# Running the mainloop application
root.mainloop()

'''
To View QR code on PC
QR SCANNER: https://www.imgonline.com.ua/eng/scan-qr-bar-code.php
'''