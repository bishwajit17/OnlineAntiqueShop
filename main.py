from flask import Flask, render_template, url_for, redirect, request, abort, session, jsonify
import gc
# import MySQLdb
# import mysql.connector
import dbConnection
from passlib.hash import sha256_crypt
from functools import wraps
from datetime import date, datetime
from validation import *

app = Flask(__name__)
app.secret_key = 'This is my Secret key'


# def get_connection():
#     conn = mysql.connector.connect(host="127.0.0.1",
#                                    user="rutvik2samant",
#                                    password="Innsworth@164",
#                                    database="rutvik2samant_prj")
#     return conn



# search individual item using search bar

@app.route('/searchSetItem', methods=['POST', 'GET'])
def searchSetItem():
    if request.method == "POST":
        searchItem = request.form['searchItem']
        conn = dbConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM set_List")
        sets = cursor.fetchall()
        searchStatement= "SELECT * FROM SetListItem WHERE Item_No LIKE %s;"
        cursor.execute(searchStatement, (searchItem,))
        w = cursor.fetchall()
        if cursor.rowcount > 0:
            cursor.close()
            conn.close()
            return render_template('setItemAfterLogin.html', rows=w, sets=sets)
        else:
            cursor.execute("SELECT * FROM SetListItem;")
            row = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template('setItemAfterLogin.html', rows=row, sets=sets)
        # return render_template('searchIndividualItem.html', data=data , items = itemNos)

@app.route('/searchIndividualItem', methods=['POST', 'GET'])
def searchIndividualItem():
    if request.method == "POST":
        searchItem = request.form['searchItem']
        conn = dbConnection.get_connection()
        cursor = conn.cursor()
        searchStatement = "SELECT * FROM ItemForSale WHERE Item_No LIKE %s;"
        cursor.execute(searchStatement, (searchItem,))
        rows = cursor.fetchall()
        if cursor.rowcount > 0:
            cursor.close()
            conn.close()
            return render_template("main.html", rows=rows)
        else:
            cursor.execute("SELECT * FROM ItemForSale;")
            row = cursor.fetchall()
            return render_template("main.html", rows=row)

# buying items
@app.route('/deleteItemFormSetItems', methods=['POST', 'GET'])
def deleteItemFormSetItems():
    if request.method == "POST":
        setNumber = request.form['setNumber']
        itemNos = request.form.getlist('itemsNumber')
        data = [setNumber, itemNos]
        return render_template('deleteItemFromSetItems.html', data=data , items = itemNos)

@app.route('/deleteItemFromSetItemsForm', methods=['POST', 'GET'])
def deleteItemFromSetItemsForm():
    if request.method == "POST":
        setNumber = request.form['setNumber']
        deleteItem = request.form['deleteItem']
        itemsNo = request.form.getlist('itemsNo')
        conn = dbConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SetListItem")
        rows = cursor.fetchall()
        cursor.execute("SELECT * FROM set_List")
        sets = cursor.fetchall()
        
        print(sets)
        for x in itemsNo:
            print(x)
            if x == deleteItem:
                print(x)
                deleteStatementSetList = "DELETE FROM set_List WHERE saleItemNo = %s;"
                cursor.execute(deleteStatementSetList, (deleteItem,))
                conn.commit()
                cursor.close()
                conn.close()
                return render_template('setItemAfterLogin.html', error= "Successfully Deleted "+ deleteItem + " From Set "+ setNumber, rows=rows, sets=sets)
        cursor.close()
        conn.close()
        return render_template('setItemAfterLogin.html', rows=rows, sets=sets, error="Item Not Found, Try Agian And Use Correct Item Number.")
        

# showing buy items for user
@app.route('/soldItemUser')
def soldItemUser():
    name = session['username']
    print(name)
    conn = dbConnection.get_connection()
    dbcursor = conn.cursor()
    if session['usertype'] == 'Standard':
        statementSet = "SELECT Id, ItemId, itemName, itemInSet, price, soldDate FROM soldAntiqueItem WHERE UserName = %s ORDER BY Id DESC"
        dbcursor.execute(statementSet, (name,))
        data = dbcursor.fetchall()
        dbcursor.close()
        conn.close()
        return render_template('soldItemUser.html', data=data)
    else:
        dbcursor.execute("SELECT * FROM soldAntiqueItem ORDER BY Id DESC")
        data = dbcursor.fetchall()
        dbcursor.close()
        conn.close()
        return render_template('soldItemAdmin.html', data=data)


# buy set items
@app.route('/buySetItem', methods=['POST', 'GET'])
def buySetItem():
    if request.method == "POST":
        setNumber = request.form['setNumber']
        setName = request.form['setName']
        setPrice = request.form['setPrice']
        itemsNumber = request.form.getlist('itemsNumber')
        data = [setNumber, setName, setPrice]
        items = itemsNumber
        print(items)
        return render_template('buySetItem.html', items=items, data=data)


