'''
Defines helper functions used in API calls using pyodbc (for database connections)
and SQL prepared statements
'''
import datetime
# //TODO: 1. add courseCode update/set 2. refactor tests to use ints instead of floats
import pyodbc

# connection information can change as we include security
# PROD CONNECTION STRING
conn = (r'Driver=ODBC Driver 17 for SQL Server;'
         r'Server=localhost;'
         r'Database=StudyBuddy;'
         r'UID=sa;'
         r'PWD=dbtools.IO'
         )
# DEV CONNECTION STRING - D.N.T
'''conn = (r'Driver=SQL Server;'
        r'Server=(local);'
        r'Database=StudyBuddy;'
        r'Trusted_Connection=yes'
        )'''
cnxn = pyodbc.connect(conn)
cursor = cnxn.cursor()


'''
METHOD: getUserData(): Debugging method used in tests to make sure that database contains the stub user data
'''
def getUserData():
    return cursor.execute("SELECT * FROM Users;").fetchall()

'''
METHOD: getClassesData(): Debugging method used in tests to make sure that database contains the stub class data
'''
def getClassesData():
    return cursor.execute("SELECT * FROM Classes;").fetchall()


'''
METHOD: getUser():
PRECONDITION: passed string <username> which will be used to find the user in the db
POSTCONDITION: 
- if the user with <username> exists in the database, return their information (form of record)
- Otherwise, None is returned
'''
def getUser(name):
    result = cursor.execute("SELECT * FROM Users WHERE username = ?", name).fetchone()
    if not result:
        return None
    return result


'''
METHOD: createAccount():
PRECONDITION: account creation requested, need to add a new entry to users table
POSTCONDITION: 
- account has been created and added to users table with given information
'''


def createAccount(username, password):
    # cursor.execute("INSERT INTO Users (username, password) VALUES (?, ?)",username, password)
    prep_stmt = "INSERT INTO Users (username, password) VALUES (?,?);"
    cursor.execute(prep_stmt, username, password)


''' 
METHODD: removeUser():
PRECONDITION: all users are present in the db
POSTCONDITION: 
- user with 'username' has been removed from the db
- if user is not in db, msg returned
'''


def removeUser(username):
    # check that user is in db
    user = getUser(username)
    if user is None:
        return "User " + username + " is not in database and cannot be removed"
    cursor.execute("DELETE FROM Users WHERE username = ?;", username)


'''
METHOD: getAllUsers():
PRECONDITION: no users have been retrieved
POSTCONDITION: 
- record of all users returned
- or None if there are no users
'''


def getAllUsers():
    record = cursor.execute("SELECT * FROM Users;").fetchall()
    if not record:
        return None
    return record


# Class Methods
'''
METHOD:getClasses():
PRECONDITION: no classes have been retrieved from db
POSTCONDITION: 
 - If user exists, and record is not empty, all classes for user 'username' have been retrieved (if the class is uncomplete)
 - Otherwise,  None if user has no classes
'''


def getClasses(username):
    user = getUser(username)
    if not user:
        return None
    # get user id
    userID = user.uID
    record = cursor.execute("SELECT * FROM Classes WHERE FK_uID = ? AND is_complete = 0;", userID).fetchall()
    if not userID or not record:
        return None
    return record


'''
METHOD: getClassID():
PRECONDITION: class id for individuals unknown
POSTCONDITION: returns classID for specified user and specified class, or None if no class exists
'''


def getClassID(username, className):
    user = getUser(username)
    if not user:
        return None
    userID = user.uID
    # print("getting", userID, className)
    record = cursor.execute("SELECT cID FROM Classes WHERE FK_uID = ? AND class_Name =?;", userID, className).fetchone()
    # print("got: ", type(record))
    if not userID or not record:
        return None
    return record.cID


'''
METHOD: getSingleClass():
PRECONDITION: no classes retrieved
POSTCONDITION: 
- If user, class present in db, a single class is returned when given username and class id
- Otherwise, None returned
'''


def getSingleClass(username, className):
    user = getUser(username)
    if not user:
        return None
    userID = user.uID
    classID = getClassID(username, className)
    # print("extra: ", userID, classID)
    if not userID or not classID:
        # print(1)
        return None
    record = cursor.execute("SELECT * FROM Classes WHERE FK_uID = ? AND cID = ?;", userID, classID).fetchone()
    if not record:
        # print(2)
        return None
    # print("good")
    return record


