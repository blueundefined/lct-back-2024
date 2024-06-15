from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import select
from starlette import status
from pydantic import BaseModel
import aiohttp
import os
from typing import List
from app.database import get_session

from app.database.tables import ChatMessage
from sqlalchemy.ext.asyncio import AsyncSession 
from app.config import config

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List

import aiohttp
import os

from app.database import get_session
from app.database.tables import ChatMessage
from app.config import config

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

async def save_chat_message(source_id: str, role: str, content: str, session: AsyncSession) -> ChatMessage:
    db_message = ChatMessage(source_id=source_id, role=role, content=content)
    session.add(db_message)
    await session.commit()
    await session.refresh(db_message)
    return db_message

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
                for msg in request.messages:
                    await save_chat_message(request.sourceId, msg.role, msg.content, session)
                await save_chat_message(request.sourceId, "assistant", result['content'], session)
                return JSONResponse(content={"content": result['content']})
            else:
                error = await response.text()
                raise HTTPException(status_code=response.status, detail=error)

@router.get("/ai/chat/get_chat_messages", response_model=List[ChatMessage],
            response_description="Успешное получение списка сообщений",
            status_code=status.HTTP_200_OK,
            description="Получить список сообщений по sourceId",
            summary="Получение списка сообщений")
async def get_messages_by_source_id(source_id: str = 'cha_uAPqOGzFSqbrUuCebnq8i', session: AsyncSession = Depends(get_session)) -> List[ChatMessage]:
    result = await session.execute(select(ChatMessage).filter(ChatMessage.source_id == source_id).order_by(ChatMessage.id))
    messages = result.scalars().all()
    return messages