@app.route('/buySetItemForm', methods=['POST', 'GET'])
def buySetItemForm():
    if request.method == "POST":
        name = session['username']
        setNumber = request.form['setNumber']
        setName = request.form['setName']
        setPrice = request.form['setPrice']
        itemsNumber = request.form.getlist('itemsNumber')
        print(itemsNumber)
        listItems = itemsNumber[0]
        print(listItems[0])
        itemString = str(itemsNumber)
        string = ','.join(str(x) for x in itemsNumber)
        toDay = date.today()
        address = request.form['address']
        print("1 here")
        print(itemString)
        print(setNumber)
        print(itemsNumber[0])
        conn = dbConnection.get_connection()
        dbcursor = conn.cursor()
        dbcursor.execute("SELECT * FROM ItemForSale")
        main = dbcursor.fetchall()
        insertStatement = "INSERT soldAntiqueItem(UserName, ItemId, itemName, itemInSet, price, soldDate, address) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        deleteStatementFormSet = "DELETE FROM SetListItem WHERE Item_No = %s;"
        deleteStatementFormItem = "DELETE FROM ItemForSale WHERE Item_No = %s;"
        deleteStatementsetList = "DELETE FROM set_List WHERE setItemNo = %s;"
        statement = "SELECT Item_No FROM SetListItem WHERE Item_No = %s"
        dbcursor.execute(statement, (setNumber,))
        rows = dbcursor.fetchall()
        print(rows)
        if dbcursor.rowcount > 0:
            dbcursor.execute(insertStatement, (name, setNumber,
                             setName, itemString, setPrice, toDay, address))
            print("Here 2")
            dbcursor.execute(deleteStatementsetList, (setNumber,))
            # conn.commit()
            print("here 5")
            dbcursor.execute(deleteStatementFormSet, (setNumber,))
            # conn.commit()
            # intNumberItems = int(itemsNumber)
            for x in itemsNumber:
                print(x)
                dbcursor.execute(deleteStatementFormItem, (x,))
                # conn.commit()
            dbcursor.execute("SELECT * FROM ItemForSale")
            rows = dbcursor.fetchall()
            dbcursor.close()
            conn.commit()
            conn.close()
            gc.collect()
            session['logged_in'] = True
            # return main()
            return render_template("main.html", message="Sucessfully able to buy.", rows=rows)
        else:
            return render_template("main.html", rows=main, error="Antique Item Not Found, Reload The Page Please!")
    else:
        return render_template("main.html", rows=main, error="Request Server Error Please Try Later!")


# buying items
@app.route('/buyIndividualItem', methods=['POST', 'GET'])
def buyIndividualItem():
    if request.method == "POST":
        userName = request.form['username']
        itemNo = request.form['itemNumber']
        itemName = request.form['itemName']
        price = request.form['itemPrice']
        shop = request.form['shopType']
        data = [itemNo, itemName, price, shop, userName]
        conn = dbConnection.get_connection()
        dbcursor = conn.cursor()
        # dbcursor.execute(
        #     "SELECT Item_No FROM ItemForSale WHERE Item_No != ( Select saleItemNo FROM set_List WHERE setItemNo = 2000)")
        dbcursor.execute(
            "Select saleItemNo FROM set_List WHERE setItemNo = 2000")
        print("Inside Main ")
        rows = dbcursor.fetchall()
        print(rows)
        return render_template('buyIndividualItem.html', data=data)