'''
METHOD: addClass():
PRECONDITION: no classes have been added 
POSTCONDITION: 
-  If user present in db, specified class for specified user is added to the db and record is returned
- Otherwise, None is returned
'''


def addClass(username, className, timeslot,cc):
    prep_stmt = "INSERT INTO Classes (class_Name, timeslot,courseCode, FK_uID, is_complete) VALUES (?,?,?,?,?);"
    user = getUser(username)
    if not user:
        return None
    id = user.uID
    if not id:
        return None
    return cursor.execute(prep_stmt, className, timeslot,cc, id, 0)


'''
METHOD: removeClass():
PRECONDITION: all classes are present in db
POSTCONDITION: 
- If class, user in db, specified class removed for specified user
- Otherwise, None returned
'''


def removeClass(username, className):
    user = getUser(username)
    if not user:
        return None
    id = user.uID
    classID = getClassID(username, className)
    if not id or not classID:
        return None
    else:
        record = cursor.execute("DELETE FROM Classes WHERE FK_uID = ? AND cID = ?;", id, classID)
        if not record:
            return None
        return record


'''
METHOD: completeClass():
PRECONDITION: all classes marked uncomplete
POSTCONDITION: 
- If class, user in db, specified class marked complete, but not removed from db
- Otherwise, None is returned
'''


def completeClass(username, className):
    user = getUser(username)
    if not user:
        return None
    userID = user.uID
    classID = getClassID(username, className)

    prep_stmt = "UPDATE Classes SET is_complete = ? WHERE cID = ? AND FK_uID = ?;"
    if not classID:
        return None
    record = cursor.execute(prep_stmt, 1, classID, userID)
    return record
'''
METHOD: addClassBreakdown()
PRECONDITION: specified class with specified user either has no breakdown or breakdown is unchanged
POSTCONDITION: breakdown for specified class is updated using breakdown value
'''
def addClassBreakdown(username, className, breakdown):
    user = getUser(username)
    if not user:
        return None
    userID = user.uID
    classID = getClassID(username,className)
    if not userID or not classID:
        return None
    cursor.execute("UPDATE Classes SET breakdown = ? WHERE cID = ? AND FK_uID = ?;", breakdown, classID, userID)

'''
METHOD: editClassReqData
PRECONDITION: required class data 'className' and 'timeslot' are unchanged
POSTCONDITION: 'className' and/or 'timeslot' changed for given class and user
'''
def editClassReqData(username, className_old,className_new, timeslot_new):
    user = getUser(username)
    classID = getClassID(username, className_old)
    if not user:
        return None
    userID = user.uID
    if not userID or not classID:
        return None
    if not className_new == "":
        cursor.execute("UPDATE Classes SET class_Name = ? WHERE cID = ? AND FK_uID = ?;", className_new, classID, userID)
    if not timeslot_new == "":
        cursor.execute("UPDATE Classes SET timeslot = ? WHERE cID = ? AND FK_uID = ?;", timeslot_new, classID, userID)

'''
METHOD: editClassMeta()
PRECONDITION: class data remains unchanged
POSTCONDITION: 
- If user and class present in db, class data for specified class and user updated using specified information
- Otherwise, None returned
'''
def editClassMeta(username, className, sectionnum, classroom, prof,
                  prof_email, prof_phone, prof_office, prof_hours):
    user = getUser(username)
    if not user:
        return None
    userID = user.uID
    classID = getClassID(username, className)
    if not userID or not classID:
        return None
        # update doesnt return a record
    cursor.execute("UPDATE Classes SET section = ? WHERE FK_uID = ? AND cID = ?", sectionnum, userID, classID)
    cursor.execute("UPDATE Classes SET classroom = ? WHERE FK_uID = ? AND cID = ?", classroom, userID, classID)
    cursor.execute("UPDATE Classes SET prof_Name = ? WHERE FK_uID = ? AND cID = ?", prof, userID, classID)
    cursor.execute("UPDATE Classes SET prof_Email = ? WHERE FK_uID = ? AND cID = ?", prof_email, userID, classID)
    cursor.execute("UPDATE Classes SET prof_Phone = ? WHERE FK_uID = ? AND cID = ?", prof_phone, userID, classID)
    cursor.execute("UPDATE Classes SET prof_Office = ? WHERE FK_uID = ? AND cID = ?", prof_office, userID, classID)
    cursor.execute("UPDATE Classes SET prof_Hours = ? WHERE FK_uID = ? AND cID = ?", prof_hours, userID, classID)


