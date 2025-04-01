import logging
from fastapi import FastAPI

app = FastAPI(title='AI Story Automation Tool')

@app.get('/')
def root():
    return {'message': 'Welcome to AI Story Automation Tool'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)