@app.route('/buyIndividualItemForm', methods=['POST', 'GET'])
def buyIndividualItemForm():
    if request.method == "POST":
        userName = request.form['username']
        itemNo = request.form['itemNumber']
        itemName = request.form['itemName']
        price = request.form['price']
        shop = request.form['shopType']
        address = request.form['address']
        toDay = date.today()
        print("1 here")
        print(itemNo)
        conn = dbConnection.get_connection()
        dbcursor = conn.cursor()
        dbcursor.execute("SELECT * FROM ItemForSale")
        main = dbcursor.fetchall()
        # insertStatement = "INSERT itemSold(itemNumber, itemName, price, soldDate, shopType) VALUES (%s, %s, %s, %s, %s)"
        insertStatement = "INSERT soldAntiqueItem(UserName, ItemId, itemName, price, soldDate, shopType, address) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        deleteStatement = "DELETE FROM ItemForSale WHERE Item_No = %s;"

        statement = "SELECT Item_No FROM ItemForSale WHERE Item_No = %s"
        dbcursor.execute(statement, (itemNo,))
        rows = dbcursor.fetchall()
        print(rows)
        if dbcursor.rowcount > 0:
            print("inside")
            statementSet = "SELECT saleItemNo FROM set_List WHERE saleItemNo = %s"
            dbcursor.execute(statementSet, (itemNo, ))
            item = dbcursor.fetchall()
            if dbcursor.rowcount > 0:
                dbcursor.execute(
                    insertStatement, (userName, itemNo, itemName, price, toDay, shop, address))
                deleteStatementSetList = "DELETE FROM set_List WHERE saleItemNo = %s;"
                dbcursor.execute(deleteStatementSetList, (itemNo,))
                dbcursor.execute(deleteStatement, (itemNo,))
                conn.commit()
                dbcursor.execute("SELECT * FROM ItemForSale")
                rows = dbcursor.fetchall()
                dbcursor.close()
                conn.close()
                gc.collect()
                session['logged_in'] = True
                # return main()
                return render_template("main.html", message="Sucessfully able to buy check to you Buy Items List.", rows=rows)

            else:
                dbcursor.execute(
                    insertStatement, (userName, itemNo, itemName, price, toDay, shop, address))
                dbcursor.execute(deleteStatement, (itemNo,))
                conn.commit()
                dbcursor.execute("SELECT * FROM ItemForSale")
                rows = dbcursor.fetchall()
                dbcursor.close()
                conn.close()
                gc.collect()
                session['logged_in'] = True
                # return main()
                return render_template("main.html", message="Sucessfully able to buy.", rows=rows)
        else:
            return render_template("main.html", rows=main, error="Antique Item Not Found, Reload The Page Please!")
    else:
        return render_template("main.html", rows=main, error="Request Server Error Please Try Later!")


@app.route('/addNewItemInSetForm', methods=['POST', 'GET'])
def addNewItemInSetForm():
    if request.method == "POST":
        itemNo = request.form['setId']
        items = request.form.getlist('multipleItems')
        print(items)
        print(itemNo)
        INSERT_statement = "SELECT saleItemNo FROM set_List WHERE setItemNo = %s"

        if itemNo != None:
            conn = dbConnection.get_connection()
            dbcursor = conn.cursor()  # Creating cursor object
            dbcursor.execute(INSERT_statement, (itemNo,))
            saleItem = dbcursor.fetchall()
            dbcursor.execute("SELECT * FROM SetListItem")
            rows = dbcursor.fetchall()
            dbcursor.execute("SELECT * FROM set_List")
            sets = dbcursor.fetchall()
            print(saleItem)

            if conn != None:
                if conn.is_connected():
                    print('MySQLerererererer Connection is established')
                    # dbcursor = conn.cursor()
                    print("Testing....")
                    statement = "INSERT set_List(setItemNo , saleItemNo ) VALUES (%s, %s)"
                    for x in items:
                        print(x)
                        dbcursor.execute(statement, (itemNo, x))
                    conn.commit()
                    dbcursor.execute("SELECT * FROM set_List")
                    sets = dbcursor.fetchall()
                    print('You are sucessfully able to Add items.')
                    dbcursor.close()
                    conn.close()
                    gc.collect()
                    session['logged_in'] = True
                    return render_template('setItemAfterLogin.html', rows=rows, sets=sets, message="Succesfully able to add items")
                else:
                    print('Connection error')
                    return render_template('setItemAfterLogin.html', rows=rows, sets=sets, error="Unable to add item, Connection Error!")
            else:
                print('Conncetion error')
                return render_template('setItemAfterLogin.html', rows=rows, sets=sets, error="Unable to add item, Connection Error!")
        else:
            print('empty parameters')
            return render_template('setItemAfterLogin.html', rows=rows, sets=sets, error="Unable to add item, Empty Parameters!")
            # return render_template("addNewItemInSet.html", error ="Unable to add Set of new item",rows=cities)

    else:
        return render_template('setItemAfterLogin.html', rows=rows, sets=sets, error="Unable to add item, request error!")
        # return render_template("addNewItemInSet.html", error="Unable to add Set of new items",rows=cities)


