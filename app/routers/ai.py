from fastapi import FastAPI, File, Path, UploadFile, HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from pydantic import BaseModel
import aiohttp
import os
from typing import List

from app.database import get_session
from app.config import config
from sqlalchemy.sql import text

from app.routers.shape_func import ShapeGet, ShapeService

API_KEY = 'sec_AIPPRiqPmLPTsC6AobETncNoTlbHg4OA'
UPLOAD_URL = 'https://api.chatpdf.com/v1/sources/add-file'
CHAT_URL = 'https://api.chatpdf.com/v1/chats/message'
DELETE_URL = 'https://api.chatpdf.com/v1/sources/delete'

router = APIRouter(prefix=config.BACKEND_PREFIX)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    sourceId: str = 'cha_uAPqOGzFSqbrUuCebnq8i'
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    content: str

class UploadResponse(BaseModel):
    sourceId: str

class DeleteRequest(BaseModel):
    sourceId: str

class DeleteResponse(BaseModel):
    detail: str

async def save_message(session: AsyncSession, sourceId: str, message: ChatMessage):
    await session.execute(
        text(f"INSERT INTO chat_messages (source_id, role, content) VALUES ('{sourceId}', '{message.role}', '{message.content}')")
    )
    await session.commit()

async def get_messages(session: AsyncSession, sourceId: str):
    result = await session.execute(
        text(f"SELECT * FROM chat_messages WHERE chat_messages.source_id = '{sourceId}' ORDER BY chat_messages.id ASC")
    )
    return result.fetchall()

@router.post("/ai/chat/upload_pdf", response_description="Успешная загрузка PDF-файла и получение его sourceId",
             response_model=UploadResponse,
             status_code=status.HTTP_200_OK,
             description="Загрузить PDF-файл и получить его sourceId",
             summary="Загрузка PDF-файла и получение его sourceId")
async def upload_pdf(file: UploadFile = File(...)):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            UPLOAD_URL,
            headers={'x-api-key': API_KEY},
            data={'file': file.file}
        ) as response:
            if response.status == 200:
                result = await response.json()
                return JSONResponse(content={"sourceId": result['sourceId']})
            else:
                error = await response.text()
                raise HTTPException(status_code=response.status, detail=error)

@router.post("/ai/chat/delete_pdf", 
             response_description="Успешное удаление PDF-файла",
             status_code=status.HTTP_200_OK,
             response_model=DeleteResponse,
             description="Удалить PDF-файл по его sourceId",
             summary="Удаление PDF-файла")
async def delete_pdf(request: DeleteRequest):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            DELETE_URL,
            headers={'x-api-key': API_KEY},
            json={"sources": [request.sourceId]}
        ) as response:
            if response.status == 200:
                return JSONResponse(content={"detail": "Файл успешно удален"})
            else:
                error = await response.text()
                raise HTTPException(status_code=response.status, detail=error)

@router.post("/ai/chat/chat_with_pdf", response_model=ChatResponse,
             response_description="Успешное получение помощи по файлу",
             status_code=status.HTTP_200_OK,
             description="Получить помощь по файлу",
             summary="Общение с файлом")
async def chat_with_pdf(request: ChatRequest, session: AsyncSession = Depends(get_session)):
    async with aiohttp.ClientSession() as http_session:
        async with http_session.post(
            CHAT_URL,
            headers={'x-api-key': API_KEY},
            json={
                "sourceId": request.sourceId,
                "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages]
            }
        ) as response:
            if response.status == 200:
                result = await response.json()
                # Сохраняем сообщения в базу данных
                for message in request.messages:
                    await save_message(session, request.sourceId, message)
                await save_message(session, request.sourceId, ChatMessage(role="assistant", content=result['content']))
                return JSONResponse(content={"content": result['content']})
            else:
                error = await response.text()
                raise HTTPException(status_code=response.status, detail=error)

@router.get("/ai/chat/get_messages", response_model=List[ChatMessage],
            response_description="Успешное получение списка сообщений",
            status_code=status.HTTP_200_OK,
            description="Получить список сообщений по sourceId",
            summary="Получение списка сообщений")
async def get_messages_route(sourceId: str = 'cha_uAPqOGzFSqbrUuCebnq8i', session: AsyncSession = Depends(get_session)):
    messages = await get_messages(session, sourceId)
    return messages


from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat

# Initialize GigaChat instance
giga = GigaChat(credentials='ODA1Y2Q0NWUtNmNhYi00OWRkLWJhNTYtN2JmNDk3YWJjOWVmOmM3ZWRlZDEzLTk4NTgtNDI4YS1iMzdlLWViODM3NGQwODJlNg==>', model='GigaChat', verify_ssl_certs=False)

# Define request body model
class MessageRequest(BaseModel):
    content: str

@router.post("/chat_with_gigachat", response_model=MessageRequest)
async def chat_with_gigachat(message: MessageRequest):
    return chat_with_gigachat_promt(message.content)

    

async def chat_with_gigachat_promt(message: str):
    try:
        # Prepare message for GigaChat
        human_message = HumanMessage(content=message)
        response = giga([human_message])

        # Return the assistant's response
        return response.content

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/generate_ai_review", response_model=MessageRequest)
async def generate_ai_review( # generates comment for shape by its id and saves it to the database
    shape_id: int = Path(..., title="Уникальный идентификатор фигуры"),
    db: AsyncSession = Depends(get_session),
):
    shape = await ShapeService.get(db=db, shape_id=shape_id)
    if not shape:
        raise HTTPException(status_code=404, detail="Фигура не найдена")
    
    # Generate AI review for the shape
    ai_review = generate_ai_review_for_shape(shape.to_dict())
    
    # Save the AI review to the database
    await ShapeService.add_ai_gen_comment(db=db, shape_id=shape_id, ai_gen_comment=ai_review)
    
    return JSONResponse(content={"content": ai_review})

async def generate_ai_review_for_shape(shape: dict) -> str:
    
    base_promt = f"Напишите заключение по фигуре с ID {shape.id}"

    ai_review = await chat_with_gigachat_promt(base_promt)
    
    return ai_review

# Additional routes and functionalities can be added as needed