'''
METHOD: addStudyTime()
PRECONDITION: the total study time for the class is unchanged
POSTCONDITION: 
- If class present in db, total study time for the specified class for the specified user has been updated with time studied
- Otherwise, None returned
'''
def addStudyTime(username, className, t):
    user = getUser(username)
    if not user:
        return None
    userID = user.uID
    record = getSingleClass(username, className)
    # print(username, " ", className)
    if not userID or not record:
        return None
    else:
        classID = record.cID
        study = record.studyTime
        uTime = study + float(t)
        prep_stmt = "UPDATE Classes SET studyTime = ? WHERE FK_uID = ? AND cID = ?;"
        result = cursor.execute(prep_stmt, uTime, userID, classID)
        if not result:
            return None
        return result


''''
METHOD: getTaskList()
PRECONDITION: no tasks have been retrieved
POSTCONDITION: 
-If user and class are present in db, the list of tasks per class is retrieved.
-Otherwise, either user or class or both isnt present in db and None is returned
'''
def getTaskList(username, className):
    user = getUser(username)
    if not user:
        return None
    userID = user.uID
    classID = getClassID(username, className)
    if not userID or not classID:
        return None
    else:
        record = cursor.execute("SELECT * FROM Tasks WHERE FK_uID = ? AND FK_cID = ?", userID, classID).fetchall()
        if not record:
            return None
        return record

'''
METHOD: getSingleTask()
PRECONDITION: no tasks retrieved from db
POSTCONDITION: 
- If specified task present in db, its returned. 
- Otherwise, task is not in db and None is returned
'''
def getSingleTask(username, className, taskName):
    user = getUser(username)
    if not user:
        return None
    userID = user.uID
    classID = getClassID(username, className)
    if not userID or not classID:
        return None
    record = cursor.execute("SELECT * FROM Tasks WHERE task_Name = ? AND FK_uID = ? AND FK_cID = ?", taskName, userID,
                            classID).fetchone()
    return record


''''
METHOD: getTaskID()
PRECONDITION: no taskID has been retrieved
POSTCONDITION: 
- If task is in db, taskID for specified [user,class, name] retrieved. 
- Otherwise, None returned
'''
def getTaskID(username, className, taskName):
    user = getUser(username)
    if not user:
        return None
    userID = user.uID
    classID = getClassID(username, className)
    if not userID or not classID:
        return None
    else:
        record = cursor.execute("SELECT * FROM Tasks WHERE FK_uID = ? AND FK_cID = ? AND task_Name = ?", userID,
                                classID,
                                taskName).fetchone()
        if not record:
            return None
        return record
''''
METHOD: completeTask()
PRECONDITION: no tasks have been completed
POSTCONDITION: 
- If task, user, class in db, specifed task has been marked as complete. 
- Otherwise,  no record is present in db and None is returned
'''
def completeTask(username, className, taskName, grade):
    task = getSingleTask(username, className, taskName)
    if task is None:
        return None
    taskID = task.tID
    user = getUser(username)
    if not user:
        return None
    userID = user.uID
    cls = getSingleClass(username, className)
    if not cls:
        return None
    classID = cls.cID
    if not taskID or not userID or not classID:
        return None
    cursor.execute("UPDATE Tasks SET task_grade = ? WHERE FK_uID = ? AND FK_cID = ? AND tID = ?", grade, userID,
                   classID, taskID)
    return True

''''
METHOD: uncompleteTask()
PRECONDITION: task was previously marked complete (grade was entered)
POSTCONDITION: 
- If specifed task is present in db, task marked uncomplete (grade set to 0).
- Otherwise, None is returned
'''
def uncompleteTask(username, className, taskName):
    taskID = getTaskID(username, className, taskName).tID
    user = getUser(username)
    if not user:
        return None
    userID = user.uID
    classID = getClassID(username, className)
    if not taskID or not userID or not classID:
        return None
    cursor.execute("UPDATE Tasks SET task_grade = ? WHERE FK_uID = ? AND FK_cID = ? AND tID = ?", 0.0, userID,
                   classID, taskID)