# add items in set
@app.route('/addNewItemInSet', methods=['POST', 'GET'])
def addNewItemInSet():
    if request.method == "POST":
        setNumber = request.form['setNumber']
        itemsNumber = request.form.getlist('itemsNumber')
        print(setNumber)
        datainfo = [setNumber]
        print(itemsNumber)
        # UPDATE_statement = ('SELECT set_List.saleItemNo FROM set_List WHERE set_List.setItemNo = %s')
        # UPDATE_statement = ('SELECT ItemForSale.Item_No FROM ItemForSale WHERE ItemForSale.Item_No != (SELECT set_List.saleItemNo FROM set_List WHERE set_List.setItemNo = %s)')
        conn = dbConnection.get_connection()
        if conn != None:  # Checking if connection is None
            print('MySQL Connection is established')
            dbcursor = conn.cursor()  # Creating cursor object
            # dbcursor.execute(UPDATE_statement,(setNumber,))
            dbcursor.execute("SELECT Item_No FROM ItemForSale")
            rows = dbcursor.fetchall()
            # print(rows)
            dbcursor.execute("SELECT * FROM set_List")
            sets = dbcursor.fetchall()
            # print(sets)
            dbcursor.close()
            conn.close()  # Connection must be
            cities = []  # list of all cities where accomodation can be booked
            for city in rows:  # as we used fetchall we must clean the data
                city = str(city).strip("(")
                city = str(city).strip(")")
                city = str(city).strip(",")
                city = str(city).strip("'")
                cities.append(city)

            return render_template('addNewItemInSet.html', rows=cities, data=datainfo, sets=sets, items=itemsNumber)
        else:
            print('DB connection Error')
            return 'DB Connection Error'

# update set of items


@app.route('/updateSet', methods=['POST', 'GET'])
def updateSet():
    if request.method == "POST":
        setNumber = request.form['setNumber']
        setName = request.form['setName']
        setPrice = request.form['setPrice']
        itemsNumber = request.form.getlist('itemsNumber')
        transferData = [setNumber, setName, setPrice]
        items = itemsNumber
        print(items)
        print(setNumber)
        print(setName)
        print(setPrice)
        return render_template('updateSetItem.html', data=transferData, items=items)


@app.route('/updateSetItemForm', methods=['POST', 'GET'])
def updateSetItemForm():
    if request.method == "POST":
        itemNo = request.form['number']
        description = request.form['description']
        price = request.form['price']
        print(itemNo)
        print(description)
        print(price)
        print("Inside update set form")
        UPDATE_statement = (
            "UPDATE SetListItem SET setDescription = %s, Price = %s WHERE Item_No = %s")
        if itemNo != None and description != None and price != None:
            conn = dbConnection.get_connection()
            if conn != None:
                if conn.is_connected():
                    dbcursor = conn.cursor()
                    dbcursor.execute(UPDATE_statement,
                                     (description, price, itemNo))
                    # dbcursor.execute("SELECT * FROM ItemForSale")
                    # rows = dbcursor.fetchall()
                    dbcursor.execute("SELECT * FROM SetListItem")
                    rows = dbcursor.fetchall()
                    dbcursor.execute("SELECT * FROM set_List")
                    sets = dbcursor.fetchall()
                    conn.commit()
                    print('You are sucessfully able to Update items.')
                    dbcursor.close()
                    conn.close()
                    gc.collect()
                    session['logged_in'] = True
                    return render_template("setItemAfterLogin.html", message='You are successfully able to Update Item ' + itemNo, rows=rows, sets=sets)
                else:
                    print('Connection error')
                    return render_template("updateSetItem.html", error="Unable to Update new items")
            else:
                print('Conncetion error')
                return render_template("updateSetItem.html", error="Unable to Update new items")
        else:
            print('empty parameters')
            return render_template("updateSetItem.html", error="Unable to Update new item")
    else:
        return render_template("updateSetItem.html", error="Unable to Update new items")


# add new set of items
@app.route('/addNewSetsItem')
def addNewSetsItem():
    conn = dbConnection.get_connection()
    if conn != None:  # Checking if connection is None
        print('MySQL Connection is established')
        dbcursor = conn.cursor()  # Creating cursor object
        dbcursor.execute('SELECT Item_No FROM ItemForSale;')
        rows = dbcursor.fetchall()
        dbcursor.close()
        conn.close()  # Connection must be
        cities = []  # list of all cities where accomodation can be booked
        for city in rows:  # as we used fetchall we must clean the data
            city = str(city).strip("(")
            city = str(city).strip(")")
            city = str(city).strip(",")
            city = str(city).strip("'")
            cities.append(city)
        return render_template('addNewSetsItem.html', rows=cities)
    else:
        print('DB connection Error')
        return 'DB Connection Error'


