from fastapi import FastAPI
from fastapi import HTTPException
import pymysql
import bcrypt
import random

app = FastAPI()


# 使用 FastAPI 的用户认证系统

# 数据库连接配置
def get_database_connection():
    # 是一个函数，它的作用是建立和 MySQL 数据库的连接
    # get_database_connection() 是定义的一个 函数，它的目的是为了封装 pymysql.connect() 的逻辑
    connection = pymysql.connect(  # 当调用get_db_connection()时，这个函数内部会使用pymysql.connect(...)方法去连接数据库
        host='localhost',
        user='root',
        password='DB_PASSWORD',
        database='fastapi_auth_project'
    )
    return connection


@app.post("/register")  # 定义API端点
# 客户端发送 POST 请求到"/register"的时候，服务器会调用这个函数
def register_user(email: str, password: str):
    # 定义函数，该函数接受两个信息，邮箱和密码
    # 当用户通过 /register 路由发送请求时，函数会提取请求中的 email 和 password 并使用它们进行注册
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # 加密密码，首先将用户输入的密码编码为 UTF-8 字符串，因为 bcrypt 只接受字节格式的数据
    # bcrypt.gensalt()：生成一个随机的盐值（salt）用于加密，这个盐值增加了哈希的随机性，使得即使两个用户使用相同的密码，生成的哈希值也会不同
    # bcrypt.hashpw()对最终结果进行加密处理
    # 获取数据库连接
    connection_outside = get_database_connection()
    cursor = connection_outside.cursor()
    # 创建一个 游标（cursor） 对象，用于在数据库中执行 SQL 查询

    # 户注册功能中的核心逻辑，负责将用户数据插入数据库中。
    try:
        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
        # .execute() 是游标对象的一个方法，用来执行 SQL 语句。SQL 语句 是用来与数据库交互的指令，类似于向数据库发出命令
        # 向users数据库表中加入用户邮件和加密后密码
        # %s 是占位符，表示"这里要放一个值，邮箱和密码两个值
        connection_outside.commit()
        # 保存当前改动
    except Exception as e:
        # 如果在插入数据的过程中出现错误，就会进入 except 部分
        # 这里的 Exception 是一种通用的异常类型，表示程序运行过程中可能会发生的大部分错误
        # as e 的意思是，将这个捕获到的异常保存到变量 e 中，以便可以访问到错误的信息
        return {"error": str(e)}
        # 如果在 try 块中发生了错误，程序会返回一个包含错误信息的字典 {"error": str(e)}
    finally:
        cursor.close()
        connection_outside.close()

    return {"message": f"User {email} registered successfully"}


@app.post("/login")
# 客户端发送 POST 请求到"/login"的时候，服务器会调用这个函数
def login_user(email: str, password: str):
    connection = get_database_connection()
    cursor = connection.cursor()

    try:
        # 查询用户信息
        cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
        # 用邮箱在数据库中查找用户，获取该用户的密码，后续可以用这个密码来验证用户登录
        # %s是一个占位符，对应后面(email,)需要填写的邮件信息
        user = cursor.fetchone()
        # 如果找到了符合条件的用户，fetchone() 会返回这个用户的一行数据（在这里是查询到的密码）
        # 如果没有找到，它会返回 None
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
            # raise HTTPException 本身是一个 标准的用法，为一个固定表达式，因为它是抛出 HTTP 错误的常见方式
            # status_code=404 这是 HTTP 状态码，用来描述错误类型

        stored_hashed_password = user[0]
        # 从返回的user元组中，提取出第一个元素，也就是加密后的密码

        # 检查用户输入的密码是否匹配
        if not bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
            raise HTTPException(status_code=401, detail="Wrong password")
            # 如果密码不匹配，我们通过 raise 语句来引发一个异常
            # 它会引发一个 HTTPException，返回给客户端一个 401 状态码和一个说明错误原因的详细信息 "Incorrect password"
    finally:
        cursor.close()
        connection.close()

    return {"message": f"User {email} logged in successfully"}
    # 键（key）："message" 表示我们要返回的内容类型。
    # 值（value）："User user@example.com logged in successfully" 是具体的信息内容


verification_codes = {}


# 定义一个验证码字典，

@app.post("/register_with_verification")
# 客户端发送 POST 请求到"/register_with_verification"的时候，服务器会调用这个函数
def register_with_verification(email: str, password: str):
    verification_code = random.randint(100000, 999999)
    # 生成随机验证码
    verification_codes[email] = verification_code
    # 通过方括号 [] 指定字典中的一个键（email）。如果字典中没有这个键，就会添加一个键值对；如果已经存在，就会更新这个键对应的值
    # 在verification_codes字典中，email是键，verification_code是值，方括号 [] 用于将这个验证码存储到对应的邮箱

    print(f"Verification code for {email}: {verification_code}")

    return {"message": f"Verification code sent to {email}"}


@app.post("/verify_email")
# 客户端发送 POST 请求到 "/verify_email" 的时候，服务器会调用这个函数
def verify_email(email: str, code: int):
    if verification_codes.get(email) == code:
        # .get(email)：从字典中获取对应邮箱的验证码
        return {"message": f"Email {email} verified successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid verification code")