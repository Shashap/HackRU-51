# Steps:
1. Make sure you have pip installed
2. Open terminal in project main folder
3. Install all dependencies of the project using the command: pip install -r requirements.txt
4. Load the web-app using the command: uvicorn main:app --reload ,and you will find in the terminal a link to the web-app
5. If step number 4 brings an error, maybe your path to uvicorn is not set. Try to give full path to the uvicorn module as the following example: C:\Python39\Scripts\uvicorn main:app --reload 
6. Enjoy! (searches might be a little slow, but it's worth it in the end)