@app.route('/addNewSetsItemForm', methods=['POST', 'GET'])
def addNewSetsItemForm():
    if request.method == "POST":
        itemNo = request.form['itemNo']
        description = request.form['description']
        price = request.form['price']
        items = request.form.getlist('multipleItems')
        print(itemNo)
        print(description)
        print(price)
        print(items)
        # for x in items:
        #     print(x)
        INSERT_statement = (
            "INSERT INTO SetListItem (Item_No, setDescription, Price) VALUES (%s, %s, %s);")
        if itemNo != None and description != None and price != None and items != None:
            conn = dbConnection.get_connection()
            dbcursor = conn.cursor()  # Creating cursor object
            dbcursor.execute('SELECT Item_No FROM ItemForSale;')
            rows = dbcursor.fetchall()
            cities = []  # list of all cities where accomodation can be booked
            for city in rows:  # as we used fetchall we must clean the data
                city = str(city).strip("(")
                city = str(city).strip(")")
                city = str(city).strip(",")
                city = str(city).strip("'")
                cities.append(city)
            if conn != None:
                if conn.is_connected():
                    print('MySQLerererererer Connection is established')
                    dbcursor = conn.cursor()
                    print("Testing....")

                    Verify_Query = "SELECT Item_No FROM SetListItem WHERE Item_No = %s;"
                    print("verify Query:  " + Verify_Query)
                    dbcursor.execute(Verify_Query, (itemNo,))
                    rows = dbcursor.fetchall()
                    if dbcursor.rowcount > 0:
                        error = "Item No is already exist. Select unique Item Number, Please.."
                        return render_template("addNewSetsItem.html", error=error, rows=cities)
                    else:
                        dbcursor.execute(INSERT_statement,
                                         (itemNo, description, price))

                        statement = "INSERT INTO set_List(setItemNo , saleItemNo ) VALUES (%s, %s)"
                        for x in items:
                            dbcursor.execute(statement, (itemNo, x))
                        conn.commit()
                        print('You are sucessfully able to Add items.')
                        dbcursor.close()
                        conn.close()
                        gc.collect()
                        session['logged_in'] = True
                        return render_template("addNewSetsItem.html", message='You are successfully able to Add New Set of Items.', rows=cities)
                else:
                    print('Connection error')
                    return render_template("addNewSetsItem.html", error="Unable to add new Set of items", rows=cities)
            else:
                print('Conncetion error')
                return render_template("addNewSetsItem.html", error="Unable to add Set of new items", rows=cities)
        else:
            print('empty parameters')
            return render_template("addNewSetsItem.html", error="Unable to add Set of new item", rows=cities)

    else:
        return render_template("addNewSetsItem.html", error="Unable to add Set of new items", rows=cities)


@app.route('/delete_itemSet', methods=['POST', 'GET'])
def delete_itemSet():
    if request.method == "POST":
        item_id = request.form['id']
        item = item_id
        print(item)
        deleteSetStatement = ("DELETE FROM SetListItem WHERE Item_No = %s;")
        deleteSetListStatement = (
            "DELETE FROM set_List WHERE setItemNo = %s;")
        if item_id != None:
            conn = dbConnection.get_connection()
            if conn != None:
                dbcursor = conn.cursor()
                print('Inside 1')
                print(" i am in here")
                dbcursor.execute(deleteSetListStatement, (item,))
                dbcursor.execute(deleteSetStatement, (item,))
                print("i am in here 2...")
                dbcursor.execute("SELECT * FROM SetListItem")
                rows = dbcursor.fetchall()
                dbcursor.execute("SELECT * FROM set_List")
                sets = dbcursor.fetchall()
                # print(sets)
                dbcursor.close()
                conn.commit()
                conn.close()
                return render_template('setItemAfterLogin.html', rows=rows, sets = sets, message = "Deleted Successfully "+item)
            else:
                print('Connection error')
                return render_template("main.html", error="Server Error Refresh the Page")
        else:
            print('Connection error')
            return render_template("main.html", error="Server Error Refresh the Page")
    else:
        print('Connection error')
        return render_template("main.html", error="Server Error Refresh the Page")


# delete items url
@app.route('/delete_item', methods=['POST', 'GET'])
def delete_item():
    if request.method == "POST":
        item_id = request.form['id']
        item = item_id
        print(item)
        deleteStatement = ("DELETE FROM ItemForSale WHERE Item_No = %s;")
        deleteStatementSetList = "DELETE FROM set_List WHERE saleItemNo = %s;"
        if item_id != None:
            conn = dbConnection.get_connection()
            if conn != None:
                dbcursor = conn.cursor()

                Verify_Query = "SELECT Item_No FROM ItemForSale WHERE Item_No = %s;"
                print("verify Query:  " + Verify_Query)
                dbcursor.execute(Verify_Query, (item,))
                value = dbcursor.fetchone()
                print(value)
                print(value[0])
                if dbcursor.rowcount > 0:
                    print(" i am in here")
                    query = "SELECT setItemNo FROM set_List WHERE saleItemNo = %s;"
                    dbcursor.execute(query, (item,))
                    dbcursor.fetchall()
                    if dbcursor.rowcount > 0:
                        dbcursor.execute(deleteStatementSetList, (item_id,))
                        dbcursor.execute(deleteStatement, (item_id,))
                        print(item_id)
                        print(" i am in here")
                        dbcursor.execute("SELECT * FROM ItemForSale")
                        rows = dbcursor.fetchall()
                        dbcursor.close()
                        conn.commit()
                        conn.close()
                        gc.collect()
                        session['logged_in'] = True
                        # return main()
                        return render_template("main.html", message="Item deleted.", rows=rows)
                    else:
                        dbcursor.execute(deleteStatement, (item_id,))
                        print(item_id)
                        print(" i am in here")
                        dbcursor.execute("SELECT * FROM ItemForSale")
                        rows = dbcursor.fetchall()
                        dbcursor.close()
                        conn.commit()
                        conn.close()
                        gc.collect()
                        session['logged_in'] = True
                        # return main()
                        return render_template("main.html", message="Item deleted.", rows=rows)
                else:
                    return render_template("main.html", error="Items not in Store....")
            else:
                print('Connection error')
                return render_template("main.html", error="Server Error Refresh the Page")
        else:
            print('Connection error')
            return render_template("main.html", error="Server Error Refresh the Page")
    else:
        print('Connection error')
        return render_template("main.html", error="Server Error Refresh the Page")

        # return render_template('main.html')


