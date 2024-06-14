from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse
from starlette import status
from pydantic import BaseModel
import aiohttp
import os
from typing import List

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
    sourceId: str
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    content: str

class UploadResponse(BaseModel):
    sourceId: str

class DeleteRequest(BaseModel):
    sourceId: str

class DeleteResponse(BaseModel):
    detail: str

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
async def chat_with_pdf(request: ChatRequest):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            CHAT_URL,
            headers={'x-api-key': API_KEY},
            json={
                "sourceId": request.sourceId,
                "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages]
            }
        ) as response:
            if response.status == 200:
                result = await response.json()
                return JSONResponse(content={"content": result['content']})
            else:
                error = await response.text()
                raise HTTPException(status_code=response.status, detail=error)