''''
METHOD: getCompleteTasksForClass()
PRECONDITION: a user has some completed tasks for class <className> in the database
POSTCONDITION: 
- If user and class in db, all completed tasks for the specified user and class have been returned
- Otherwise, None is returned
'''
def getCompleteTasksForClass(username, className):
    user = getUser(username)
    if not user:
        return None
    userID = user.uID
    classID = getClassID(username, className)
    if not userID or not classID:
        return None
    record = cursor.execute("SELECT * FROM Tasks WHERE task_grade > 0.0 AND FK_uID = ? AND FK_cID = ?;", userID,
                            classID).fetchall()
    if not record:
        return None
    return record


'''
METHOD: addTask()
PRECONDITION: no tasks have been added to db
--> required: name and task weight
POSTCONDITION: 
- If user and class both present in db, task with given information added to db for specified user and class
- Otherwise, None is returned
'''
def addTask(username, className, taskName, weight, deadline,goal):
    user = getUser(username)
    if not user:
        return None
    userID = user.uID
    classID = getClassID(username, className)
    if not userID or not classID:
        return None
    if goal is None:
        prep_stmt = "INSERT INTO Tasks (task_Name, deadline, task_Weight, FK_uID, FK_cID) VALUES (?,?,?,?,?);"
        return cursor.execute(prep_stmt, taskName, deadline, weight, userID, classID)
    else:
        prep_stmt = "INSERT INTO Tasks (task_Name, deadline, task_Weight,task_goal, FK_uID, FK_cID) VALUES (?,?,?,?,?,?);"
        return cursor.execute(prep_stmt, taskName, deadline, weight,goal, userID, classID)

'''
METHOD: removeTask()
PRECONDITION: all tasks present in the db
POSTCONDITION: 
- If task, user, class present in db, task with specified [user, class, name] removed from db
- Otherwise, None is returned
'''
def removeTask(username, className, taskName):
    user = getUser(username)
    if not user:
        return None
    userID = user.uID
    classID = getClassID(username, className)
    taskID = getTaskID(username, className, taskName).tID
    if not userID or not classID or not taskID:
        return None
    prep_stmt = "DELETE FROM Tasks WHERE tID = ? AND FK_uID = ? AND FK_cID = ?;"
    cursor.execute(prep_stmt, taskID, userID, classID)

'''
METHOD: editTask
PRECONDITION: all tasks remain unchanged
POSTCONDITION: 
- If task, user, class present in db, task with specified [user, class, name] edited based on specified attributes
- Otherwise, None is returned and task remains unchanged
- ** make sure that eDate is passed in as a datetime object or converted
'''
def editTask (username, className, taskName, eName, eDate, eWeight,eGoal):
    user = getUser(username)
    if not user:
        return None
    userID = user.uID
    cls = getSingleClass(username, className)
    if not cls:
        return None
    classID = cls.cID
    task = getSingleTask(username, className, taskName)
    if not task:
        return None
    taskID = task.tID
    if not userID or not classID or not taskID:
        return None
    if eName != "":
        cursor.execute("UPDATE Tasks SET task_Name = ? WHERE tID = ? AND FK_uID = ? AND FK_cID = ?;", eName,taskID, userID, classID )
    if eDate != "":
        cursor.execute("UPDATE Tasks SET deadline = ? WHERE tID = ? AND FK_uID = ? AND FK_cID = ?;", eDate, taskID,
                       userID, classID)
    if eWeight != 0:
        cursor.execute("UPDATE Tasks SET task_Weight = ? WHERE tID = ? AND FK_uID = ? AND FK_cID = ?;", eWeight, taskID,
                       userID, classID)
    if eGoal !='' or eGoal is not None:
        cursor.execute("UPDATE Tasks SET task_goal = ? WHERE tID = ? AND FK_uID = ? AND FK_cID = ?;", eGoal, taskID,
                       userID, classID)


'''
METHOD: getDeadlines()
PRECONDITION: no task deadlines have been retrieved
POSTCONDITION:
- if user present, retrieve top 5 task deadlines from database for that user
- else, return None (user doesnt exist)
'''
def getDeadlines(username):
    user = getUser(username)
    if not user:
        return None
    userID = user.uID
    if not userID:
        return None
    prep_stmt = "SELECT TOP 5 Tasks.task_Name, Tasks.deadline FROM Tasks INNER JOIN Classes ON Tasks.FK_cID=Classes.cID WHERE Tasks.FK_uID = ? ORDER BY Tasks.deadline DESC;"
    record = cursor.execute(prep_stmt, userID).fetchall()
    return record