# update url
@app.route('/update', methods=['POST', 'GET'])
def update():
    if request.method == "POST":
        itemNo = request.form['itemNumber']
        description = request.form['itemName']
        price = request.form['itemPrice']
        shop = request.form['shoeType']
        transferData = [itemNo, description, price, shop]
        return render_template('updateItem.html', data=transferData)


@app.route('/updateItemForm', methods=['POST', 'GET'])
def updateItemForm():
    if request.method == "POST":
        itemNo = request.form['itemNo']
        description = request.form['description']
        price = request.form['price']
        shop = request.form['shop']
        UPDATE_statement = (
            "UPDATE ItemForSale SET Description = %s, Price = %s, ShopType=%s WHERE Item_No = %s")
        if itemNo != None and description != None and price != None and shop != None:
            conn = dbConnection.get_connection()
            if conn != None:
                if conn.is_connected():
                    dbcursor = conn.cursor()
                    dbcursor.execute(UPDATE_statement,
                                     (description, price, shop, itemNo))
                    dbcursor.execute("SELECT * FROM ItemForSale")
                    rows = dbcursor.fetchall()
                    conn.commit()
                    print('You are sucessfully able to Update items.')
                    dbcursor.close()
                    conn.close()
                    gc.collect()
                    session['logged_in'] = True
                    return render_template("main.html", message='You are successfully able to Update Item ' + itemNo, rows=rows)
                else:
                    print('Connection error')
                    return render_template("updateItem.html", error="Unable to Update new items")
            else:
                print('Conncetion error')
                return render_template("updateItem.html", error="Unable to Update new items")
        else:
            print('empty parameters')
            return render_template("updateItem.html", error="Unable to Update new item")
    else:
        return render_template("updateItem.html", error="Unable to Update new items")


@app.route('/addNewItem')
def addNewItem():
    return render_template('addNewItem.html')


@app.route('/addNewItemForm', methods=['POST', 'GET'])
def adminaddNewAdmin():
    if request.method == "POST":
        itemNo = request.form['itemNo']
        description = request.form['description']
        price = request.form['price']
        shop = request.form['shop']
        print(shop)
        INSERT_statement = (
            "INSERT INTO ItemForSale (Item_No, Description, Price, ShopType) VALUES (%s, %s, %s, %s);")
        if shop == "ShopA" or shop == "ShopB":
            if itemNo != None and description != None and price != None:
                conn = dbConnection.get_connection()
                if conn != None:
                    if conn.is_connected():
                        print('MySQLerererererer Connection is established')
                        dbcursor = conn.cursor()
                        print("Testing....")

                        Verify_Query = "SELECT Item_No FROM ItemForSale WHERE Item_No = %s;"
                        print("verify Query:  " + Verify_Query)
                        dbcursor.execute(Verify_Query, (itemNo,))
                        rows = dbcursor.fetchall()
                        if dbcursor.rowcount > 0:
                            error = "Item No is already exist. Select unique Item Number, Please.."
                            return render_template("addNewItem.html", error=error)
                        else:
                            dbcursor.execute(
                                INSERT_statement, (itemNo, description, price, shop))
                            conn.commit()
                            print('You are sucessfully able to Add items.')
                            dbcursor.close()
                            conn.close()
                            gc.collect()
                            session['logged_in'] = True
                            return render_template("addNewItem.html", message='You are successfully able to Add New Items ...')
                    else:
                        print('Connection error')
                        return render_template("addNewItem.html", error="Unable to add new items")
                else:
                    print('Conncetion error')
                    return render_template("addNewItem.html", error="Unable to add new items")
            else:
                print('empty parameters')
                return render_template("addNewItem.html", error="Unable to add new item")
        else:
            return render_template("addNewItem.html", error="Unable to add new items Please Select Shop")
    else:
        return render_template("addNewItem.html", error="Unable to add new items")


@app.route('/')
@app.route('/index')
def index():
    conn = dbConnection.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ItemForSale")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', rows=rows)


@app.route('/setItems')
def setItems():
    conn = dbConnection.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM SetListItem")
    rows = cursor.fetchall()
    cursor.execute("SELECT * FROM set_List")
    sets = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('setItems.html', rows=rows, sets=sets)


@app.route('/setItemAfterLogin')
def setItemAfterLogin():
    conn = dbConnection.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM SetListItem")
    rows = cursor.fetchall()
    cursor.execute("SELECT * FROM set_List")
    sets = cursor.fetchall()
    print(sets)
    cursor.close()
    conn.close()
    return render_template('setItemAfterLogin.html', rows=rows, sets=sets)


@app.route('/main')
def main():
    conn = dbConnection.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ItemForSale")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("main.html", rows=rows)
    # return render_template('main.html')


@app.route('/privacyAndPolicy')
def privacyAndPolicy():
    return render_template('privacyAndPolicy.html')


@app.route('/termAndCondition')
def termAndCondition():
    return render_template('termAndCondition.html')

# sign in url for html page


@app.route('/signIn')
def signIn():
    return render_template('signIn.html')

# login url


@app.route('/login', methods=["GET", "POST"])
def login():
    form = {}
    error = ''
    try:
        if request.method == "POST":
            username = request.form['username']
            password = request.form['password']
            print('login start ')
            # verifyLogIn(username, password)
            form = request.form
            if username != None and password != None:
                conn = dbConnection.get_connection()
                if conn != None:
                    if conn.is_connected():
                        print('MySQL Connection is established')
                        dbcursor = conn.cursor()
                        dbcursor.execute("SELECT Password, UserType\
                                FROM User_Table WHERE UserName= %s;", (username,))
                        print("username " + username)
                        data = dbcursor.fetchone()
                        if dbcursor.rowcount < 1:
                            error = "username and password does not exist, Login again"
                            return render_template("signIn.html", error=error)
                        else:
                            if sha256_crypt.verify(request.form['password'], str(data[0])):
                                session['logged_in'] = True
                                session['username'] = request.form['username']
                                session['usertype'] = str(data[1])
                                print("You are now logged in")
                                # conn = get_connection()
                                # cursor = conn.cursor()
                                dbcursor.execute("SELECT * FROM ItemForSale")
                                rows = dbcursor.fetchall()
                                print(rows[1])
                                if session['usertype'] == 'Standard':
                                    print(rows[1])
                                    print("user Standard")
                                    message = "Welcome Your are successfully LogIn " + username + ", Thank You..."
                                    return render_template("main.html", rows=rows, username=username,
                                                           data='this is user specific data',  usertype=session['usertype'], message=message)
                                    # return render_template("404.html")
                                else:
                                    message = "Welcome Your are successfully LogIn as Admin " + \
                                        username + ", Thank You..."
                                    return render_template("main.html", rows=rows, user=username,
                                                           data='this is user specific data',  usertype=session['usertype'], message=message)

                            else:
                                error = "Invalid username and password , Try again."
                                print("this one may br")
                                return render_template("401.html", error=error)
                    gc.collect()
                    print('login start verison 2.0 ')
                    error = "Invalid username and password , Try again."
                    return render_template("signIn.html", form=form, error=error)
    except Exception as e:
        error = str(e) + "<br/> Invalid credentials, try agin."
        print('here........')
        print(error)
        return render_template("404.html", form=form, error=error)
    return render_template("signIn.html", form=form, error=error)


@app.route('/signUp')
def signUp():
    return render_template('signUp.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    error = ''
    print('Register start')
    try:
        if request.method == "POST":
            firstname = request.form['firstname']
            if(len(firstname) < 3):
                    return render_template("signUp.html", error='User Correct First Name Please...')
        
            lastname = request.form['lastname']
            if(len(lastname) < 3):
                    return render_template("signUp.html", error='User Correct Last Name Please...')
            username = request.form['username']
            if(len(lastname) < 5):
                return render_template("signUp.html", error='User Correct UserName Please...')
            email = request.form['email']
            if(not Email(email)):
                return render_template("signUp.html", error='User Correct Email Please...')
            password = request.form['password']
            if(len(password) < 8):
                    return render_template("signUp.html", error='Password Must Be more than 8 character Please...')
            elif(not Password(password)):
                return render_template("signUp.html", error='Password Must Be strong u one special charater and number than 8 character Please...')
                
            if firstname != None and lastname != None and username != None and email != None and password != None:
                conn = dbConnection.get_connection()
                if conn != None:
                    if conn.is_connected():
                        print('MySQLerererererer Connection is established')
                        dbcursor = conn.cursor()
                        password = sha256_crypt.hash((str(password)))
                        print("Testing....")
                        Verify_Query = "SELECT * FROM User_Table WHERE UserName = %s;"
                        print("verify Query:  " + Verify_Query)
                        dbcursor.execute(Verify_Query, (username,))
                        rows = dbcursor.fetchall()
                        if dbcursor.rowcount > 0:
                            print('username already taken, Please choose another')
                            error = "User name already taken, Please choose another"
                            return render_template("signUp.html", error=error)
                        else:
                            dbcursor.execute("INSERT INTO User_Table (FirstName, LastName, UserName, Email, Password) VALUES (%s, %s, %s, %s, %s)", (
                                firstname, lastname, username, email, password))
                            conn.commit()
                            print('Thanks for registering')
                            dbcursor.close()
                            conn.close()
                            gc.collect()
                            session['logged_in'] = True
                            session['username'] = username
                            session['usertype'] = 'standard'
                            return render_template("signIn.html", message='User registered successfully ...')
                    else:
                        print('Connection error')
                        return 'Db connection Error'
                else:
                    print('Conncetion error')
                    return 'DB connection Error'
            else:
                print('empty parameters')
                return render_template("signUp.html", error=error)
        else:
            return render_template("signUp.html", error=error)
    except Exception as e:
        return render_template("signIn.html", error=e)
    # return render_template("signUp.html", error=error)

# Forget password url


@app.route('/forgetPasswordForm')
def forgetPasswordForm():
    return render_template("forgetPassword.html")


@app.route('/forgetPassword', methods=['POST', 'GET'])
def forgetPassword():
    if request.method == "POST":
        userName = request.form['userName']
        # oldPassword = request.form['oldPassword']
        # oldpassword = sha256_crypt.encrypt((str(oldPassword)))
        newPassword = request.form['newPassword']
        if(len(newPassword) < 8):
                    return render_template("forgetPassword.html", error='Password Must Be more than 8 character Please...')
        # elif(not Password(password)):
        #         return render_template("forgetPassword.html", error='Password Must Be strong u one special charater and number than 8 character Please...')
        confirmPassword = request.form['confirmPassword']
        conn = dbConnection.get_connection()
        cursor = conn.cursor()
        Verify_Query = "SELECT Password FROM User_Table WHERE UserName =%s;"
        # cursor.execute("SELECT Password FROM User_Table WHERE UserName =%s;")
        cursor.execute(Verify_Query, (userName,))
        rows = cursor.fetchone()
        # print(rows[0])
        # oldpassword = sha256_crypt.encrypt((str(rows[0])))
        # print(oldpassword)

        # if(oldpassword == rows):
        if newPassword == confirmPassword:
            if userName != None and  newPassword != None and confirmPassword != None:
                if conn != None:
                    if conn.is_connected():
                        print('MySQLerererererer Connection is established')
                        # dbcursor = conn.cursor()
                        INSERT_statement = (
                            "UPDATE User_Table SET Password = %s WHERE UserName = %s;")
                        password = sha256_crypt.hash((str(newPassword)))
                        print("Testing....")
                        cursor.execute(INSERT_statement, (password, userName))
                        conn.commit()
                        print('you have been sucessfully change the password')
                        cursor.close()
                        conn.close()
                        gc.collect()
                        return render_template("signIn.html", message='You are successfully able to change the Password.')
                    else:
                        print('Connection error')
                        return render_template("forgetPassword.html", message="Db connection Error.")
                else:
                    print('Conncetion error')
                    return render_template("forgetPassword.html", message="Db connection Error.")
            else:
                return render_template("forgetPassword.html", message="Please fill all the form.")

        else:
            return render_template("forgetPassword.html", message="Your New Password is not same.")
        # else:
        #     return render_template("forgetPassword.html", message = "Your Old Password is incorrect.")

    else:
        return render_template("forgetPassword.html", message="Server Post Error")


# log in required to check it is log in or not
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            print("You need to login first")
            return render_template('401.html', error='You need to login first')
    return wrap


@app.route("/logout")
# @login_required
def logout():
    session.clear()
    print("You have been logged out!")
    gc.collect()
    message = "Your are successfully logout , Thank You..."
    # flash('You are successfully log out from the page. Thank you....')
    conn = dbConnection.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ItemForSale")
    rows = cursor.fetchall()
    return render_template('index.html', rows=rows, message=message)
    # return render_template('index.html')


if __name__ == '__main__':
    for i in range(13000, 18000):
        try:
            app.run(debug=True, port=i)
            break
        except OSError as e:
            print("Port {i} not available".format(i))
